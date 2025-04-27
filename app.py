import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager


# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass


# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configure file uploads
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload size
os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "cvs"), exist_ok=True)
os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "profile_pics"), exist_ok=True)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"

# Import models and create tables
with app.app_context():
    import models
    db.create_all()

# Import and register blueprints
from routes.auth import auth_bp
from routes.student import student_bp
from routes.company import company_bp
from routes.jobs import jobs_bp
from routes.messages import messages_bp

app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(company_bp)
app.register_blueprint(jobs_bp)
app.register_blueprint(messages_bp)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Root route
@app.route('/')
def home():
    from flask import render_template
    return render_template('home.html')

@app.errorhandler(404)
def not_found_error(error):
    from flask import render_template
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    from flask import render_template
    return render_template('500.html'), 500

@app.context_processor
def inject_user_type():
    from flask_login import current_user
    from models import Student, Company
    
    if current_user.is_authenticated:
        if Student.query.filter_by(user_id=current_user.id).first():
            return {"user_type": "student"}
        elif Company.query.filter_by(user_id=current_user.id).first():
            return {"user_type": "company"}
    return {"user_type": None}
