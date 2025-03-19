# sttService

이 프로젝트는 FastAPI와 Docker를 사용하여 음성 인식 서비스를 제공하는 프로젝트입니다. PostgreSQL과 통신하며, OpenAI의 Whisper 모델을 활용합니다.

## 주요 기능

1. **도커 컴포즈 설정**
   - 프로젝트는 Docker Compose를 사용하여 손쉽게 배포 및 실행할 수 있도록 설정되어 있습니다.

2. **FastAPI 설정**
   - FastAPI를 사용하여 RESTful API를 구현합니다.

3. **PostgreSQL 통신**
   - 데이터베이스로 PostgreSQL을 사용하며, API와의 통신을 통해 데이터를 저장하고 조회합니다.

4. **OpenAI Whisper 모델 사용**
   - 음성 인식 기능을 위해 OpenAI의 Whisper 모델을 사용합니다.

## API 기능

각각의 기능은 API로 구현되어 있으며, 다음과 같은 기능을 제공합니다:

1. **오디오 및 영상 파일 처리**
   - 오디오 또는 영상 파일을 전송하면, 해당 파일의 처리 결과를 JSON 형식으로 반환합니다.
   - 엔드포인트: `POST /api/transcription/`

2. **보고서 양식 코드 매핑**
   - 보고서 양식 코드(C001, C002, C003 등)를 입력하면, 해당 코드에 매핑된 보고서의 JSON 데이터 포맷을 반환합니다.
   - 엔드포인트: `GET /api/report-template/{code}`

3. **텍스트 보고서 생성**
   - 입력된 텍스트와 보고서 양식 코드를 기반으로 텍스트를 보고서 형식으로 변환하여 JSON 결과를 반환합니다.
   - 엔드포인트: `POST /api/report/text`

4. **오디오/영상 파일 및 보고서 양식 코드 처리**
   - 오디오 또는 영상 파일과 보고서 양식 코드를 함께 전송하면, 해당 정보를 기반으로 생성된 보고서 결과를 JSON 형식으로 반환합니다.
   - 엔드포인트: `POST /api/report/audio`

## 시작하기

### 사전 요구사항

- Docker 및 Docker Compose
- OpenAI API 키

### 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 다음과 같이 설정합니다:

```
# 애플리케이션 설정
APP_NAME=sttService
DEBUG=True
SECRET_KEY=your_secret_key_here
API_PREFIX=/api

# 데이터베이스 설정
DB_HOST=postgres
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=stt_db

# OpenAI API 설정
OPENAI_API_KEY=your_openai_api_key_here
```

### Docker Compose로 실행

```bash
docker-compose up -d
```

### 로컬에서 실행

1. PostgreSQL 서버 실행
2. 필요한 패키지 설치:
   ```bash
   pip install -r requirements.txt
   ```
3. 실행 스크립트 실행:
   ```bash
   python run.py
   ```

## API 문서

API 문서는 애플리케이션이 실행된 후 다음 URL에서 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## 프로젝트 구조

```
sttService/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── transcription.py
│   │   │   ├── report_template.py
│   │   │   └── report.py
│   │   ├── api.py
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py
│   │   └── __init__.py
│   ├── db/
│   │   ├── base.py
│   │   ├── create_tables.py
│   │   ├── init_data.py
│   │   └── __init__.py
│   ├── models/
│   │   ├── transcription.py
│   │   ├── schemas.py
│   │   └── __init__.py
│   ├── services/
│   │   ├── transcription_service.py
│   │   ├── report_service.py
│   │   └── __init__.py
│   ├── main.py
│   └── __init__.py
├── docker/
├── .env
├── docker-compose.yml
├── Dockerfile
├── README.md
├── requirements.txt
└── run.py
```

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여

1. 이 저장소를 포크합니다.
2. 새 브랜치를 생성합니다: `git checkout -b my-new-feature`
3. 변경 사항을 커밋합니다: `git commit -am 'Add some feature'`
4. 브랜치에 푸시합니다: `git push origin my-new-feature`
5. Pull Request를 제출합니다.

---
