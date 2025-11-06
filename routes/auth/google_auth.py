
import os
from flask import Blueprint, redirect, url_for, session, request
from authlib.integrations.flask_client import OAuth
from get_db import get_db
from .reset_password import clear_reset_stage

google_auth_bp = Blueprint('google_auth', __name__)

oauth = OAuth()

def init_google_oauth(app):
    oauth.init_app(app)
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # Only register if credentials are provided
    if client_id and client_secret:
        google = oauth.register(
            name='google',
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={
                'scope': 'openid email profile'
            }
        )
        return google
    return None

@google_auth_bp.route('/login/google')
def google_login():
    if not oauth.google:
        return redirect(url_for('auth.login') + '?error=google_auth_failed')
    google = oauth.google
    redirect_uri = url_for('google_auth.google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@google_auth_bp.route('/login/google/callback')
def google_callback():
    if not oauth.google:
        return redirect(url_for('auth.login') + '?error=google_auth_failed')
    google = oauth.google
    try:
        token = google.authorize_access_token()
        if not token:
            return redirect(url_for('auth.login') + '?error=google_auth_failed')
        
        # Get user info - Authlib returns dict directly
        try:
            user_info = google.userinfo()
        except Exception as e:
            import logging
            logging.error(f"Error calling userinfo: {str(e)}", exc_info=True)
            # Try alternative method - get from token
            if 'id_token' in token:
                try:
                    from authlib.jose import jwt
                    import json
                    id_token = token['id_token']
                    # Decode without verification (just for fallback)
                    parts = id_token.split('.')
                    if len(parts) >= 2:
                        import base64
                        # Add padding if needed
                        payload = parts[1]
                        payload += '=' * (4 - len(payload) % 4)
                        decoded = base64.urlsafe_b64decode(payload)
                        user_info = json.loads(decoded)
                    else:
                        return redirect(url_for('auth.login') + '?error=google_auth_failed')
                except Exception as e2:
                    logging.error(f"Error parsing ID token: {str(e2)}")
                    return redirect(url_for('auth.login') + '?error=google_auth_failed')
            else:
                return redirect(url_for('auth.login') + '?error=google_auth_failed')
        
        if not user_info or not isinstance(user_info, dict):
            return redirect(url_for('auth.login') + '?error=google_auth_failed')
        
        google_id = user_info.get('sub')
        email = user_info.get('email', '').lower().strip()
        name = user_info.get('name', '').strip()
        picture = user_info.get('picture', '')
        
        if not google_id or not email:
            return redirect(url_for('auth.login') + '?error=google_auth_failed')
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Check if user exists by google_id
            cursor.execute("SELECT username FROM users WHERE google_id = ?", (google_id,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                # User exists, log them in
                username = existing_user[0]
                session['username'] = username
                clear_reset_stage()
                return redirect('/home')
            else:
                # Check if email already exists
                cursor.execute("SELECT username FROM users WHERE email = ?", (email,))
                email_user = cursor.fetchone()
                
                if email_user:
                    # Email exists but no Google ID, link the account
                    username = email_user[0]
                    cursor.execute("UPDATE users SET google_id = ? WHERE email = ?", (google_id, email))
                    conn.commit()
                    session['username'] = username
                    clear_reset_stage()
                    return redirect('/home')
                else:
                    # New user, create account
                    # Generate username from email
                    base_username = email.split('@')[0].replace('.', '_').replace('+', '_')
                    username = base_username
                    counter = 1
                    
                    # Ensure username is unique
                    while True:
                        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                        if not cursor.fetchone():
                            break
                        username = f"{base_username}_{counter}"
                        counter += 1
                    
                    # Create user with Google ID
                    cursor.execute(
                        "INSERT INTO users (username, email, name, avatar, google_id, is_verified) VALUES (?, ?, ?, ?, ?, ?)",
                        (username, email, name or username, picture, google_id, 0)
                    )
                    conn.commit()
                    
                    session['username'] = username
                    clear_reset_stage()
                    return redirect('/home')
                    
    except Exception as e:
        import logging
        logging.error(f"Google OAuth error: {str(e)}", exc_info=True)
        return redirect(url_for('auth.login') + '?error=google_auth_error')

