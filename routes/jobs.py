from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import or_

# Import db inside the routes to avoid circular import
def get_db():
    from app import db
    return db

from models import JobPost, Company, Student, Application, User
from forms import ApplicationForm, SearchForm
from utils import create_notification

# Define the blueprint
jobs_bp = Blueprint('jobs', __name__, url_prefix='/jobs')

@jobs_bp.route('/')
def listing():
    db = get_db()
    form = SearchForm()

    query = request.args.get('query', '')
    job_type = request.args.get('job_type', '')
    location = request.args.get('location', '')

    job_query = JobPost.query.filter_by(is_active=True)

    if query:
        job_query = job_query.filter(or_(
            JobPost.title.ilike(f'%{query}%'),
            JobPost.description.ilike(f'%{query}%'),
            JobPost.requirements.ilike(f'%{query}%')
        ))

    if job_type:
        job_query = job_query.filter_by(job_type=job_type)

    if location:
        job_query = job_query.filter(JobPost.location.ilike(f'%{location}%'))

    jobs = job_query.order_by(JobPost.created_at.desc()).all()
    companies = {job.company_id: Company.query.get(job.company_id) for job in jobs}

    applied_jobs = set()
    if current_user.is_authenticated:
        student = Student.query.filter_by(user_id=current_user.id).first()
        if student:
            applications = Application.query.filter_by(student_id=student.id).all()
            applied_jobs = {app.job_post_id for app in applications}

    return render_template('jobs/listing.html', jobs=jobs, companies=companies, 
                           applied_jobs=applied_jobs, form=form, 
                           query=query, job_type=job_type, location=location)

@jobs_bp.route('/<int:job_id>')
def detail(job_id):
    db = get_db()
    job = JobPost.query.filter_by(id=job_id, is_active=True).first_or_404()
    company = Company.query.get_or_404(job.company_id)

    already_applied = False
    student = None

    if current_user.is_authenticated:
        student = Student.query.filter_by(user_id=current_user.id).first()
        if student:
            application = Application.query.filter_by(student_id=student.id, job_post_id=job.id).first()
            already_applied = application is not None

    return render_template('jobs/detail.html', job=job, company=company, already_applied=already_applied)

@jobs_bp.route('/<int:job_id>/apply', methods=['GET', 'POST'])
@login_required
def apply(job_id):
    db = get_db()

    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash('Only students can apply for jobs!', 'danger')
        return redirect(url_for('jobs.detail', job_id=job_id))

    job = JobPost.query.filter_by(id=job_id, is_active=True).first_or_404()
    company = Company.query.get_or_404(job.company_id)

    existing_application = Application.query.filter_by(student_id=student.id, job_post_id=job.id).first()
    if existing_application:
        flash('You have already applied for this job!', 'info')
        return redirect(url_for('jobs.detail', job_id=job.id))

    form = ApplicationForm()

    if form.validate_on_submit():
        application = Application(
            student_id=student.id,
            job_post_id=job.id,
            cover_letter=form.cover_letter.data,
            status='pending'
        )
        db.session.add(application)
        db.session.commit()

        company_user = User.query.get(company.user_id) if company.user_id else None
        if company_user:
            message = f'New application received for "{job.title}" from {student.first_name} {student.last_name}'
            link = url_for('company.applications')
            create_notification(company_user, message, link)

        flash('Your application has been submitted successfully!', 'success')
        return redirect(url_for('jobs.detail', job_id=job.id))

    return render_template('jobs/apply.html', form=form, job=job, company=company)

@jobs_bp.route('/company/<int:company_id>')
def company_jobs(company_id):
    db = get_db()
    company = Company.query.get_or_404(company_id)
    jobs = JobPost.query.filter_by(company_id=company.id, is_active=True).order_by(JobPost.created_at.desc()).all()

    applied_jobs = set()
    if current_user.is_authenticated:
        student = Student.query.filter_by(user_id=current_user.id).first()
        if student:
            applications = Application.query.filter_by(student_id=student.id).all()
            applied_jobs = {app.job_post_id for app in applications}

    return render_template('jobs/company_jobs.html', jobs=jobs, company=company, applied_jobs=applied_jobs)

@jobs_bp.route('/start_conversation/<int:user_id>', methods=['GET'])
@login_required
def start_conversation(user_id):
    company_user = User.query.get_or_404(user_id)

    try:
        return redirect(url_for('messages.new_conversation', user_id=company_user.id))
    except Exception as e:
        flash('Conversation system not available or route is missing.', 'danger')
        return redirect(url_for('jobs.listing'))
