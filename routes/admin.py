from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from models import User, Student, Company, JobPost, Application, Message, Notification, Skill, Conversation
from sqlalchemy import func, desc
import json

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to check if the user is an admin"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/admin/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with overview statistics"""
    stats = {
        'total_users': User.query.count(),
        'total_students': Student.query.count(),
        'total_companies': Company.query.count(),
        'total_jobs': JobPost.query.count(),
        'total_applications': Application.query.count(),
        'total_messages': Message.query.count(),
        'recent_users': User.query.order_by(desc(User.created_at)).limit(5).all(),
        'recent_jobs': JobPost.query.order_by(desc(JobPost.created_at)).limit(5).all(),
        'application_status_counts': db.session.query(
            Application.status, func.count(Application.id)
        ).group_by(Application.status).all()
    }
    
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/admin/users')
@login_required
@admin_required
def users():
    """List all users with search and filter capabilities"""
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    
    query = User.query
    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) | 
            (User.email.ilike(f'%{search}%'))
        )
    
    pagination = query.order_by(User.username).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('admin/users.html', 
                          pagination=pagination, 
                          search=search)

@admin_bp.route('/admin/companies')
@login_required
@admin_required
def companies():
    """List all companies"""
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    
    query = Company.query
    if search:
        query = query.filter(Company.name.ilike(f'%{search}%'))
    
    pagination = query.order_by(Company.name).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('admin/companies.html', 
                          pagination=pagination, 
                          search=search)

@admin_bp.route('/admin/students')
@login_required
@admin_required
def students():
    """List all students"""
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    
    query = Student.query
    if search:
        query = query.filter(
            (Student.first_name.ilike(f'%{search}%')) | 
            (Student.last_name.ilike(f'%{search}%'))
        )
    
    pagination = query.paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('admin/students.html', 
                          pagination=pagination, 
                          search=search)

@admin_bp.route('/admin/jobs')
@login_required
@admin_required
def jobs():
    """List all job posts"""
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    
    query = JobPost.query
    if search:
        query = query.filter(JobPost.title.ilike(f'%{search}%'))
    
    pagination = query.order_by(desc(JobPost.created_at)).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('admin/jobs.html', 
                          pagination=pagination, 
                          search=search)

@admin_bp.route('/admin/applications')
@login_required
@admin_required
def applications():
    """List all applications"""
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    
    query = Application.query
    if status:
        query = query.filter(Application.status == status)
    
    pagination = query.order_by(desc(Application.created_at)).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('admin/applications.html', 
                          pagination=pagination, 
                          status=status)

@admin_bp.route('/admin/user/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """View detailed information about a user"""
    user = User.query.get_or_404(user_id)
    return render_template('admin/user_detail.html', user=user)

@admin_bp.route('/admin/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    """Toggle admin status for a user"""
    user = User.query.get_or_404(user_id)
    
    # Prevent removing admin status from yourself
    if user.id == current_user.id:
        flash('You cannot remove your own admin status.', 'danger')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    flash(f'Admin status for {user.username} has been {"granted" if user.is_admin else "revoked"}.', 'success')
    return redirect(url_for('admin.user_detail', user_id=user_id))

@admin_bp.route('/admin/toggle_active/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_active(user_id):
    """Toggle active status for a user"""
    user = User.query.get_or_404(user_id)
    
    # Prevent deactivating yourself
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'danger')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    flash(f'Account for {user.username} has been {"activated" if user.is_active else "deactivated"}.', 'success')
    return redirect(url_for('admin.user_detail', user_id=user_id))

@admin_bp.route('/admin/database')
@login_required
@admin_required
def database():
    """Direct database access and visualization"""
    tables = {
        'users': User.query.count(),
        'students': Student.query.count(),
        'companies': Company.query.count(),
        'job_posts': JobPost.query.count(),
        'applications': Application.query.count(),
        'messages': Message.query.count(),
        'notifications': Notification.query.count(),
        'skills': Skill.query.count(),
        'conversations': Conversation.query.count()
    }
    
    return render_template('admin/database.html', tables=tables)

@admin_bp.route('/admin/table/<table_name>')
@login_required
@admin_required
def table_view(table_name):
    """View contents of a specific database table"""
    page = request.args.get('page', 1, type=int)
    
    # Map table names to model classes
    table_models = {
        'users': User,
        'students': Student,
        'companies': Company,
        'job_posts': JobPost,
        'applications': Application,
        'messages': Message, 
        'notifications': Notification,
        'skills': Skill,
        'conversations': Conversation
    }
    
    if table_name not in table_models:
        abort(404)
    
    model = table_models[table_name]
    pagination = model.query.paginate(page=page, per_page=20, error_out=False)
    
    # Get column names for the table
    columns = [column.name for column in model.__table__.columns]
    
    return render_template('admin/table_view.html', 
                          table_name=table_name,
                          pagination=pagination,
                          columns=columns)

@admin_bp.route('/admin/stats')
@login_required
@admin_required
def stats():
    """Statistical data for charts and graphs"""
    # Jobs by job type
    jobs_by_type = db.session.query(
        JobPost.job_type, func.count(JobPost.id)
    ).group_by(JobPost.job_type).all()
    
    # Applications by status
    applications_by_status = db.session.query(
        Application.status, func.count(Application.id)
    ).group_by(Application.status).all()
    
    # Users over time (last 30 days)
    users_over_time = db.session.query(
        func.date(User.created_at), func.count(User.id)
    ).group_by(func.date(User.created_at)).all()
    
    # Companies by industry
    companies_by_industry = db.session.query(
        Company.industry, func.count(Company.id)
    ).group_by(Company.industry).all()
    
    # Prepare data for charts
    chart_data = {
        'jobs_by_type': {
            'labels': [t[0] or 'unknown' for t in jobs_by_type],
            'data': [t[1] for t in jobs_by_type]
        },
        'applications_by_status': {
            'labels': [s[0] for s in applications_by_status],
            'data': [s[1] for s in applications_by_status]
        },
        'users_over_time': {
            'labels': [str(d[0]) for d in users_over_time],
            'data': [d[1] for d in users_over_time]
        },
        'companies_by_industry': {
            'labels': [i[0] or 'unknown' for i in companies_by_industry],
            'data': [i[1] for i in companies_by_industry]
        }
    }
    
    return render_template('admin/stats.html', chart_data=json.dumps(chart_data))