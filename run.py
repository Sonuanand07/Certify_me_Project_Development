from app import create_app
from extensions import db
from models import Admin
import os

app = create_app()

with app.app_context():
    db.create_all()
    if not Admin.query.filter_by(email='demo@admin.com').first():
        demo = Admin(full_name='Demo Admin', email='demo@admin.com')
        demo.set_password('demopass123')
        db.session.add(demo)
        db.session.commit()
    print('Demo user created: demo@admin.com / demopass123')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

