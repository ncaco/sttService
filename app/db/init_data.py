import json
from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.models.transcription import ReportTemplate

def init_data():
    """초기 데이터 생성"""
    db = SessionLocal()
    try:
        # 기존 데이터 확인
        existing_templates = db.query(ReportTemplate).all()
        if existing_templates:
            print(f"이미 {len(existing_templates)}개의 템플릿이 존재합니다.")
            return
        
        # 템플릿 데이터 생성
        templates = [
            {
                "code": "C001",
                "name": "회의록 양식",
                "description": "회의 내용을 요약하는 일반적인 회의록 양식",
                "template": {
                    "fields": {
                        "title": {"type": "string", "description": "회의 제목"},
                        "date": {"type": "string", "description": "회의 날짜"},
                        "participants": {"type": "array", "description": "참석자 목록"},
                        "agenda": {"type": "array", "description": "회의 안건 목록"},
                        "discussion": {"type": "array", "description": "논의 사항 목록"},
                        "action_items": {"type": "array", "description": "액션 아이템 목록"},
                        "next_meeting": {"type": "string", "description": "다음 회의 일정"}
                    }
                }
            },
            {
                "code": "C002",
                "name": "인터뷰 요약 양식",
                "description": "인터뷰 내용을 요약하는 양식",
                "template": {
                    "fields": {
                        "interviewee": {"type": "string", "description": "인터뷰 대상자"},
                        "interviewer": {"type": "string", "description": "인터뷰어"},
                        "date": {"type": "string", "description": "인터뷰 날짜"},
                        "duration": {"type": "string", "description": "인터뷰 시간"},
                        "key_topics": {"type": "array", "description": "주요 주제 목록"},
                        "summary": {"type": "string", "description": "인터뷰 요약"},
                        "key_quotes": {"type": "array", "description": "주요 인용구 목록"},
                        "follow_up": {"type": "string", "description": "후속 조치 사항"}
                    }
                }
            },
            {
                "code": "C003",
                "name": "강의 노트 양식",
                "description": "강의 내용을 요약하는 양식",
                "template": {
                    "fields": {
                        "title": {"type": "string", "description": "강의 제목"},
                        "instructor": {"type": "string", "description": "강사명"},
                        "date": {"type": "string", "description": "강의 날짜"},
                        "main_topics": {"type": "array", "description": "주요 주제 목록"},
                        "key_points": {"type": "array", "description": "핵심 요점 목록"},
                        "examples": {"type": "array", "description": "예시 목록"},
                        "questions": {"type": "array", "description": "질문 목록"},
                        "references": {"type": "array", "description": "참고 자료 목록"}
                    }
                }
            }
        ]
        
        # 데이터베이스에 템플릿 저장
        for template_data in templates:
            db_template = ReportTemplate(
                code=template_data["code"],
                name=template_data["name"],
                description=template_data["description"],
                template=json.dumps(template_data["template"])
            )
            db.add(db_template)
        
        db.commit()
        print(f"{len(templates)}개의 보고서 템플릿이 생성되었습니다.")
    
    finally:
        db.close()

if __name__ == "__main__":
    init_data() 