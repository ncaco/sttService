import json
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.base import get_db
from app.models import schemas
from app.models.transcription import ReportTemplate

router = APIRouter()


@router.get("/{code}", response_model=schemas.ReportTemplateFormatResponse)
def get_report_template_format(
    code: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    보고서 양식 코드에 해당하는 보고서 템플릿 포맷을 반환합니다.
    
    - **code**: 보고서 양식 코드 (예: C001)
    """
    # 데이터베이스에서 템플릿 조회
    template = db.query(ReportTemplate).filter(ReportTemplate.code == code).first()
    
    if not template:
        raise HTTPException(
            status_code=404,
            detail=f"코드 '{code}'에 해당하는 보고서 템플릿이 없습니다"
        )
    
    # 템플릿 데이터 반환
    return {
        "code": template.code,
        "name": template.name,
        "format": json.loads(template.template),
        "description": template.description
    }


@router.get("/", response_model=List[schemas.ReportTemplateResponse])
def list_report_templates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Any:
    """모든 보고서 템플릿 목록을 반환합니다."""
    templates = db.query(ReportTemplate).offset(skip).limit(limit).all()
    
    # ORM 모델을 Pydantic 모델로 변환
    return [
        schemas.ReportTemplateResponse(
            id=t.id,
            code=t.code,
            name=t.name,
            description=t.description,
            template=json.loads(t.template),
            created_at=t.created_at,
            updated_at=t.updated_at
        )
        for t in templates
    ]


@router.post("/", response_model=schemas.ReportTemplateResponse)
def create_report_template(
    template: schemas.ReportTemplateCreate,
    db: Session = Depends(get_db)
) -> Any:
    """새 보고서 템플릿을 생성합니다."""
    try:
        # 템플릿 데이터를 JSON 문자열로 변환
        template_json = json.dumps(template.template)
        
        # 데이터베이스에 템플릿 저장
        db_template = ReportTemplate(
            code=template.code,
            name=template.name,
            description=template.description,
            template=template_json
        )
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        
        # ORM 모델을 Pydantic 모델로 변환하여 반환
        return schemas.ReportTemplateResponse(
            id=db_template.id,
            code=db_template.code,
            name=db_template.name,
            description=db_template.description,
            template=json.loads(db_template.template),
            created_at=db_template.created_at,
            updated_at=db_template.updated_at
        )
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"코드 '{template.code}'의 템플릿이 이미 존재합니다"
        )


@router.post("/init-child-counseling", response_description="아동 상담 보고서 템플릿 초기화")
def init_child_counseling_template(db: Session = Depends(get_db)):
    """아동 상담 보고서 템플릿을 초기화합니다."""
    
    # 이미 존재하는지 확인
    existing = db.query(ReportTemplate).filter(ReportTemplate.code == "CHILD01").first()
    if existing:
        return {
            "message": "아동 상담 보고서 템플릿이 이미 존재합니다.",
            "template": json.loads(existing.template)
        }
    
    # 아동 상담 보고서 템플릿 정의
    child_counseling_template = {
        "fields": {
            "client_info": {
                "type": "object",
                "description": "내담자 기본 정보",
                "properties": {
                    "name": {"type": "string", "description": "내담 아동 이름"},
                    "age": {"type": "number", "description": "내담 아동 나이"},
                    "gender": {"type": "string", "description": "내담 아동 성별"},
                    "grade": {"type": "string", "description": "학년/학급"},
                    "guardian": {"type": "string", "description": "보호자 관계 및 이름"}
                }
            },
            "session_info": {
                "type": "object",
                "description": "상담 세션 정보",
                "properties": {
                    "date": {"type": "string", "description": "상담 일자"},
                    "duration": {"type": "number", "description": "상담 시간(분)"},
                    "session_number": {"type": "number", "description": "회기 번호"},
                    "counselor": {"type": "string", "description": "상담사 이름"}
                }
            },
            "presenting_issues": {
                "type": "array",
                "description": "주호소 문제",
                "items": {"type": "string"}
            },
            "counseling_goals": {
                "type": "array",
                "description": "상담 목표",
                "items": {"type": "string"}
            },
            "session_summary": {
                "type": "string",
                "description": "세션 요약"
            },
            "behavioral_observations": {
                "type": "array",
                "description": "행동 관찰 사항",
                "items": {"type": "string"}
            },
            "emotional_state": {
                "type": "object",
                "description": "정서 상태",
                "properties": {
                    "mood": {"type": "string", "description": "전반적인 기분"},
                    "affect": {"type": "string", "description": "정서 표현"},
                    "anxiety_level": {"type": "string", "description": "불안 수준"},
                    "stress_indicators": {"type": "array", "description": "스트레스 지표", "items": {"type": "string"}}
                }
            },
            "communication_patterns": {
                "type": "object",
                "description": "의사소통 패턴",
                "properties": {
                    "verbal": {"type": "string", "description": "언어적 의사소통"},
                    "nonverbal": {"type": "string", "description": "비언어적 의사소통"},
                    "interaction_style": {"type": "string", "description": "상호작용 스타일"}
                }
            },
            "play_themes": {
                "type": "array",
                "description": "놀이 주제 및 특징",
                "items": {"type": "string"}
            },
            "therapeutic_interventions": {
                "type": "array",
                "description": "사용된 치료적 개입",
                "items": {"type": "string"}
            },
            "progress_assessment": {
                "type": "string",
                "description": "진전 평가"
            },
            "recommendations": {
                "type": "array",
                "description": "권고사항",
                "items": {"type": "string"}
            },
            "next_session_plan": {
                "type": "string",
                "description": "다음 세션 계획"
            },
            "additional_notes": {
                "type": "string",
                "description": "추가 참고사항"
            }
        }
    }
    
    # 템플릿 저장
    template = ReportTemplate(
        code="CHILD01",
        name="아동 상담 보고서",
        description="아동 상담 결과를 기록하기 위한 종합적인 보고서 템플릿입니다. 상담 과정, 행동 관찰, 정서 상태, 놀이 주제, 개입 방법 등이 포함됩니다.",
        template=json.dumps(child_counseling_template, ensure_ascii=False)
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return {
        "message": "아동 상담 보고서 템플릿이 성공적으로 생성되었습니다.",
        "id": template.id,
        "code": template.code,
        "name": template.name,
        "template": child_counseling_template
    } 