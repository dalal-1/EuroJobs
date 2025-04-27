from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from models import Company, JobPost, Application, Student, User
from forms import CompanyProfileForm, JobPostForm
from utils import save_picture, create_notification
from datetime import datetime

company_bp = Blueprint('company', __name__, url_prefix='/company')

@company_bp.route('/profile')
@login_required
def profile():
    company = Company.query.filter_by(user_id=current_user.id).first_or_404()
    jobs = JobPost.query.filter_by(company_id=company.id).order_by(JobPost.created_at.desc()).all()
    active_jobs_count = JobPost.query.filter_by(company_id=company.id, is_active=True).count()
    
    return render_template('company/profile.html', company=company, jobs=jobs, active_jobs_count=active_jobs_count)

@company_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    company = Company.query.filter_by(user_id=current_user.id).first_or_404()
    form = CompanyProfileForm()
    
    if form.validate_on_submit():
        company.name = form.name.data
        company.description = form.description.data
        company.industry = form.industry.data
        company.website = form.website.data
        company.location = form.location.data
        company.size = form.size.data
        company.founded_year = form.founded_year.data
        
        if form.logo.data:
            logo_file = save_picture(form.logo.data, 'profile_pics')
            company.logo = logo_file
        
        db.session.commit()
        flash('Your company profile has been updated!', 'success')
        return redirect(url_for('company.profile'))
    
    elif request.method == 'GET':
        form.name.data = company.name
        form.description.data = company.description
        form.industry.data = company.industry
        form.website.data = company.website
        form.location.data = company.location
        form.size.data = company.size
        form.founded_year.data = company.founded_year
    
    return render_template('company/edit_profile.html', form=form, company=company)

@company_bp.route('/create_job', methods=['GET', 'POST'])
@login_required
def create_job():
    company = Company.query.filter_by(user_id=current_user.id).first_or_404()
    form = JobPostForm()
    
    if form.validate_on_submit():
        job = JobPost(
            company_id=company.id,
            title=form.title.data,
            description=form.description.data,
            requirements=form.requirements.data,
            location=form.location.data,
            job_type=form.job_type.data,
            salary_min=form.salary_min.data,
            salary_max=form.salary_max.data,
            deadline=form.deadline.data
        )
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('company.profile'))
    
    return render_template('company/job_post.html', form=form, company=company)

@company_bp.route('/manage_job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def manage_job(job_id):
    company = Company.query.filter_by(user_id=current_user.id).first_or_404()
    job = JobPost.query.filter_by(id=job_id, company_id=company.id).first_or_404()
    
    form = JobPostForm()
    
    if form.validate_on_submit():
        job.title = form.title.data
        job.description = form.description.data
        job.requirements = form.requirements.data
        job.location = form.location.data
        job.job_type = form.job_type.data
        job.salary_min = form.salary_min.data
        job.salary_max = form.salary_max.data
        job.deadline = form.deadline.data
        
        db.session.commit()
        flash('Job updated successfully!', 'success')
        return redirect(url_for('company.manage_job', job_id=job.id))
    
    elif request.method == 'GET':
        form.title.data = job.title
        form.description.data = job.description
        form.requirements.data = job.requirements
        form.location.data = job.location
        form.job_type.data = job.job_type
        form.salary_min.data = job.salary_min
        form.salary_max.data = job.salary_max
        form.deadline.data = job.deadline
    
    applications = Application.query.filter_by(job_post_id=job.id).all()
    
    return render_template('company/manage_job.html', form=form, job=job, company=company, applications=applications)

@company_bp.route('/toggle_job_status/<int:job_id>', methods=['POST'])
@login_required
def toggle_job_status(job_id):
    company = Company.query.filter_by(user_id=current_user.id).first_or_404()
    job = JobPost.query.filter_by(id=job_id, company_id=company.id).first_or_404()
    
    job.is_active = not job.is_active
    db.session.commit()
    
    status = "activated" if job.is_active else "deactivated"
    flash(f'Job {status} successfully!', 'success')
    return redirect(url_for('company.manage_job', job_id=job.id))

@company_bp.route('/delete_job/<int:job_id>', methods=['POST'])
@login_required
def delete_job(job_id):
    company = Company.query.filter_by(user_id=current_user.id).first_or_404()
    job = JobPost.query.filter_by(id=job_id, company_id=company.id).first_or_404()
    
    # First, delete all applications for this job
    Application.query.filter_by(job_post_id=job.id).delete()
    
    # Then delete the job
    db.session.delete(job)
    db.session.commit()
    
    flash('Job deleted successfully!', 'success')
    return redirect(url_for('company.profile'))

@company_bp.route('/applications')
@login_required
def applications():
    company = Company.query.filter_by(user_id=current_user.id).first_or_404()
    jobs = JobPost.query.filter_by(company_id=company.id).all()
    job_ids = [job.id for job in jobs]
    
    applications = Application.query.filter(Application.job_post_id.in_(job_ids)).order_by(Application.created_at.desc()).all()
    
    return render_template('company/applications.html', applications=applications, company=company)

@company_bp.route('/update_application_status/<int:application_id>', methods=['POST'])
@login_required
def update_application_status(application_id):
    company = Company.query.filter_by(user_id=current_user.id).first_or_404()
    
    # Find the application and check if it belongs to a job from this company
    application = Application.query.filter_by(id=application_id).first_or_404()
    job = JobPost.query.filter_by(id=application.job_post_id, company_id=company.id).first_or_404()
    
    new_status = request.form.get('status')
    if new_status not in ['pending', 'reviewing', 'rejected', 'accepted']:
        flash('Invalid status!', 'danger')
        return redirect(url_for('company.applications'))
    
    application.status = new_status
    db.session.commit()
    
    # Create notification for the student
    student = Student.query.filter_by(id=application.student_id).first()
    user = User.query.filter_by(id=student.user_id).first()
    
    message = f'Your application for "{job.title}" has been updated to: {new_status.capitalize()}'
    link = url_for('student.applications')
    create_notification(user, message, link)
    
    flash('Application status updated successfully!', 'success')
    return redirect(url_for('company.applications'))
