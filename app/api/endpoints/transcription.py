import os
import tempfile
from typing import Any
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models import schemas
from app.models.transcription import Transcription
from app.services.transcription_service import transcribe_audio

router = APIRouter()


@router.post("/", response_model=schemas.TranscriptionResult)
async def transcribe_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Any:
    """
    오디오 또는 영상 파일을 업로드하여 텍스트로 변환합니다.
    
    - **file**: 변환할 오디오 또는 영상 파일
    """
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
        # 음성/영상 변환 서비스 호출
        transcription_result = transcribe_audio(temp_file_path)
        
        # 데이터베이스에 결과 저장
        db_transcription = Transcription(
            file_name=file.filename,
            file_type=file_type,
            transcription_text=transcription_result["text"],
            duration=transcription_result.get("duration")
        )
        db.add(db_transcription)
        db.commit()
        db.refresh(db_transcription)
        
        return transcription_result
    
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path) 