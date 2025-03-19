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