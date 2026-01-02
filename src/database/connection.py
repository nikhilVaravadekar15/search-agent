from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from src.commonlib.config import settings

engine = create_engine(settings.db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> SessionLocal:
    """Create and yield a database session.

    This is a dependency that will be used in FastAPI endpoints.
    The session is automatically closed after use.

    Yields:
        SessionLocal: SQLAlchemy database session

    Example:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
