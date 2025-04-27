from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from models import Student, Skill, Application, JobPost
from forms import StudentProfileForm, SkillForm
from utils import save_picture, save_cv

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/profile')
@login_required
def profile():
    student = Student.query.filter_by(user_id=current_user.id).first_or_404()
    skills = Skill.query.filter_by(student_id=student.id).all()
    # Get recent applications
    applications = Application.query.filter_by(student_id=student.id).order_by(Application.created_at.desc()).limit(5).all()
    return render_template('student/profile.html', student=student, skills=skills, applications=applications)

@student_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    student = Student.query.filter_by(user_id=current_user.id).first_or_404()
    form = StudentProfileForm()
    
    if form.validate_on_submit():
        student.first_name = form.first_name.data
        student.last_name = form.last_name.data
        student.bio = form.bio.data
        student.education = form.education.data
        student.phone = form.phone.data
        student.website = form.website.data
        
        if form.profile_picture.data:
            picture_file = save_picture(form.profile_picture.data, 'profile_pics')
            student.profile_picture = picture_file
        
        if form.cv_file.data:
            cv_file = save_cv(form.cv_file.data)
            student.cv_file = cv_file
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('student.profile'))
    
    elif request.method == 'GET':
        form.first_name.data = student.first_name
        form.last_name.data = student.last_name
        form.bio.data = student.bio
        form.education.data = student.education
        form.phone.data = student.phone
        form.website.data = student.website
    
    return render_template('student/edit_profile.html', form=form, student=student)

@student_bp.route('/add_skill', methods=['GET', 'POST'])
@login_required
def add_skill():
    student = Student.query.filter_by(user_id=current_user.id).first_or_404()
    form = SkillForm()
    
    if form.validate_on_submit():
        skill = Skill(
            student_id=student.id,
            name=form.name.data,
            level=form.level.data
        )
        db.session.add(skill)
        db.session.commit()
        flash('Skill added successfully!', 'success')
        return redirect(url_for('student.profile'))
    
    return render_template('student/edit_profile.html', form=form, student=student, skill_form=True)

@student_bp.route('/delete_skill/<int:skill_id>', methods=['POST'])
@login_required
def delete_skill(skill_id):
    student = Student.query.filter_by(user_id=current_user.id).first_or_404()
    skill = Skill.query.filter_by(id=skill_id, student_id=student.id).first_or_404()
    
    db.session.delete(skill)
    db.session.commit()
    flash('Skill deleted successfully!', 'success')
    return redirect(url_for('student.profile'))

@student_bp.route('/applications')
@login_required
def applications():
    student = Student.query.filter_by(user_id=current_user.id).first_or_404()
    applications = Application.query.filter_by(student_id=student.id).order_by(Application.created_at.desc()).all()
    return render_template('student/applications.html', applications=applications)

@student_bp.route('/withdraw_application/<int:application_id>', methods=['POST'])
@login_required
def withdraw_application(application_id):
    student = Student.query.filter_by(user_id=current_user.id).first_or_404()
    application = Application.query.filter_by(id=application_id, student_id=student.id).first_or_404()
    
    # Only allow withdrawing if still pending
    if application.status == 'pending':
        db.session.delete(application)
        db.session.commit()
        flash('Application withdrawn successfully!', 'success')
    else:
        flash('Cannot withdraw application that is already being processed.', 'danger')
    
    return redirect(url_for('student.applications'))
