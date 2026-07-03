# ============================================================
# app/database.py
# Database connection, session factory, and base class
# Bridges Python code to PostgreSQL
# ============================================================

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True, pool_size=5, max_overflow=10)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False

)

class Base(DeclarativeBase):
    pass


def get_db():
    """
    Creates a new database session for each request.
    Yields the session to the endpoint.
    Closes the session after the endpoint finishes,
    even if an error occurs.

    Usage in FastAPI:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Creates all tables defined by models that inherit from Base.
    Safe to call multiple times — only creates tables that don't exist yet.
    """
    Base.metadata.create_all(bind=engine)
    print("Database tables created")
