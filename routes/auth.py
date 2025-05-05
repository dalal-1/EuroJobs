from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from extensions import db  # Import db from extensions instead of app
from models import User, Student, Company
from forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Redirect to dashboard if the user is an admin
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))  # Redirect to admin dashboard
        return redirect(url_for('home'))  # For regular users, redirect to home
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            # Redirect to the appropriate page based on the user type
            if current_user.is_admin:
                next_page = url_for('admin.dashboard')  # Redirect to admin dashboard
            elif Student.query.filter_by(user_id=user.id).first():
                next_page = url_for('student.profile')
            elif Company.query.filter_by(user_id=user.id).first():
                next_page = url_for('company.profile')
            else:
                next_page = url_for('home')  # Default redirect
        
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()  # Get the user ID without committing
        
        if form.account_type.data == 'student':
            student = Student(user_id=user.id)
            db.session.add(student)
        else:  # company
            company = Company(user_id=user.id, name=form.username.data)
            db.session.add(company)
        
        db.session.commit()
        flash('Congratulations, you are now registered! Please login to continue.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))
