from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import Opportunity, Admin
from extensions import db
from datetime import datetime
from wtforms import Form, StringField, IntegerField, SelectField, DateField, TextAreaField, validators, EmailField
import json

bp = Blueprint('opportunities', __name__, url_prefix='/api')

class OpportunityForm(Form):
    name = StringField('Name', [validators.DataRequired(), validators.Length(max=100)])
    duration = StringField('Duration', [validators.DataRequired(), validators.Length(max=50)])
    start_date = DateField('Start Date', [validators.DataRequired()])
    description = TextAreaField('Description', [validators.DataRequired()])
    skills = StringField('Skills', [validators.DataRequired()])
    category = SelectField('Category', choices=[
        ('technology', 'Technology'),
        ('business', 'Business'),
        ('design', 'Design'),
        ('marketing', 'Marketing'),
        ('data_science', 'Data Science'),
        ('other', 'Other')
    ], validators=[validators.DataRequired()])
    future_opportunities = TextAreaField('Future Opportunities', [validators.DataRequired()])
    max_applicants = IntegerField('Max Applicants')

@bp.route('/opportunities', methods=['GET'])
@login_required
def get_opportunities():
    opps = Opportunity.query.filter_by(admin_id=current_user.id).all()
    data = [{
        'id': o.id,
        'name': o.name,
        'duration': o.duration,
        'start_date': o.start_date.isoformat(),
        'description': o.description[:100] + '...',
        'skills': o.skills,
        'category': o.category,
        'future_opportunities': o.future_opportunities,
        'max_applicants': o.max_applicants,
        'created_at': o.created_at.isoformat()
    } for o in opps]
    return jsonify({'success': True, 'data': data})

@bp.route('/opportunities', methods=['POST'])
@login_required
def create_opportunity():
    form = OpportunityForm(request.form)
    if not form.validate():
        return jsonify({'error': form.errors}), 400

    opp = Opportunity(
        name=form.name.data,
        duration=form.duration.data,
        start_date=form.start_date.data,
        description=form.description.data,
        skills=form.skills.data,
        category=form.category.data,
        future_opportunities=form.future_opportunities.data,
        max_applicants=form.max_applicants.data,
        admin_id=current_user.id
    )
    db.session.add(opp)
    db.session.commit()
    return jsonify({
        'success': True,
        'data': {
            'id': opp.id,
            'name': opp.name,
            # ... full obj
        }
    }), 201

@bp.route('/opportunities/<int:id>', methods=['GET'])
@login_required
def get_opportunity(id):
    opp = Opportunity.query.filter_by(id=id, admin_id=current_user.id).first_or_404()
    data = {
        'id': opp.id,
        'name': opp.name,
        'duration': opp.duration,
        'start_date': opp.start_date.isoformat(),
        'description': opp.description,
        'skills': opp.skills,
        'category': opp.category,
        'future_opportunities': opp.future_opportunities,
        'max_applicants': opp.max_applicants
    }
    return jsonify({'success': True, 'data': data})

@bp.route('/opportunities/<int:id>', methods=['PUT'])
@login_required
def update_opportunity(id):
    opp = Opportunity.query.filter_by(id=id, admin_id=current_user.id).first_or_404()
    form = OpportunityForm(request.form)
    if not form.validate():
        return jsonify({'error': form.errors}), 400

    opp.name = form.name.data
    opp.duration = form.duration.data
    opp.start_date = form.start_date.data
    opp.description = form.description.data
    opp.skills = form.skills.data
    opp.category = form.category.data
    opp.future_opportunities = form.future_opportunities.data
    opp.max_applicants = form.max_applicants.data
    db.session.commit()
    return jsonify({'success': True, 'message': 'Updated'})

@bp.route('/opportunities/<int:id>', methods=['DELETE'])
@login_required
def delete_opportunity(id):
    opp = Opportunity.query.filter_by(id=id, admin_id=current_user.id).first_or_404()
    db.session.delete(opp)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Deleted'})

