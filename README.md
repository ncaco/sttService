# STT Service

음성/영상 파일을 텍스트로 변환하고 분석하는 API 서비스입니다.

## 기능

1. 음성/영상 파일의 텍스트 변환
2. 변환된 텍스트의 보고서 생성
3. 요약본 생성

## 설치 및 실행

### 환경 설정

1. `.env.example` 파일을 복사하여 `.env` 파일을 만듭니다.
2. `.env` 파일에 OpenAI API 키를 설정합니다.

```bash
cp .env.example .env
# .env 파일을 편집하여 OPENAI_API_KEY를 설정합니다.
```

### Docker를 사용한 실행

```bash
docker-compose up -d
```

## API 문서

서비스가 실행되면 다음 URL에서 API 문서를 확인할 수 있습니다:

```
http://localhost:8000/api/docs
```

## 주요 API 엔드포인트

- `/api/transcription/`: 음성/영상 파일 텍스트 변환
- `/api/report-template/`: 보고서 템플릿 관리
- `/api/report/`: 보고서 생성
- `/api/summary/`: 음성/영상 파일 요약