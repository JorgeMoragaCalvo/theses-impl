"""
Database initialization script.
Drops existing tables, creates new tables with updated schema,
and creates an initial admin user.
"""

import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import drop_db, init_db, SessionLocal, Student, UserRole
from app.auth import get_password_hash
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_database():
    """Initialize the database with the new schema."""
    logger.info("Dropping existing database tables...")
    try:
        drop_db()
        logger.info("Existing tables dropped successfully")
    except Exception as e:
        logger.warning(f"Could not drop tables (might not exist): {e}")

    logger.info("Creating new database tables...")
    try:
        init_db()
        logger.info("New tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise


def create_admin_user(
    name: str = "Admin User",
    email: str = "admin@example.com",
    password: str | None = None,
):
    """
    Create the first admin user.

    Args:
        name: Admin user's name
        email: Admin user's email (used for login)
        password: Admin user's password
    """

    if password is None:
        password = settings.admin_password

    db = SessionLocal()
    try:
        # Check if admin already exists
        existing_admin = db.query(Student).filter(Student.email == email).first()
        if existing_admin:
            logger.warning(f"Admin user with email {email} already exists")
            return existing_admin

        # Create admin user
        admin_user = Student(
            name=name,
            email=email,
            password_hash=get_password_hash(password),
            role=UserRole.ADMIN,
            is_active=True,
            knowledge_levels={
                "operations_research": "advanced",
                "mathematical_modeling": "advanced",
                "linear_programming": "advanced",
                "integer_programming": "advanced",
                "nonlinear_programming": "advanced",
            },
            preferences={},
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        logger.info("Admin user created successfully")
        logger.info(f"  Email: {email}")
        logger.info(f"  Password: {password}")
        logger.info(f"  ID: {admin_user.id}")
        logger.info("  IMPORTANT: Change the admin password after first login!")

        return admin_user

    except Exception as e:
        logger.error(f"Failed to create admin user: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main initialization function."""
    print("=" * 60)
    print("DATABASE INITIALIZATION SCRIPT")
    print("=" * 60)
    print()

    print("WARNING: This will DROP all existing tables and data!")
    response = input("Do you want to continue? (yes/no): ")

    if response.lower() not in ["yes", "y"]:
        print("Initialization cancelled.")
        return

    print()

    # Initialize database
    initialize_database()
    print()

    # Create admin user
    print("Creating admin user...")
    print("You can customize the admin credentials or press Enter to use defaults:")
    print()

    name = input("Admin name (default: Admin User): ").strip() or "Admin User"
    email = (
        input("Admin email (default: admin@example.com): ").strip()
        or "admin@example.com"
    )
    password = (
        input(
            f"Admin password (default from ADMIN_PASSWORD: {settings.admin_password}): "
        ).strip()
        or settings.admin_password
    )

    print()
    create_admin_user(name=name, email=email, password=password)

    print()
    print("=" * 60)
    print("Database initialization complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Start the backend server: python -m app.main")
    print("2. Start the frontend: streamlit run frontend/app.py")
    print("3. Login with your admin credentials")
    print("4. Change the admin password from the UI")
    print()


if __name__ == "__main__":
    main()
