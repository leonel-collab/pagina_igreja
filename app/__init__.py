# -*- coding: utf-8 -*-
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'
mail = Mail()


def create_app():
    app = Flask(__name__)

    # Configuracao da SECRET_KEY
    app.config['SECRET_KEY'] = os.environ.get(
        'SECRET_KEY',
        'fallback-dev-key-mude-em-producao'
    )

    # Configuracao do banco de dados
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        base_dir = os.path.abspath(os.path.dirname(__file__))
        database_url = 'sqlite:///' + os.path.join(
            os.path.dirname(base_dir), 'controle_membros.db'
        )
    elif database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    elif database_url.startswith('mysql://'):
        database_url = database_url.replace('mysql://', 'mysql+pymysql://', 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configuracao de upload
    app.config['UPLOAD_FOLDER'] = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'uploads'
    )
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB

    # Configuracao de email
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', '')

    # Inicializar extensoes
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Importar modelos (para criar tabelas)
    from app.models import Membro, Usuario

    with app.app_context():
        db.create_all()

        from app.models import Usuario
        admin = Usuario.query.filter_by(username='admin').first()
        if not admin:
            admin = Usuario(
                username='admin',
                email='admin@igreja.com'
            )
            admin.set_senha('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Usuario admin criado (admin / admin123)')

    # Registrar Blueprints
    from app.routes.auth import auth_bp
    from app.routes.membros import membros_bp
    from app.routes.api import api_bp
    from app.routes.email_massa import email_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(membros_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(email_bp)

    # Tratamento de erro 404
    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template('404.html'), 404

    # Tratamento de erro 500
    @app.errorhandler(500)
    def server_error(e):
        from flask import render_template
        return render_template('500.html'), 500

    # Injetar variaveis globais nos templates
    @app.context_processor
    def inject_globals():
        from datetime import datetime
        return {
            'current_year': datetime.now().year,
            'app_name': 'Igreja+'
        }

    return app
