
import os.path
from flask import Blueprint
from flask import render_template, request, redirect, session
from werkzeug.utils import secure_filename

from get_db import get_db
from login_required import login_required

products_bp = Blueprint('products', __name__)

@products_bp.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        currency = request.form['currency']
        user = session['username']

        cursor.execute("SELECT id FROM users WHERE username=?", (user,))
        user_id = cursor.fetchone()[0]

        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            image_path = f"uploads/products/{user}/{filename}"
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            image.save(image_path)
        else:
            filename = ""

        cursor.execute("""
            INSERT INTO products (user_id, title, description, price, image_filename, currency)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, title, description, price, filename, currency))
        conn.commit()
        conn.close()
        return redirect(f"/profile/{user}")

    return render_template('profile/add_product.html')

@products_bp.route('/delete_product', methods=['POST'])
@login_required
def delete_product():
    product_id = request.form.get('product_id')
    if not product_id:
        return "Missing product ID", 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT image_filename FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    if row and row[0]:
        try:
            os.remove(row[0])
        except:
            pass

    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

    return redirect(f"/profile/{session['username']}")


