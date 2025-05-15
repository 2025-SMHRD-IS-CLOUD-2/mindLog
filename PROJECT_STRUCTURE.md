# 🗂️ 프로젝트 구조 설명 (mindLog)

이 문서는 `mindLog` 프로젝트의 전체 폴더 및 파일 구조와 각 구성요소의 역할을 설명합니다. 주니어 개발자도 쉽게 이해할 수 있도록 계층적으로 안내합니다.

---

```
mindLog/
├── app/
│   ├── ai/
│   │   ├── models/
│   │   │   └── depression/
│   │   │       └── model/                     # 우울증 감지 모델 관련 파일(토크나이저, 설정 등)
│   │   ├── test/                              # AI/모델 관련 테스트 코드
│   │   ├── sentiment.py                       # 감정 분석 관련 코드
│   │   ├── services.py                        # AI 서비스 로직
│   │   ├── chatbot.py                         # 챗봇 엔진 및 대화 처리
│   │   └── depression_model.py                # 우울증 감지 모델 로직
│   ├── models/
│   │   └── users.py                           # 사용자 모델(Flask-Login 등)
│   ├── routes/
│   │   ├── auth.py                            # 인증/회원가입/로그인 라우트
│   │   ├── chatbot.py                         # 챗봇 관련 라우트
│   │   ├── counseling.py                      # 상담 예약/센터 관련 라우트
│   │   ├── diagnosis.py                       # 우울증 진단/설문 라우트
│   │   ├── main.py                            # 메인 페이지 및 공통 라우트
│   │   └── __init__.py                        # 라우트 블루프린트 등록
│   ├── static/
│   │   ├── assets/
│   │   │   ├── icons/                         # SVG 등 아이콘 파일
│   │   │   │   ├── building.svg               # 건물 아이콘
│   │   │   │   ├── calendar.svg               # 달력 아이콘
│   │   │   │   ├── chatbot.svg                # 챗봇 아이콘
│   │   │   │   ├── diagnosis.svg              # 진단 아이콘
│   │   │   │   └── notification.svg           # 알림 아이콘
│   │   │   ├── mindbridge_secure_logo.png     # 로고 이미지
│   │   │   └── .DS_Store                     # macOS 시스템 파일
│   │   ├── css/
│   │   │   ├── main.css                       # 메인 스타일
│   │   │   ├── schedule.css                   # 일정 관련 스타일
│   │   │   ├── survey.css                     # 설문 스타일
│   │   │   ├── common.css                     # 공통 스타일
│   │   │   ├── counseling.css                 # 상담 스타일
│   │   │   ├── delete.css                     # 회원탈퇴 스타일
│   │   │   ├── diagnosis.css                  # 진단 스타일
│   │   │   ├── findpw.css                     # 비밀번호 찾기 스타일
│   │   │   ├── index.css                      # 인덱스 페이지 스타일
│   │   │   ├── join.css                       # 회원가입 스타일
│   │   │   ├── login.css                      # 로그인 스타일
│   │   │   ├── UI.css                         # UI 공통 스타일
│   │   │   ├── appointment.css                # 예약 스타일
│   │   │   └── chatbot.css                    # 챗봇 스타일
│   │   ├── js/
│   │   │   ├── join.js                        # 회원가입 JS
│   │   │   ├── login.js                       # 로그인 JS
│   │   │   ├── schedule.js                    # 일정 관련 JS
│   │   │   ├── score(CES-D).js                # CES-D 점수 계산 JS
│   │   │   ├── score(CESD-10-D).js            # CESD-10-D 점수 계산 JS
│   │   │   ├── score(PHQ-9).js                # PHQ-9 점수 계산 JS
│   │   │   ├── auth.js                        # 인증 관련 JS
│   │   │   ├── chatbot.js                     # 챗봇 관련 JS
│   │   │   ├── counseling.js                  # 상담 관련 JS
│   │   │   ├── delete.js                      # 회원탈퇴 JS
│   │   │   └── diagnosis.js                   # 진단 관련 JS
│   │   └── .DS_Store                          # macOS 시스템 파일
│   ├── templates/
│   │   ├── auth/                             # 인증 관련 HTML 템플릿
│   │   │   ├── delete.html                   # 회원탈퇴 페이지
│   │   │   ├── find_password.html            # 비밀번호 찾기 페이지
│   │   │   ├── join.html                     # 회원가입 페이지
│   │   │   ├── login.html                    # 로그인 페이지
│   │   │   └── update.html                   # 회원정보 수정 페이지
│   │   ├── chatbot/                          # 챗봇 UI 템플릿
│   │   │   └── chat.html                     # 챗봇 대화 페이지
│   │   ├── counseling/                       # 상담/예약 관련 템플릿
│   │   │   ├── appointment.html              # 상담 예약 페이지
│   │   │   ├── cancel.html                   # 예약 취소 페이지
│   │   │   ├── center_detail.html            # 상담센터 상세 페이지
│   │   │   ├── centers.html                  # 상담센터 목록 페이지
│   │   │   ├── schedule.html                 # 예약 일정 페이지
│   │   │   └── success.html                  # 예약 성공 페이지
│   │   ├── diagnosis/                        # 진단/설문 템플릿
│   │   │   ├── index.html                    # 진단 설문 메인
│   │   │   └── results.html                  # 진단 결과 페이지
│   │   ├── errors/                           # 에러 페이지 템플릿(404, 500 등)
│   │   │   ├── 404.html                      # 404 에러 페이지
│   │   │   └── 500.html                      # 500 에러 페이지
│   │   ├── base.html                         # 공통 레이아웃 템플릿
│   │   ├── main.html                         # 메인 페이지 템플릿
│   │   ├── _header.html                      # 헤더 공통 템플릿
│   │   └── .DS_Store                         # macOS 시스템 파일
│   ├── utils/
│   │   └── db.py                             # DB 연결 및 유틸리티 함수
│   └── __init__.py                           # Flask 앱 생성 및 설정
├── auth.py                                   # 인증 관련 전역 코드
├── config.py                                 # 환경설정 및 Flask 설정
├── requirements.txt                          # 파이썬 의존성 목록
├── run.py                                    # 앱 실행 진입점
├── README.md                                 # 프로젝트 소개 및 실행법
└── PROJECT_STRUCTURE.md                      # (본 문서) 프로젝트 구조 설명
```

---

## 주요 폴더/파일 설명

- **app/**: 실제 서비스 코드가 위치하는 최상위 폴더입니다.
  - **ai/**: AI 모델, 챗봇, 감정 분석 등 인공지능 관련 코드와 모델 파일이 위치합니다.
  - **models/**: 데이터베이스 ORM 모델(예: 사용자 모델 등)이 정의됩니다.
  - **routes/**: Flask의 라우트(페이지/기능별 URL 처리)가 모여 있습니다. 각 기능별로 파일이 분리되어 있습니다.
  - **static/**: CSS, JS, 이미지 등 정적 파일이 위치합니다. 프론트엔드 리소스 관리에 사용됩니다.
  - **templates/**: Jinja2 기반 HTML 템플릿 파일이 위치합니다. 페이지별로 폴더가 분리되어 있습니다.
  - **utils/**: 데이터베이스 연결 등 공통 유틸리티 함수가 위치합니다.
  - **__init__.py**: Flask 앱 생성, 확장기능 초기화, 블루프린트 등록 등 앱의 진입점 역할을 합니다.

- **auth.py**: 인증 관련 전역 코드(토큰, 세션 등)입니다.
- **config.py**: 환경변수, DB, Flask 등 전역 설정을 관리합니다.
- **requirements.txt**: 프로젝트에 필요한 파이썬 패키지 목록입니다.
- **run.py**: Flask 앱 실행을 위한 진입점 스크립트입니다.
- **README.md**: 프로젝트 소개, 실행 방법, 팀 정보 등이 담긴 문서입니다.
- **PROJECT_STRUCTURE.md**: (본 문서) 전체 폴더/파일 구조와 역할을 설명합니다.

---

## 참고
- 각 폴더/파일의 상세한 역할은 주석 및 README를 참고하세요.
- Flask, Jinja2, PyTorch, HuggingFace 등 다양한 기술이 통합된 구조입니다.
- 궁금한 점은 팀원 또는 시니어 개발자에게 문의하세요. 