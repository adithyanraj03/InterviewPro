import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models.user import User

def create_admin():
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("Admin user already exists!")
            return
        
        try:
            # Create admin user            admin = User(
                username='admin',
                is_admin=True
            )
            admin.set_password('admin123')  # Updated to match README
            print("Admin user created with:")
            print(f"Username: {admin.username}")
            print(f"Is Admin: {admin.is_admin}")
            print(f"Password Hash: {admin.password_hash}")
            
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
            
            # Verify the user was created
            admin_check = User.query.filter_by(username='admin').first()
            if admin_check:
                print("Verified: Admin user exists in database")
            else:
                print("Error: Admin user not found in database after creation!")
        except Exception as e:
            print(f"Error creating admin: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    create_admin() 