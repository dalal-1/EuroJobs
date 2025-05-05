from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms import BooleanField, IntegerField, FloatField, DateField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, URL, NumberRange, ValidationError
from models import User  # Assuming 'User' model is defined in 'models.py'

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    account_type = SelectField('Account Type', choices=[('student', 'Student'), ('company', 'Company')], validators=[DataRequired()])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already in use. Please choose a different one.')

class StudentProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=500)])
    education = TextAreaField('Education', validators=[Optional(), Length(max=500)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    website = StringField('Website', validators=[Optional(), URL(), Length(max=120)])
    profile_picture = FileField('Profile Picture', validators=[Optional(), FileAllowed(['jpg', 'png'], 'Images only!')])
    cv_file = FileField('CV', validators=[Optional(), FileAllowed(['pdf', 'doc', 'docx'], 'Documents only!')])
    submit = SubmitField('Update Profile')

class SkillForm(FlaskForm):
    name = StringField('Skill Name', validators=[DataRequired(), Length(max=64)])
    level = IntegerField('Skill Level (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField('Add Skill')

class CompanyProfileForm(FlaskForm):
    name = StringField('Company Name', validators=[DataRequired(), Length(max=128)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=2000)])
    industry = StringField('Industry', validators=[Optional(), Length(max=64)])
    website = StringField('Website', validators=[Optional(), URL(), Length(max=120)])
    location = StringField('Location', validators=[Optional(), Length(max=128)])
    size = SelectField('Company Size', choices=[
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('501-1000', '501-1000 employees'),
        ('1001+', '1001+ employees')
    ], validators=[Optional()])
    founded_year = IntegerField('Founded Year', validators=[Optional(), NumberRange(min=1800, max=2100)])
    logo = FileField('Company Logo', validators=[Optional(), FileAllowed(['jpg', 'png'], 'Images only!')])

    # 🆕 Ajout du champ 'company_select' pour voir les étudiants
    company_select = SelectField('Select Company', choices=[], validators=[Optional()])

    submit = SubmitField('Update Profile')

class JobPostForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired(), Length(max=128)])
    description = TextAreaField('Job Description', validators=[DataRequired(), Length(max=5000)])
    requirements = TextAreaField('Requirements', validators=[Optional(), Length(max=2000)])
    location = StringField('Location', validators=[Optional(), Length(max=128)])
    job_type = SelectField('Job Type', choices=[
        ('full-time', 'Full-time'),
        ('part-time', 'Part-time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('remote', 'Remote')
    ], validators=[DataRequired()])
    salary_min = FloatField('Minimum Salary', validators=[Optional()])
    salary_max = FloatField('Maximum Salary', validators=[Optional()])
    deadline = DateField('Application Deadline', validators=[Optional()], format='%Y-%m-%d')
    submit = SubmitField('Post Job')
    
    def validate_salary_max(self, salary_max):
        if self.salary_min.data and salary_max.data and self.salary_min.data > salary_max.data:
            raise ValidationError('Maximum salary must be greater than or equal to minimum salary.')

class ApplicationForm(FlaskForm):
    cover_letter = TextAreaField('Cover Letter', validators=[DataRequired(), Length(max=2000)])
    submit = SubmitField('Submit Application')

class MessageForm(FlaskForm):
    recipient_id = HiddenField('Recipient', validators=[DataRequired()])
    body = TextAreaField('Message', validators=[DataRequired(), Length(max=2000)])
    submit = SubmitField('Send Message')

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[Optional(), Length(max=128)])
    job_type = SelectField('Job Type', choices=[
        ('', 'All Types'),
        ('full-time', 'Full-time'),
        ('part-time', 'Part-time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('remote', 'Remote')
    ], validators=[Optional()])
    location = StringField('Location', validators=[Optional(), Length(max=128)])
    submit = SubmitField('Search')

