from flask import Blueprint, request, jsonify
from models import Wine
from extensions import db
from sqlalchemy import or_, and_

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/search')
def search():
    query = request.args.get('q', '').strip()
    rating = request.args.get('rating', type=int)
    year_from = request.args.get('year_from', type=int)
    year_to = request.args.get('year_to', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    wines_query = Wine.query
    
    if query:
        search_filter = or_(
            Wine.wine_name.ilike(f'%{query}%'),
            Wine.vineyard_name.ilike(f'%{query}%')
        )
        wines_query = wines_query.filter(search_filter)
    
    if rating:
        wines_query = wines_query.filter(Wine.rating == rating)
    
    if year_from:
        wines_query = wines_query.filter(Wine.vintage_year >= year_from)
    
    if year_to:
        wines_query = wines_query.filter(Wine.vintage_year <= year_to)
    
    wines_query = wines_query.order_by(Wine.date_added.desc())
    
    pagination = wines_query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'wines': [wine.to_dict() for wine in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@bp.route('/wines/<int:wine_id>')
def get_wine(wine_id):
    wine = Wine.query.get_or_404(wine_id)
    return jsonify(wine.to_dict())


@bp.route('/wines', methods=['GET'])
def get_wines():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort_by = request.args.get('sort_by', 'date_added')
    order = request.args.get('order', 'desc')
    
    valid_sort_fields = ['date_added', 'wine_name', 'vineyard_name', 'vintage_year', 'rating']
    if sort_by not in valid_sort_fields:
        sort_by = 'date_added'
    
    sort_field = getattr(Wine, sort_by)
    if order == 'asc':
        sort_field = sort_field.asc()
    else:
        sort_field = sort_field.desc()
    
    pagination = Wine.query.order_by(sort_field).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'wines': [wine.to_dict() for wine in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@bp.route('/wines/suggestions')
def get_suggestions():
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify({'suggestions': []})
    
    wine_suggestions = db.session.query(Wine.wine_name).filter(
        Wine.wine_name.ilike(f'%{query}%')
    ).distinct().limit(5).all()
    
    vineyard_suggestions = db.session.query(Wine.vineyard_name).filter(
        Wine.vineyard_name.ilike(f'%{query}%')
    ).distinct().limit(5).all()
    
    suggestions = []
    for wine in wine_suggestions:
        suggestions.append({'type': 'wine', 'value': wine[0]})
    
    for vineyard in vineyard_suggestions:
        suggestions.append({'type': 'vineyard', 'value': vineyard[0]})
    
    return jsonify({'suggestions': suggestions[:10]})


@bp.route('/stats')
def get_stats():
    total_wines = Wine.query.count()
    
    if total_wines == 0:
        return jsonify({
            'total_wines': 0,
            'average_rating': 0,
            'rating_distribution': {},
            'wines_by_year': {},
            'top_vineyards': []
        })
    
    avg_rating = db.session.query(db.func.avg(Wine.rating)).scalar() or 0
    
    rating_dist = db.session.query(
        Wine.rating,
        db.func.count(Wine.id)
    ).group_by(Wine.rating).all()
    
    wines_by_year = db.session.query(
        Wine.vintage_year,
        db.func.count(Wine.id)
    ).group_by(Wine.vintage_year).order_by(Wine.vintage_year.desc()).limit(10).all()
    
    top_vineyards = db.session.query(
        Wine.vineyard_name,
        db.func.count(Wine.id).label('count'),
        db.func.avg(Wine.rating).label('avg_rating')
    ).group_by(Wine.vineyard_name).order_by(db.text('count DESC')).limit(5).all()
    
    return jsonify({
        'total_wines': total_wines,
        'average_rating': round(avg_rating, 2),
        'rating_distribution': {str(r): c for r, c in rating_dist},
        'wines_by_year': {str(y): c for y, c in wines_by_year},
        'top_vineyards': [
            {
                'name': v[0],
                'count': v[1],
                'avg_rating': round(v[2], 2)
            } for v in top_vineyards
        ]
    })