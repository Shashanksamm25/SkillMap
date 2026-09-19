"""
auth/auth_db.py — User creation, login verification, password hashing
"""
import hashlib, os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import User, get_session

def hash_password(password: str) -> str:
    """Simple SHA-256 hash with salt."""
    salt = "skillmap_salt_2024"
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()

def create_user(username: str, email: str, password: str, role: str = "user") -> bool:
    """Create a new user. Returns True if successful, False if username/email exists."""
    session = get_session()
    try:
        existing = session.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing:
            return False
        user = User(
            username=username,
            email=email,
            password=hash_password(password),
            role=role
        )
        session.add(user)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error creating user: {e}")
        return False
    finally:
        session.close()

def verify_login(username: str, password: str):
    """Returns User object if login is valid, else None."""
    session = get_session()
    try:
        user = session.query(User).filter_by(
            username=username,
            password=hash_password(password),
            is_active=True
        ).first()
        if user:
            return {"id": user.id, "username": user.username,
                    "email": user.email, "role": user.role}
        return None
    finally:
        session.close()

def get_all_users():
    """Admin only — get all users."""
    session = get_session()
    try:
        users = session.query(User).all()
        return [{"id": u.id, "username": u.username, "email": u.email,
                 "role": u.role, "active": u.is_active,
                 "created": u.created_at.strftime("%Y-%m-%d")} for u in users]
    finally:
        session.close()

def toggle_user_status(user_id: int):
    """Admin — activate or deactivate a user."""
    session = get_session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            user.is_active = not user.is_active
            session.commit()
    finally:
        session.close()

def seed_admin():
    """Create default admin account if it doesn't exist."""
    create_user("admin", "admin@skillmap.com", "admin123", role="admin")
    print("Admin account ready — username: admin | password: admin123")

if __name__ == "__main__":
    seed_admin()