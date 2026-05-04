from app import create_app
from extensions import db
from models import Admin

app = create_app()
with app.app_context():
    db.create_all()
    # Create demo user
    if not Admin.query.filter_by(email='demo@admin.com').first():
        demo = Admin(full_name='Demo Admin', email='demo@admin.com')
        demo.set_password('demopass123')
        db.session.add(demo)
        db.session.commit()
    print('DB initialized with demo user: demo@admin.com / demopass123')

