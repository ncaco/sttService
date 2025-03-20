from fastapi import APIRouter
from app.api.endpoints import transcription, report_template, report, summary

api_router = APIRouter()

# 음성/영상 변환 API
api_router.include_router(
    transcription.router,
    prefix="/transcription",
    tags=["transcription"]
)

# 보고서 템플릿 API
api_router.include_router(
    report_template.router,
    prefix="/report-template",
    tags=["report-template"]
)

# 보고서 API
api_router.include_router(
    report.router,
    prefix="/report",
    tags=["report"]
)

# 요약 API
api_router.include_router(
    summary.router,
    prefix="/summary",
    tags=["summary"]
) 