import uvicorn
from app.db.create_tables import create_tables
from app.db.init_data import init_data

if __name__ == "__main__":
    print("데이터베이스 테이블 생성 중...")
    create_tables()
    
    print("초기 데이터 생성 중...")
    init_data()
    
    print("STT 서비스 애플리케이션 시작 중...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 