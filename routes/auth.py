from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import Admin
from extensions import db
from werkzeug.security import check_password_hash
from wtforms import Form, StringField, PasswordField, validators, EmailField
from wtforms.validators import ValidationError
import re
import secrets

bp = Blueprint('auth', __name__, url_prefix='/')

class LoginForm(Form):
    email = EmailField('Email', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])

class SignupForm(Form):
    full_name = StringField('Full Name', [validators.DataRequired(), validators.Length(min=2, max=100)])
    email = EmailField('Email', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=8)])
    confirm_password = PasswordField('Confirm Password', [validators.DataRequired()])

    def validate_confirm_password(self, field):
        if field.data != self.password.data:
            raise ValidationError('Passwords do not match')

class ForgotForm(Form):
    email = EmailField('Email', [validators.DataRequired()])

@bp.route('/signup', methods=['POST'])
def signup():
    form = SignupForm(request.form)
    if not form.validate():
        return jsonify({'error': form.errors}), 400

    if Admin.query.filter_by(email=form.email.data).first():
        return jsonify({'error': 'Email already registered'}), 400

    admin = Admin(full_name=form.full_name.data, email=form.email.data)
    admin.set_password(form.password.data)
    db.session.add(admin)
    db.session.commit()
    print("SIGNUP DEBUG - user created:", admin.id, admin.email)
    print("SIGNUP DEBUG - stored hash:", admin.password_hash)

    return jsonify({'success': True, 'message': 'Account created'}), 201

@bp.route('/login', methods=['POST'])
def login():
    # Log raw request
    print("LOGIN DEBUG - raw request.form:", dict(request.form))
    
    form = LoginForm(request.form)
    
    # Strip whitespace and log
    if form.email.data:
        form.email.data = form.email.data.strip()
    if form.password.data:
        form.password.data = form.password.data.strip()
        
    print("LOGIN DEBUG - after strip - email data:", repr(form.email.data))
    print("LOGIN DEBUG - after strip - password data length:", len(form.password.data) if form.password.data else 0)
    print("LOGIN DEBUG - form.errors:", form.errors)
    
    if not form.validate():
        print("LOGIN DEBUG - validation failed")
        return jsonify({'error': f'Validation failed: {form.errors}'}), 400

    admin = Admin.query.filter_by(email=form.email.data).first()
    print("LOGIN DEBUG - admin found:", admin is not None, getattr(admin, 'email', None))
    
    if admin:
        print("LOGIN DEBUG - stored hash:", admin.password_hash)
        print("LOGIN DEBUG - input pw:", form.password.data)
        print("LOGIN DEBUG - check result:", admin.check_password(form.password.data))
        if admin.check_password(form.password.data):
            print("LOGIN DEBUG - password check passed")
            remember = bool(request.form.get('remember', False))
            login_user(admin, remember=remember)
            return jsonify({
                'success': True,
                'user': {
                    'id': admin.id,
                    'full_name': admin.full_name,
                    'email': admin.email
                }
            }), 200
        print("LOGIN DEBUG - password mismatch")
    else:
        print("LOGIN DEBUG - no admin found for email")
    print("LOGIN DEBUG - login failed")
    return jsonify({'error': 'Invalid credentials'}), 401

@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'success': True}), 200

@bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    form = ForgotForm(request.form)
    if not form.validate():
        return jsonify({'success': True, 'message': 'Reset link sent (if email exists)'}), 200  # Always success

    admin = Admin.query.filter_by(email=form.email.data).first()
    if admin:
        token = admin.generate_reset_token()
        print(f'Reset token for {form.email.data}: {token} (expires in 1h)')
        current_app.logger.info(f'Reset token generated for {form.email.data}: {token}')

    return jsonify({'success': True, 'message': 'Reset link sent (if email exists)'}), 200

