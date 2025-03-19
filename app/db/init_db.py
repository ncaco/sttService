from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.session import engine

def init_db() -> None:
    """데이터베이스 테이블 생성"""
    Base.metadata.create_all(bind=engine) 