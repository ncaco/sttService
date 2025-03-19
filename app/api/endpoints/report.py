import json
import os
import tempfile
from typing import Any
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models import schemas
from app.models.transcription import Report, ReportTemplate, Transcription
from app.services.transcription_service import transcribe_audio
from app.services.report_service import text_to_report

router = APIRouter()


@router.post("/text", response_model=schemas.ReportResponse)
def create_report_from_text(
    request: schemas.TextToReportRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    텍스트를 보고서 양식에 맞게 변환하여 보고서를 생성합니다.
    
    - **text**: 변환할 텍스트
    - **code**: 보고서 양식 코드 (예: C001)
    """
    # 템플릿 조회
    template = db.query(ReportTemplate).filter(ReportTemplate.code == request.code).first()
    if not template:
        raise HTTPException(
            status_code=404,
            detail=f"코드 '{request.code}'에 해당하는 보고서 템플릿이 없습니다"
        )
    
    # 텍스트를 보고서로 변환
    report_content = text_to_report(request.text, json.loads(template.template))
    
    # 데이터베이스에 저장
    db_report = Report(
        template_id=template.id,
        raw_text=request.text,
        content=json.dumps(report_content)
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    
    # 응답 반환
    return {
        "id": db_report.id,
        "code": template.code,
        "name": template.name,
        "content": report_content,
        "created_at": db_report.created_at
    }


@router.post("/audio", response_model=schemas.ReportResponse)
async def create_report_from_audio(
    file: UploadFile = File(...),
    code: str = None,
    db: Session = Depends(get_db)
) -> Any:
    """
    오디오 또는 영상 파일과 보고서 양식 코드를 받아 보고서를 생성합니다.
    
    - **file**: 변환할 오디오 또는 영상 파일
    - **code**: 보고서 양식 코드 (예: C001)
    """
    if not code:
        raise HTTPException(
            status_code=400,
            detail="보고서 양식 코드(code)가 필요합니다"
        )
    
    # 템플릿 조회
    template = db.query(ReportTemplate).filter(ReportTemplate.code == code).first()
    if not template:
        raise HTTPException(
            status_code=404,
            detail=f"코드 '{code}'에 해당하는 보고서 템플릿이 없습니다"
        )
    
    # 파일 확장자 확인
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    # 지원하는 파일 형식 확인
    audio_formats = ['.mp3', '.wav', '.ogg', '.m4a']
    video_formats = ['.mp4', '.avi', '.mov', '.webm']
    
    if file_ext in audio_formats:
        file_type = "audio"
    elif file_ext in video_formats:
        file_type = "video"
    else:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식입니다. 지원하는 형식: {', '.join(audio_formats + video_formats)}"
        )
    
    # 파일 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
        temp_file.write(await file.read())
        temp_file_path = temp_file.name
    
    try:
        # 음성/영상 변환
        transcription_result = transcribe_audio(temp_file_path)
        transcription_text = transcription_result["text"]
        
        # 데이터베이스에 변환 결과 저장
        db_transcription = Transcription(
            file_name=file.filename,
            file_type=file_type,
            transcription_text=transcription_text,
            duration=transcription_result.get("duration")
        )
        db.add(db_transcription)
        db.commit()
        db.refresh(db_transcription)
        
        # 텍스트를 보고서로 변환
        report_content = text_to_report(transcription_text, json.loads(template.template))
        
        # 데이터베이스에 보고서 저장
        db_report = Report(
            transcription_id=db_transcription.id,
            template_id=template.id,
            raw_text=transcription_text,
            content=json.dumps(report_content)
        )
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        
        # 응답 반환
        return {
            "id": db_report.id,
            "code": template.code,
            "name": template.name,
            "content": report_content,
            "created_at": db_report.created_at
        }
    
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path) 