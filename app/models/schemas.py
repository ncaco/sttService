from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class TranscriptionBase(BaseModel):
    file_name: str
    file_type: str


class TranscriptionCreate(TranscriptionBase):
    pass


class TranscriptionResponse(TranscriptionBase):
    id: int
    transcription_text: Optional[str] = None
    duration: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ReportTemplateBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    template: Dict[str, Any]


class ReportTemplateCreate(ReportTemplateBase):
    pass


class ReportTemplateResponse(ReportTemplateBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ReportBase(BaseModel):
    template_id: int
    content: Dict[str, Any]
    raw_text: Optional[str] = None


class ReportCreate(ReportBase):
    transcription_id: Optional[int] = None


class ReportResponse(ReportBase):
    id: int
    transcription_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# API 요청 및 응답 스키마
class TranscriptionRequest(BaseModel):
    """음성/영상 변환 요청 스키마"""
    # 파일은 FastAPI의 UploadFile로 처리되므로 여기서는 정의하지 않음
    pass


class TranscriptionResult(BaseModel):
    """음성/영상 변환 결과 스키마"""
    text: str
    duration: Optional[int] = None


class ReportTemplateFormatRequest(BaseModel):
    """보고서 템플릿 포맷 요청 스키마"""
    code: str = Field(..., description="보고서 양식 코드 (예: C001)")


class ReportTemplateFormatResponse(BaseModel):
    """보고서 템플릿 포맷 응답 스키마"""
    code: str
    name: str
    format: Dict[str, Any]
    description: Optional[str] = None


class TextToReportRequest(BaseModel):
    """텍스트를 보고서로 변환 요청 스키마"""
    text: str = Field(..., description="변환할 텍스트")
    code: str = Field(..., description="보고서 양식 코드 (예: C001)")


class AudioToReportRequest(BaseModel):
    """음성/영상을 보고서로 변환 요청 스키마"""
    # 파일은 FastAPI의 UploadFile로 처리되므로 여기서는 정의하지 않음
    code: str = Field(..., description="보고서 양식 코드 (예: C001)")


class ReportResponse(BaseModel):
    """보고서 응답 스키마"""
    id: int
    code: str
    name: str
    content: Dict[str, Any]
    created_at: datetime 