import logging
import hashlib
from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.orm import Session
from pgvector.sqlalchemy import Vector
from sentence_transformers import SentenceTransformer
from app.agent.llm import get_model
from app.models.error_memory import ErrorMemory
from app.db.session import SessionLocal

logger = logging.getLogger("agent")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# need to use a local embedding model and not this one
async def get_embedding(text: str) -> list[float]:
    embeddings = embedding_model.encode(text)
    
    return embeddings

def calculate_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

async def find_similar_error(error_summary: str, threshold: float = 0.85) -> Optional[ErrorMemory]:
    try:
        embedding = await get_embedding(error_summary)
        
        db: Session = SessionLocal()
        try:
            # Cosine distance: <=> operator in pgvector is cosine distance (1 - cosine similarity)
            # So similarity >= 0.85 means distance <= 0.15
            # Wait, typically we select by distance and filter.
            # pgvector: <-> is L2, <=> is cosine distance, <#> is inner product.
            # Cosine distance range [0, 2]. 0 is identical.
            # Convert threshold: distance <= 1 - 0.85 = 0.15
            
            target_distance = 1 - threshold
            
            stmt = select(ErrorMemory).order_by(
                ErrorMemory.embedding.cosine_distance(embedding)
            ).limit(1)
            
            result = db.execute(stmt).scalars().first()
            
            if result:
                 # Check the actual distance if needed, or trust the order_by + limit logic isn't enough?
                 # We need to filter by distance.
                 # SQLAlchemy doesn't return the distance easily unless we select it.
                 pass
            
            # Better query to get distance
            stmt = select(ErrorMemory, ErrorMemory.embedding.cosine_distance(embedding).label("distance")) \
                   .order_by("distance").limit(1)
            
            res = db.execute(stmt).first()
            if res:
                memory, distance = res
                if distance <= target_distance:
                    logger.info(f"Found similar error memory. Distance: {distance}")
                    return memory
            
            return None
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error finding similar memory: {e}")
        return None

async def store_error_memory(error_summary: str, file_path: str, corrected_code: str):
    try:
        embedding = await get_embedding(error_summary)
        error_hash = calculate_hash(error_summary)
        
        db: Session = SessionLocal()
        try:
            memory = ErrorMemory(
                error_hash=error_hash,
                error_summary=error_summary,
                file_path=file_path,
                corrected_code=corrected_code,
                embedding=embedding
            )
            db.add(memory)
            db.commit()
            logger.info("Stored error memory.")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error storing memory: {e}")
