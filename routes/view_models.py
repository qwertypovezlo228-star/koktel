
from flask import Blueprint
from flask import render_template, request, redirect, url_for

from get_db import get_db
from login_required import login_required

view_models_bp = Blueprint('view_models', __name__)

@view_models_bp.route('/api/virtual_models_cards')
@login_required
def virtual_models_cards():
    is_verified = request.args.get('verified') == '1'
    page = request.args.get('page', 1, type=int)
    per_page = 12
    offset = (page - 1) * per_page
    
    query = """
        SELECT u.id, u.name, u.avatar, TRIM(u.city), u.is_verified 
        FROM users u
        LEFT JOIN (
            SELECT user_id, MAX(created_at) as latest_post_date
            FROM blog_posts
            GROUP BY user_id
        ) bp ON u.id = bp.user_id
        WHERE u.category=1 AND u.visible=1
    """
    count_query = "SELECT COUNT(*) FROM users WHERE category=1 AND visible=1"
    params = []
    
    if is_verified:
        query += " AND u.is_verified = 1"
        count_query += " AND is_verified = 1"
    
    query += " ORDER BY CASE WHEN bp.latest_post_date IS NOT NULL THEN 0 ELSE 1 END, bp.latest_post_date DESC, u.name ASC"
    query += " LIMIT ? OFFSET ?"
    params.extend([per_page, offset])
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(count_query)
        total_count = cursor.fetchone()[0]
        cursor.execute(query, params)
        models = cursor.fetchall()
    
    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
    
    return render_template('models/models_cards.html', models=models, page=page, total_pages=total_pages, has_next=page < total_pages, has_prev=page > 1)

@view_models_bp.route('/api/models_cities_button')
@login_required
def individual_models_cities_button():

    selected_city = request.args.get('city')
    verified_only = request.args.get('verified') == '1'

    with get_db() as conn:
        cursor = conn.cursor()

        city_query = """
            SELECT TRIM(city), COUNT(*) 
            FROM users 
            WHERE category=2 
              AND visible=1 
              AND city IS NOT NULL AND city != ''
        """
        if verified_only:
            city_query += " AND is_verified = 1"

        city_query += " GROUP BY TRIM(city)"
        cursor.execute(city_query)
        cities_data = cursor.fetchall()

    template = 'models/cities_button.html'
    if request.args.get('dropdown') == '1':
        template = 'models/cities_select.html'

    return render_template(
        template,
        cities=cities_data,
        selected_city=selected_city
    )

@view_models_bp.route('/api/individuals_cards')
@login_required
def individual_models_cards():
    selected_city = request.args.get('city')
    verified_only = request.args.get('verified') == '1'
    page = request.args.get('page', 1, type=int)
    per_page = 12
    offset = (page - 1) * per_page

    with get_db() as conn:
        cursor = conn.cursor()

        base_query = """
            SELECT u.id, u.name, u.avatar, TRIM(u.city), u.is_verified 
            FROM users u
            LEFT JOIN (
                SELECT user_id, MAX(created_at) as latest_post_date
                FROM blog_posts
                GROUP BY user_id
            ) bp ON u.id = bp.user_id
            WHERE u.category=2 
              AND u.visible=1
        """
        count_query = """
            SELECT COUNT(*) 
            FROM users 
            WHERE category=2 
              AND visible=1
        """
        params = []
        count_params = []

        if selected_city:
            base_query += " AND LOWER(TRIM(u.city)) = LOWER(?)"
            count_query += " AND LOWER(TRIM(city)) = LOWER(?)"
            params.append(selected_city)
            count_params.append(selected_city)

        if verified_only:
            base_query += " AND u.is_verified = 1"
            count_query += " AND is_verified = 1"

        # Get total count
        cursor.execute(count_query, count_params)
        total_count = cursor.fetchone()[0]

        # Check redirects only if no results on first page
        if page == 1:
            if verified_only and selected_city and total_count == 0:
                return redirect(url_for('view_models.individual_models_cards', verified=1))
            elif selected_city and total_count == 0:
                return redirect(url_for('view_models.individual_models_cards'))

        # Add sorting by blog post date
        base_query += " ORDER BY CASE WHEN bp.latest_post_date IS NOT NULL THEN 0 ELSE 1 END, bp.latest_post_date DESC, u.name ASC"
        
        # Add pagination
        base_query += " LIMIT ? OFFSET ?"
        params.extend([per_page, offset])

        cursor.execute(base_query, params)
        models = cursor.fetchall()

    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
    
    return render_template('models/models_cards.html', models=models, show_city=True, page=page, total_pages=total_pages, has_next=page < total_pages, has_prev=page > 1)

@view_models_bp.route('/category/1')
@login_required
def virtual_models():
    return render_template('models/virtual_models.html')

@view_models_bp.route('/category/2')
@login_required
def real_models():
    return render_template('models/category_real.html')

