from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base

class Transcription(Base):
    """음성/영상 파일의 변환 결과를 저장하는 모델"""
    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # audio or video
    transcription_text = Column(Text, nullable=True)
    duration = Column(Integer, nullable=True)  # 파일 길이(초)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Transcription(id={self.id}, file_name={self.file_name})>"


class ReportTemplate(Base):
    """보고서 템플릿 정보를 저장하는 모델"""
    __tablename__ = "report_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    template = Column(Text, nullable=False)  # JSON 형식으로 저장된 템플릿
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ReportTemplate(id={self.id}, code={self.code})>"


class Report(Base):
    """생성된 보고서 정보를 저장하는 모델"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    transcription_id = Column(Integer, ForeignKey("transcriptions.id"), nullable=True)
    template_id = Column(Integer, ForeignKey("report_templates.id"), nullable=False)
    content = Column(Text, nullable=False)  # JSON 형식으로 저장된 보고서 내용
    raw_text = Column(Text, nullable=True)  # 직접 입력된 텍스트
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Report(id={self.id}, template_id={self.template_id})>" 