from app import create_app
from models.user import User

def check_admin():
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("Admin user exists:")
            print(f"Username: {admin.username}")
            print(f"Is Admin: {admin.is_admin}")
            print(f"Password Hash: {admin.password_hash}")
        else:
            print("Admin user does not exist!")

if __name__ == "__main__":
    check_admin() 