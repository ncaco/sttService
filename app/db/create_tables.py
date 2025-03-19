from app.db.base import Base, engine
from app.models.transcription import Transcription, ReportTemplate, Report

def create_tables():
    """데이터베이스 테이블 생성"""
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
    print("데이터베이스 테이블이 생성되었습니다.") 