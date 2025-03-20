from openai import OpenAI
from app.core.config import settings
from app.services.transcription_service import transcribe_audio
from app.services.report_service import text_to_report

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def summarize_audio(file_path, summary_options=None):
    """
    음성/영상 파일을 텍스트로 변환한 후 요약하여 보고서로 반환
    
    Args:
        file_path: 음성/영상 파일 경로
        summary_options: 요약 옵션 (dict)
            - length: 요약 길이 ('short', 'medium', 'long')
            - focus: 요약 초점 ('general', 'key_points', 'action_items')
            - language: 요약 언어 ('ko', 'en', 'ja', 등)
            
    Returns:
        dict: {"text": 원본 텍스트, "summary": 요약 텍스트, "report": 보고서 형식}
    """
    # 기본 옵션 설정
    if summary_options is None:
        summary_options = {}
    
    length = summary_options.get('length', 'medium')  # 기본값: medium
    focus = summary_options.get('focus', 'general')   # 기본값: general
    language = summary_options.get('language', 'ko')  # 기본값: 한국어
    
    # 음성/영상 파일을 텍스트로 변환
    transcription_result = transcribe_audio(file_path)
    original_text = transcription_result["text"]
    
    # 텍스트 요약
    summary = create_summary(original_text, length, focus, language)
    
    # 보고서 템플릿 정의
    report_template = {
        "fields": {
            "title": {"type": "string", "description": "보고서 제목"},
            "summary": {"type": "string", "description": "요약 내용"},
            "key_points": {"type": "array", "description": "주요 포인트 목록"},
            "action_items": {"type": "array", "description": "필요한 조치 사항 목록"},
            "additional_notes": {"type": "string", "description": "추가 참고사항"}
        }
    }
    
    # 요약된 텍스트를 보고서 형식으로 변환
    report = text_to_report(summary, report_template)
    
    return {
        "text": original_text,
        "summary": summary,
        "report": report,
        "duration": transcription_result["duration"]
    }

def create_summary(text, length='medium', focus='general', language='ko'):
    """
    텍스트를 요약
    
    Args:
        text: 요약할 텍스트
        length: 요약 길이 ('short', 'medium', 'long')
        focus: 요약 초점 ('general', 'key_points', 'action_items')
        language: 요약 언어 ('ko', 'en', 'ja', 등)
        
    Returns:
        str: 요약된 텍스트
    """
    # 길이에 따른 토큰 수 설정
    length_tokens = {
        'short': "100단어 이내로",
        'medium': "200-300단어 정도로",
        'long': "500단어 정도로"
    }
    
    # 초점에 따른 프롬프트 추가
    focus_prompt = {
        'general': "주요 내용을 균형있게 요약해주세요.",
        'key_points': "가장 중요한 핵심 포인트만 추출하여 요약해주세요.",
        'action_items': "필요한 조치사항과 결정사항을 중심으로 요약해주세요."
    }
    
    # 언어 설정
    language_prompt = {
        'ko': "한국어로 요약해주세요.",
        'en': "영어로 요약해주세요.",
        'ja': "일본어로 요약해주세요."
    }
    
    # 선택한 언어가 없으면 기본값 사용
    if language not in language_prompt:
        language = 'ko'
    
    # 프롬프트 구성
    prompt = f"""
    다음 텍스트를 {length_tokens.get(length, length_tokens['medium'])} 요약해주세요.
    {focus_prompt.get(focus, focus_prompt['general'])}
    {language_prompt.get(language, language_prompt['ko'])}
    
    원본 텍스트:
    {text}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 텍스트를 요약하는 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        print(f"OpenAI API 오류: {str(e)}")
        return f"요약 생성 중 오류가 발생했습니다: {str(e)}" 