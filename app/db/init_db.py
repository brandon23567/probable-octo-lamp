import logging
from sqlalchemy import text
from app.db.session import engine
from app.db.base import Base
from app.models.user import User
from app.models.project import Project
from app.models.error_memory import ErrorMemory
from app.models.job import Job

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    try:
        with engine.connect() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            connection.commit()
            logger.info("pgvector extension created/verified.")
        
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    init_db()
