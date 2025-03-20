from openai import OpenAI
from app.core.config import settings
import os

def get_openai_client():
    """OpenAI 클라이언트를 초기화하여 반환합니다."""
    # API 키 확인
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        raise ValueError("OpenAI API 키가 설정되지 않았습니다. OPENAI_API_KEY 환경 변수를 확인하세요.")
    
    # API 키가 환경 변수에도 설정되어 있는지 확인
    os.environ["OPENAI_API_KEY"] = api_key
    
    # OpenAI 클라이언트 초기화 및 반환
    return OpenAI(api_key=api_key)

# 기본 클라이언트 인스턴스 생성
client = get_openai_client() 