# test_db.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db, create_tables, engine
from app.models import User, Document, Conversation, Messages
from sqlalchemy.orm import Session

# Test connection
try:
    with engine.connect() as conn:
        print("✅ Connected to PostgreSQL")
except Exception as e:
    print(f"❌ Connection failed: {e}")

# Create all 4 tables
create_tables()

# Test inserting a user
db = next(get_db())
    # Check if test user already exists
existing = db.query(User).filter(User.email == "test@example.com").first()
    
if not existing:
        test_user = User(
            username = "test",
            email="test@example.com",
            password_hash="fake_hash_for_testing"
        )
        db.add(test_user)
        db.commit()
        print("✅ Test user created")
else:
        print("✅ Test user already exists")

    # Query the user back
user = db.query(User).filter(User.email == "test@example.com").first()
print(f"✅ Found user: {user.email} (id={user.id})")