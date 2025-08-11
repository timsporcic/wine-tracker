from flask import Blueprint, render_template, jsonify
from models import Wine
from extensions import db
from sqlalchemy import func

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    total_wines = Wine.query.count()
    avg_rating = db.session.query(func.avg(Wine.rating)).scalar() or 0
    recent_wines = Wine.query.order_by(Wine.date_added.desc()).limit(5).all()
    
    return render_template('index.html',
                         total_wines=total_wines,
                         avg_rating=round(avg_rating, 1),
                         recent_wines=recent_wines)


@bp.route('/search')
def search_page():
    return render_template('search.html')


@bp.route('/gallery')
def gallery():
    wines = Wine.query.order_by(Wine.date_added.desc()).all()
    return render_template('gallery.html', wines=wines)


@bp.route('/about')
def about():
    return render_template('about.html')