# HONEST-OCEAN 백엔드

부산소프트웨어마이스터고등학교 오션 해커톤 프로젝트.
이 프로젝트는 "Honest Ocean"의 백엔드 서비스로, 어종 식별, 시장가 분석, 금어기 및 금지체장 확인 기능을 제공합니다.

## 📚 API 문서

**[Apidog 문서 보러가기](https://5vs02l3vq6.apidog.io/)**

## 🚀 주요 기능

*   **AI 기반 어종 분석**: Google Gemini 또는 OpenAI GPT-4o를 활용하여 이미지에서 어종을 자동으로 식별합니다.
*   **과학적 무게 추정**: 어종별 성장 상수($W = aL^b$)를 사용하여 측정된 길이를 기반으로 예상 무게를 계산합니다.
*   **실시간 시세 정보**: **인어교주해적단(The Pirates)** API를 통해 실시간 수산물 소매 가격을 조회합니다.
*   **금어기/금지체장 확인**: 해양수산부 데이터를 기반으로 낚시 금지 기간(금어기) 및 금지 체장에 해당하는지 자동으로 판별합니다.
*   **상인 기록 관리**: 상인이 업로드한 조업 기록과 이미지를 **Supabase Storage**와 **PostgreSQL**에 안전하게 저장합니다.

## 🛠️ 기술 스택

*   **프레임워크**: FastAPI (Python)
*   **데이터베이스**: PostgreSQL (via Supabase)
*   **스토리지**: Supabase Storage
*   **AI 모델**: Google Gemini 2.0 / OpenAI GPT-4o
*   **배포**: Uvicorn / Docker (Optional)

## ⚙️ 설정 방법

### 요구 사항 (Prerequisites)
*   Python 3.9 이상
*   PostgreSQL 데이터베이스
*   Supabase 프로젝트

### 환경 변수 설정 (.env)
프로젝트 루트 경로에 `.env` 파일을 생성하고 아래 내용을 입력하세요:

```bash
# AI 모델 키 (둘 중 하나 이상 필수)
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key

# 데이터베이스
DATABASE_URL=postgresql://user:password@host:port/dbname

# Supabase 설정
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_BUCKET_NAME=hittingbalance

# 참고: OPEN_API_SERVICE_KEY (공공데이터포털)는 더 이상 시세 조회에 사용되지 않음
```

### 설치 (Installation)

```bash
# 가상 환경 생성
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 서버 실행 (Run Server)

```bash
uvicorn app.main:app --reload
```

API 서버는 `http://127.0.0.1:8000`에서 실행됩니다.
Swagger UI 문서: `http://127.0.0.1:8000/docs`

## 📝 API 엔드포인트

### 1. 어종 분석 (`POST /api/v1/fish/analyze`)
물고기 사진을 업로드하여 다음 정보를 분석합니다:
*   어종 이름 (학명 및 한국어 명칭)
*   예상 시장 가격 (실시간 시세 반영)
*   예상 무게 (길이 입력 시)
*   금지 여부 (`currentlyForbidden`: true/false)

### 2. 상인 기록 관리
*   `POST /api/v1/merchant/record`: 물고기 사진과 정보를 업로드하여 저장합니다. (이미지는 Supabase에 저장)
*   `GET /api/v1/merchant/records?id={id}`: 특정 기록의 상세 정보(이미지 URL 포함)를 조회합니다.