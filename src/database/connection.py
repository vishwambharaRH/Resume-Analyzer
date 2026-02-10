# src/database/connection.py

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# --- Configuration (Load from Environment) ---
POSTGRES_USER = os.environ.get("POSTGRES_USER", "parser_user")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "secret")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "resume_parser_db")

# Construct the database URL
DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# --- SQLAlchemy Engine and Session ---
# The Engine is the starting point for all SQLAlchemy applications
Engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# SessionLocal is a class used to create a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)


@contextmanager
def get_db_session():
    """
    Context manager to provide a transactional database session.
    Automatically handles commit/rollback and closing the session.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database transaction error (Rollback executed): {e}")
        # Re-raise the exception after rollback
        raise
    finally:
        db.close()


def init_db(base_class):
    # """
    # Initialize database connection and create tables if they don't exist.
    # """
    # try:
    #     # Import models here to register them with the Base class
    #     import src.database.metadata_model

    #     # Create all defined tables in the database
    #     base_class.metadata.create_all(bind=Engine)
    #     print(f"📦 Database tables created successfully for {POSTGRES_DB}")
    #     return True
    # except Exception:
    #     print(
    #         "❌ Database initialization or table creation failed. Check DB server/creds."
    #     )
    #     import traceback

    #     traceback.print_exc()
    #     return False
    return None
