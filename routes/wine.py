from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import Wine
from extensions import db
from utils import save_and_process_image, delete_image_files
from datetime import datetime, UTC

bp = Blueprint('wine', __name__, url_prefix='/wines')


@bp.route('/')
def list_wines():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    wines = Wine.query.order_by(Wine.date_added.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return render_template('wines/list.html', wines=wines)


@bp.route('/add', methods=['GET', 'POST'])
def add_wine():
    if request.method == 'POST':
        wine_name = request.form.get('wine_name', '').strip()
        vineyard_name = request.form.get('vineyard_name', '').strip()
        vintage_year = request.form.get('vintage_year', type=int)
        rating = request.form.get('rating', type=int)
        notes = request.form.get('notes', '').strip()
        
        if 'image' not in request.files:
            flash('No image file provided', 'error')
            return redirect(request.url)
        
        file = request.files['image']
        if file.filename == '':
            flash('No image selected', 'error')
            return redirect(request.url)
        
        image_path, thumbnail_path = save_and_process_image(file)
        
        if not image_path:
            flash('Error processing image. Please try again.', 'error')
            return redirect(request.url)
        
        wine = Wine(
            wine_name=wine_name,
            vineyard_name=vineyard_name,
            vintage_year=vintage_year,
            rating=rating,
            notes=notes,
            image_path=image_path,
            thumbnail_path=thumbnail_path
        )
        
        errors = wine.validate()
        if errors:
            delete_image_files(image_path, thumbnail_path)
            for error in errors:
                flash(error, 'error')
            return redirect(request.url)
        
        try:
            db.session.add(wine)
            db.session.commit()
            flash('Wine added successfully!', 'success')
            return redirect(url_for('wine.view_wine', wine_id=wine.id))
        except Exception as e:
            db.session.rollback()
            delete_image_files(image_path, thumbnail_path)
            flash(f'Error saving wine: {str(e)}', 'error')
            return redirect(request.url)
    
    return render_template('wines/add.html', current_year=datetime.now().year)


@bp.route('/<int:wine_id>')
def view_wine(wine_id):
    wine = Wine.query.get_or_404(wine_id)
    return render_template('wines/view.html', wine=wine)


@bp.route('/<int:wine_id>/edit', methods=['GET', 'POST'])
def edit_wine(wine_id):
    wine = Wine.query.get_or_404(wine_id)
    
    if request.method == 'POST':
        wine.wine_name = request.form.get('wine_name', '').strip()
        wine.vineyard_name = request.form.get('vineyard_name', '').strip()
        wine.vintage_year = request.form.get('vintage_year', type=int)
        wine.rating = request.form.get('rating', type=int)
        wine.notes = request.form.get('notes', '').strip()
        
        if 'image' in request.files and request.files['image'].filename != '':
            file = request.files['image']
            new_image_path, new_thumbnail_path = save_and_process_image(file)
            
            if new_image_path:
                old_image_path = wine.image_path
                old_thumbnail_path = wine.thumbnail_path
                
                wine.image_path = new_image_path
                wine.thumbnail_path = new_thumbnail_path
                
                delete_image_files(old_image_path, old_thumbnail_path)
        
        errors = wine.validate()
        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(request.url)
        
        try:
            wine.date_modified = datetime.now(UTC)
            db.session.commit()
            flash('Wine updated successfully!', 'success')
            return redirect(url_for('wine.view_wine', wine_id=wine.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating wine: {str(e)}', 'error')
            return redirect(request.url)
    
    return render_template('wines/edit.html', wine=wine, current_year=datetime.now().year)


@bp.route('/<int:wine_id>/delete', methods=['POST'])
def delete_wine(wine_id):
    wine = Wine.query.get_or_404(wine_id)
    
    try:
        delete_image_files(wine.image_path, wine.thumbnail_path)
        
        db.session.delete(wine)
        db.session.commit()
        
        flash('Wine deleted successfully!', 'success')
        return redirect(url_for('main.index'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting wine: {str(e)}', 'error')
        return redirect(url_for('wine.view_wine', wine_id=wine_id))