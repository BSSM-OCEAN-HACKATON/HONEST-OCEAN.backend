# 🐟 Backend System Architecture Summary

현재 백엔드 시스템(FastAPI)의 구조와 핵심 기능을 요약한 문서입니다.

## 1. 🏗 System Architecture (시스템 아키텍처)

*   **Framework**: FastAPI (Python) - 비동기 처리 및 고성능 API.
*   **Database**: PostgreSQL (Supabase) - 영구 데이터 저장.
*   **Storage**: Supabase Storage - 이미지 파일 호스팅.
*   **AI Models**:
    *   **Main**: OpenAI GPT-4o (높은 정확도).
    *   **Fast/Backup**: Google Gemini 1.5 Flash (빠른 속도).
*   **Deployment**: Render (호환성 최적화 완료).

---

## 2. 🧩 Key Modules & Services (핵심 모듈 및 서비스)

백엔드 로직은 `app/services/` 디렉토리에 모듈화되어 있습니다.

### A. 🤖 Fish Analysis (`analysis_service.py`)
*   **역할**: 생선 이미지 분석.
*   **로직**:
    1.  이미지를 Base64로 인코딩하여 AI 모델(GPT-4o/Gemini)에 전송.
    2.  **어종(Scientific Name/Seafood Type)** 식별.
    3.  **과학적 무게 추정**: $W = a L^b$ 공식을 사용하여 길이(Length) 기반 무게 산출.

### B. 💰 Market Price (`market_price_service.py`)
*   **역할**: 실시간 싯가 조회.
*   **로직**:
    1.  **인어교주해적단(The Pirates) API** (`pub-api.tpirates.com`)를 연동.
    2.  식별된 어종명을 검색어로 사용하여 현재 평균 소매가(kg당)를 가져옵니다.

### C. ⚖️ Fish Yield Data (`fish_data.py`)
*   **역할**: 생선 수율(살코기 비율) 데이터 관리.
*   **로직**:
    *   광어(48%), 우럭(30%), 연어(65%) 등 주요 어종별 수율 상수 관리.
    *   `compare_fillet` 기능에서 실제 섭취 가능한 살코기 양(Fillet Weight) 계산에 사용.

### D. 🚫 Regulation Check (`regulation_service.py`)
*   **역할**: 금어기 및 금지체장 확인.
*   **로직**:
    *   현재 날짜 기준 금어기(Season) 해당 여부 체크.
    *   입력된 길이/무게 기준 금지 규격(Size Limit) 위반 여부 체크.
    *   위반 시 `currentlyForbidden: true` 반환.

### E. ☁️ Storage (`storage_service.py`)
*   **역할**: 이미지 파일 업로드.
*   **로직**: Supabase Storage 버킷에 이미지를 업로드하고 공개 URL(`publicUrl`)을 반환.

---

## 3. 🔌 API Endpoints (주요 기능)

### A. 생선 분석 (`/api/v1/fish`)
1.  **`POST /analyze` (단일 분석)**
    *   **입력**: 이미지 파일, 생선 길이(cm).
    *   **수행**: AI 분석 -> 싯가 조회 -> 무게 계산 -> 규제 확인.
    *   **출력**: 어종명, 예상 가격, 예상 무게, 금지 여부.

2.  **`POST /compare_fillet` (비교 분석)**
    *   **입력**: 두 개의 생선 이미지와 각각의 길이.
    *   **수행**:
        1.  두 생선을 각각 분석(AI + 무게 계산).
        2.  `fish_data`의 수율 상수를 곱해 **순수 살코기 무게(Fillet Weight)** 산출.
    *   **출력**:
        *   `maxFIsh`: 더 많은 살코기가 나오는 생선의 **Index (0 or 1)**.
        *   `portion`: 해당 생선의 살코기로 나올 수 있는 **n인분 수** (200g 기준).

### B. 상인 기록 (`/api/v1/merchant`)
1.  **`POST /record` (기록 저장)**
    *   **기능**: 분석된 데이터를 상인의 판매 기록으로 저장합니다.
    *   **특징**: 이미지는 Supabase에 업로드하고 URL만 DB에 저장. GPS 좌표 포함.
2.  **`GET /records` (목록 조회)**
    *   **기능**: 저장된 기록을 페이지네이션(Page/Size)하여 조회.
3.  **`GET /record` (상세 조회)**
    *   **기능**: ID(`recordId`)로 특정 기록의 상세 정보를 조회.

---

## 4. 💾 Database Schema (DB 구조)

*   **MerchantRecord 테이블**:
    *   `id`: Primary Key.
    *   `seafood_type`: 어종명.
    *   `estimated_weight`: AI 추정 무게.
    *   `merchant_weight`: 상인 실제 측정 무게.
    *   `market_price`: 당시 싯가.
    *   `image_filename`: 이미지 URL.
    *   `latitude`, `longitude`: 거래 위치.
    *   `created_at`: 생성 시간.
