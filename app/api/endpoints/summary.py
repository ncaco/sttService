import os
import tempfile
import json
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.services.summary_service import summarize_audio
from app.services.transcription_service import transcribe_audio
from app.db.session import get_db
from app.models.transcription import Transcription, Summary

router = APIRouter()

class SummaryOptions(BaseModel):
    length: Optional[str] = "medium"  # short, medium, long
    focus: Optional[str] = "general"  # general, key_points, action_items
    language: Optional[str] = "ko"    # ko, en, ja, etc.

@router.post("/", response_description="음성 데이터 요약 및 보고서 생성")
async def create_summary(
    file: UploadFile = File(...),
    length: Optional[str] = Form("medium"),
    focus: Optional[str] = Form("general"),
    language: Optional[str] = Form("ko"),
    save_to_db: Optional[bool] = Form(True),
    db: Session = Depends(get_db)
):
    """
    음성/영상 파일을 업로드하여 요약 및 보고서 생성
    
    - **file**: 음성/영상 파일 (mp3, wav, mp4, etc.)
    - **length**: 요약 길이 (short, medium, long)
    - **focus**: 요약 초점 (general, key_points, action_items)
    - **language**: 요약 언어 (ko, en, ja, etc.)
    - **save_to_db**: 결과를 데이터베이스에 저장할지 여부
    """
    # 파일 확장자 확인
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    allowed_extensions = ['.mp3', '.wav', '.m4a', '.ogg', '.mp4', '.avi', '.mov', '.webm']
    
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, 
                          detail=f"지원되지 않는 파일 형식입니다. 지원 형식: {', '.join(allowed_extensions)}")
    
    # 임시 파일로 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
        temp_path = temp_file.name
        contents = await file.read()
        temp_file.write(contents)
    
    try:
        # 요약 옵션 설정
        summary_options = {
            'length': length,
            'focus': focus,
            'language': language
        }
        
        # 음성 데이터 요약
        result = summarize_audio(temp_path, summary_options)
        
        # 결과를 데이터베이스에 저장
        if save_to_db:
            # 먼저 변환 결과 저장
            file_type = "audio" if ext in ['.mp3', '.wav', '.m4a', '.ogg'] else "video"
            
            transcription = Transcription(
                file_name=filename,
                file_type=file_type,
                transcription_text=result["text"],
                duration=result["duration"]
            )
            db.add(transcription)
            db.flush()
            
            # 요약 결과 저장
            summary = Summary(
                transcription_id=transcription.id,
                summary_text=result["summary"],
                length=length,
                focus=focus,
                language=language,
                report_content=json.dumps(result["report"], ensure_ascii=False)
            )
            db.add(summary)
            db.commit()
            
            # 결과에 ID 추가
            result["transcription_id"] = transcription.id
            result["summary_id"] = summary.id
        
        return {
            "filename": filename,
            "duration": result["duration"],
            "text": result["text"],
            "summary": result["summary"],
            "report": result["report"],
            "saved_to_db": save_to_db,
            "ids": {
                "transcription_id": result.get("transcription_id"),
                "summary_id": result.get("summary_id")
            } if save_to_db else None
        }
    except Exception as e:
        # 에러 발생 시 트랜잭션 롤백
        if save_to_db:
            db.rollback()
        raise HTTPException(status_code=500, detail=f"요약 생성 중 오류가 발생했습니다: {str(e)}")
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_path):
            os.unlink(temp_path)

@router.get("/{summary_id}", response_description="요약 정보 조회")
def get_summary(summary_id: int, db: Session = Depends(get_db)):
    """
    요약 ID로 요약 정보 조회
    
    - **summary_id**: 요약 ID
    """
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="요약 정보를 찾을 수 없습니다")
    
    transcription = db.query(Transcription).filter(Transcription.id == summary.transcription_id).first()
    
    return {
        "id": summary.id,
        "transcription_id": summary.transcription_id,
        "file_name": transcription.file_name if transcription else None,
        "duration": transcription.duration if transcription else None,
        "text": transcription.transcription_text if transcription else None,
        "summary": summary.summary_text,
        "length": summary.length,
        "focus": summary.focus,
        "language": summary.language,
        "report": json.loads(summary.report_content) if summary.report_content else None,
        "created_at": summary.created_at,
        "updated_at": summary.updated_at
    } 