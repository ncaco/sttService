import json
import openai
from openai import OpenAI
from app.core.config import settings

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def text_to_report(text, template_format):
    """
    텍스트를 보고서 양식에 맞게 변환
    
    Args:
        text: 변환할 텍스트
        template_format: 보고서 템플릿 포맷 (dict)
        
    Returns:
        dict: 보고서 데이터
    """
    # 템플릿 포맷에서 필드 추출
    fields = template_format.get("fields", {})
    
    # OpenAI API를 사용하여 텍스트를 보고서로 변환
    prompt = f"""
    다음 텍스트를 지정된 보고서 양식에 맞게 변환해주세요.
    보고서에는 다음 필드가 포함되어야 합니다:
    
    {json.dumps(fields, ensure_ascii=False, indent=2)}
    
    입력 텍스트: 
    {text}
    
    JSON 형식으로 결과를 반환해주세요.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 텍스트를 구조화된 보고서로 변환하는 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        
        result_text = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API 오류: {str(e)}")
        raise
    
    # JSON 문자열에서 실제 JSON 부분만 추출
    try:
        # 응답에서 JSON 부분만 추출
        start_idx = result_text.find('{')
        end_idx = result_text.rfind('}') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = result_text[start_idx:end_idx]
            report_data = json.loads(json_str)
        else:
            # JSON 형식이 아닌 경우 텍스트 그대로 반환
            report_data = {"text": result_text}
    except json.JSONDecodeError:
        # JSON 파싱 오류 시 텍스트 그대로 반환
        report_data = {"text": result_text}
    
    # 템플릿 형식에 맞게 데이터 구조 확인 및 조정
    for field_name, field_info in fields.items():
        if field_name not in report_data:
            # 필드가 없는 경우 기본값 설정
            if field_info.get("type") == "array":
                report_data[field_name] = []
            else:
                report_data[field_name] = ""
    
    return report_data