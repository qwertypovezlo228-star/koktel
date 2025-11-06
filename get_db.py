
import os
import sqlite3
from contextlib import suppress

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

DB_PATH = os.path.join(DB_DIR, 'database.db')

def get_db():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError("❌ База database.db не знайдена в папці data/")
    return sqlite3.connect(DB_PATH)

def create_db_if_not_exists():
    with suppress(FileExistsError):
        os.mkdir(DB_DIR)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    command = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        name TEXT,
        avatar TEXT,
        is_verified INTEGER DEFAULT 0,
        description TEXT,
        category INTEGER,
        city TEXT,
        last_seen TEXT,
        visible INTEGER DEFAULT 1,
        is_admin INTEGER DEFAULT 0,
        email TEXT UNIQUE,
        google_id TEXT UNIQUE
    );

    CREATE TABLE IF NOT EXISTS support_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contact TEXT NOT NULL,
        message TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS partners (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        cover TEXT,
        link TEXT,
        link_text TEXT
    );

    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        description TEXT,
        price REAL,
        image_filename TEXT,
        currency TEXT DEFAULT 'UAH',
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS private_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        msg TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        message TEXT,
        room TEXT,
        media_urls TEXT,
        timestamp TEXT,
        content TEXT,
        reply_to_id INTEGER,
        is_read INTEGER DEFAULT 0,
        status TEXT,
        reply_to TEXT,
        reply TEXT
    );

    CREATE TABLE IF NOT EXISTS shared_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        text TEXT,
        media_urls TEXT,
        reply_to INTEGER,
        sender TEXT,
        timestamp TEXT
    );
    CREATE TABLE IF NOT EXISTS password_reset_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        code TEXT NOT NULL,
        expires_at DATETIME NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS blog_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS blog_post_images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        image_path TEXT NOT NULL,
        FOREIGN KEY (post_id) REFERENCES blog_posts(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS blog_subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subscriber_id INTEGER NOT NULL,
        model_id INTEGER NOT NULL,
        subscribed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (subscriber_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (model_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE (subscriber_id, model_id)
    );
    """

    cursor.executescript(command)
    
    # Migrate existing database: add google_id column if it doesn't exist
    try:
        cursor.execute("SELECT google_id FROM users LIMIT 1")
    except sqlite3.OperationalError:
        # Column doesn't exist, add it
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN google_id TEXT")
            # Create unique index for google_id
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id) WHERE google_id IS NOT NULL")
            conn.commit()
        except sqlite3.OperationalError as e:
            # If column already exists or other error, continue
            pass
    
    cursor.execute("INSERT OR IGNORE INTO users (username, password, name) VALUES ('admin', ?, 'admin');", (os.environ["ADMIN_DEFAULT_PASSWORD"],))
    conn.commit()
    conn.close()

