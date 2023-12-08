from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from .models import User, UserRole
from . import db
from .forms import LoginForm, RegisterForm, CreateUserForm
import bcrypt

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', form=form)

@auth.route('/login', methods=['POST'])
def login_post():
    form = LoginForm()
    if form.validate_on_submit():
        # Login Code Goes Here
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        # Check if user exists and compare hashed password
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            flash('Please check login details and try again!')
            return redirect(url_for('auth.login'))

        # if all checks pass, log in the user
        login_user(user, remember=remember)
        return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
    form = RegisterForm()
    return render_template('signup.html', form=form)

@auth.route('/signup', methods=['POST'])
def signup_post():
    form = RegisterForm()
    if form.validate_on_submit():
        # code to validate and add user to db goes here
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        
        # check if email already exists in db
        user = User.query.filter_by(email=email).first()
        
        # if user already exists redirect back to signup page to retry
        if user:
            flash('User already exists!')
            return redirect(url_for('auth.signup'))

        # Hash the password with bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Fetch the role 'user' from the database
        role = UserRole.query.filter_by(name='user').first()

        # Create a new user with the data from the form, hashed password, and 'user' role
        new_user = User(email=email, name=name, password=hashed_password, roles=[role])

        # Add New User to db
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))

@auth.route('/create-user', methods=['GET', 'POST'])
@login_required
def create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        email = form.email.data
        name = form.name.data
        password = form.password.data
        role_name = form.role.data

        # Check if email aready exists
        user = User.query.filter_by(email=email).first()

        # If user already exists redirect back to create user page
        if user:
            flash('User already exists!', 'danger')
            return redirect(url_for('auth.create_user'))

        # Hash the password with bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Get role
        role = UserRole.query.filter_by(name=role_name).first()

        # Create a new user with the data from the form, hashed password and role
        new_user = User(email=email, name=name, password=hashed_password, roles=[role])

        # Add new user to db
        db.session.add(new_user)
        db.session.commit()

        flash('User created Successfully!', 'success')
        return redirect(url_for('auth.create_user'))
    return render_template('create_user.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

