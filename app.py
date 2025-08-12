import os
from flask import Flask, send_from_directory
from config import config
from extensions import db, migrate, csrf


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Import models after db initialization to avoid circular imports
    from models import Wine
    
    from routes import main, wine, api
    app.register_blueprint(main.bp)
    app.register_blueprint(wine.bp)
    app.register_blueprint(api.bp)
    
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    @app.route('/uploads/thumbnails/<path:filename>')
    def uploaded_thumbnail(filename):
        return send_from_directory(app.config['THUMBNAIL_FOLDER'], filename)
    
    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    
    # Get server configuration from environment
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    app.run(debug=debug, host=host, port=port)