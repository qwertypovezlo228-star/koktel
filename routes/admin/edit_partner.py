
from os import remove
from contextlib import suppress
from urllib.parse import urlparse

from flask import Blueprint, flash
from flask import render_template, request, redirect, url_for
from flask_babel import gettext as _

from get_db import get_db
from utils.images import save_image
from login_required import admin_required

edit_partner_bp = Blueprint('edit_partner', __name__)

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        print(result)
        return bool(result.netloc or result.path)
    except:
        return False

def normalize_url(link: str) -> str:
    parsed = urlparse(link)
    if not parsed.scheme:
        return 'https://' + link
    return link


@edit_partner_bp.route('/add_partner', methods=['GET', 'POST'])
@admin_required
def add_partner_from_admin_panel():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        link = request.form.get('link', '').strip()
        link_text = request.form.get('link_text', '').strip()
        image_file = request.files.get('image')

        if link:
            if not is_valid_url(link):
                flash(_("Please provide the correct link"), "danger")
                return render_template('admin/add_partner.html', name=name, link=link)

            link = normalize_url(link)

        if not image_file or not image_file.filename:
            flash(_("Please upload an image"), "danger")
            return render_template('admin/add_partner.html', name=name, link=link)

        try:
            cover_path = save_image(
                image_file,
                folder="uploads/partners/covers",
                prefix="partner_cover"
            )
        except ValueError:
            flash(_("Please upload an image"), "danger")
            return render_template('admin/add_partner.html', name=name, link=link)

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO partners (name, cover, link, link_text) VALUES (?, ?, ?, ?);",
                (name if name else None, cover_path, link if link else None, link_text if link_text else None)
            )
            conn.commit()
        return redirect(url_for('admin.partners'))

    return render_template('admin/add_partner.html')


@edit_partner_bp.route('/edit_partner/<int:partner_id>', methods=['GET', 'POST'])
@admin_required
def edit_partner(partner_id):
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, cover, link, link_text FROM partners WHERE id = ?", (partner_id,))
        partner = cursor.fetchone()

        if not partner:
            flash(_("Partner not found"), "danger")
            return redirect(url_for('admin.partners'))

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            link = request.form.get('link', '').strip()
            link_text = request.form.get('link_text', '').strip()
            image_file = request.files.get('image')

            if link:
                if not is_valid_url(link):
                    flash(_("Please provide the correct link"), "danger")
                    return render_template('admin/add_partner.html', name=name, link=link)

                link = normalize_url(link)

            cover_path = partner[2]

            if image_file and image_file.filename:
                try:
                    cover_path = save_image(
                        image_file,
                        folder="uploads/partners/covers",
                        prefix="partner_cover"
                    )
                except ValueError:
                    flash(_("Please upload a valid image"), "danger")
                    return render_template('admin/edit_partner.html', partner=partner)

            cursor.execute(
                "UPDATE partners SET name = ?, link = ?, link_text = ?, cover = ? WHERE id = ?",
                (name if name else None, link if link else None, link_text if link_text else None, cover_path, partner_id)
            )
            conn.commit()

            return redirect(url_for('admin.partners'))

    return render_template('admin/edit_partner.html', partner=partner)


@edit_partner_bp.route('/delete_partner/<int:partner_id>')
@admin_required
def delete_partner(partner_id):
    cover_path = None

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT cover FROM partners WHERE id=?", (partner_id,))
        result = cursor.fetchone()
        if result:
            cover_path = result[0]

        cursor.execute("DELETE FROM partners WHERE id=?", (partner_id,))
        conn.commit()

    if cover_path:
        with suppress(FileNotFoundError):
            remove(cover_path)

    return redirect(url_for('admin.partners'))

