# 🧠 mindLog: 청소년 정신건강 AI 상담 챗봇

### 🏆 GitHub 활동 통계 (조직 기준)
![Yeongmin's GitHub Stats](https://github-readme-stats.vercel.app/api?username=black4305&show_icons=true)
![Top Langs](https://github-readme-stats.vercel.app/api/top-langs/?username=black4305&layout=compact)
![Trophy](https://github-profile-trophy.vercel.app/?username=black4305&theme=gruvbox&column=6)

--

### 🧰 사용 기술 (Skills)

#### 💻 언어 & 프레임워크
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=Python&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=JavaScript&logoColor=black)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=HTML5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=CSS3&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=Flask&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=PyTorch&logoColor=white)
![HuggingFace](https://img.shields.io/badge/HuggingFace-FFB000?style=flat-square&logo=huggingface&logoColor=black)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=flat-square&logo=jsonwebtokens&logoColor=white)

#### 📊 데이터 사이언스
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)

#### 🗃️ 데이터베이스
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=MySQL&logoColor=white)

---

### 🛠️ 개발 도구

#### 🧑‍💻 IDE & 환경
![VSCode](https://img.shields.io/badge/VS%20Code-007ACC?style=flat-square&logo=visual-studio-code&logoColor=white)
![Cursor](https://img.shields.io/badge/Cursor-333333?style=flat-square&logo=cursor&logoColor=white)
![Google Colab](https://img.shields.io/badge/Google%20Colab-F9AB00?style=flat-square&logo=google-colab&logoColor=black)
![Anaconda](https://img.shields.io/badge/Anaconda-42B029?style=flat-square&logo=anaconda&logoColor=white)

#### ☁️ 협업 & 버전관리
![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)
![Google Drive](https://img.shields.io/badge/Google%20Drive-4285F4?style=flat-square&logo=google-drive&logoColor=white)

--

## 🧩 프로젝트 소개

> **koBERT와 GPT-3.5 Turbo 기반의 청소년 우울증 감지 및 AI 상담 챗봇**  
> 청소년 정신건강 문제를 조기에 발견하고, 접근성을 높이기 위한 AI 기반 챗봇 서비스입니다.

## ✅ 프로젝트 배경

청소년 정신건강 문제는 점점 심각해지고 있으나,  
기존 오프라인 위주 서비스는 다음과 같은 한계가 있습니다:

- 익명성 부족으로 인한 이용 꺼림
- 시간·공간적 제약
- 초기 이상 신호 포착의 어려움

**mindLog**는 이러한 한계를 해결하고,  
AI를 활용한 조기 개입과 감정 모니터링이 가능한 새로운 상담 경험을 제공합니다.

--

## 🎯 주요 기능

- 🤖 **GPT-3.5 기반 AI 상담**: 자연스러운 대화 흐름 제공
- 🧠 **koBERT 기반 우울증 감지 모델**: 감정 상태 실시간 분석
- 🚨 **위기 개입 시스템**: 위험 징후 감지 시 즉시 알림

---

## ⚙️ 기술 스택

### 🔍 AI & 모델링
- **koBERT** – 한국어 특화 우울증 감지
- **GPT-3.5 Turbo (OpenAI API)** – 챗봇 대화 생성
- **Hugging Face Transformers** – 사전학습 모델 활용
- **scikit-learn**, **Pandas**, **NumPy** – 데이터 분석 및 평가

### 🖥️ 백엔드
- **Flask** – REST API 서버
- **PyTorch** – 딥러닝 프레임워크
- **MySQL** – 사용자/상담 DB
- **JWT** – 인증 토큰 시스템

### 💻 프론트엔드
- **HTML / CSS / JavaScript** – 챗봇 UI 구현

### 🧰 개발환경 & 툴
- IDE: **VSCode**, **Cursor**, **Google Colab**
- 협업: **GitHub**, **Google Drive**
- 외부 API: **OpenAI**, **Google Maps API**

---

## 👥 팀 구성 (총 4명, 개발 기간: 04.03 ~ 05.14)

| 이름     | 역할             | 담당 업무 |
|----------|------------------|------------|
| 전대원   | Backend 개발     | Flask 서버, DB 구축, API 연동 |
| 장영민   | AI/모델링        | koBERT 미세조정, 감정 분석 모델 개발 |
| 주현빈   | Frontend 개발    | 챗봇 UI 구현, 사용자 인터페이스 개발 |
| 황상제   | Backend 개발     | GPT API 연동, 인증 및 시스템 설계 |

---

## 🚀 실행 방법

```bash
# 프로젝트 클론
git clone https://github.com/2025-SMHRD-IS-CLOUD-2/mindLog.git
cd mindLog

# 가상환경 설정 (선택)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 실행
python app.py
