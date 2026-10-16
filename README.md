# AI 여행지 추천 챗봇 (trip_chatbot)

여행자 프로필을 입력하면 Google Gemini가 맞춤 여행지 3곳을 추천하고, 이어지는 질문에 답하는 Streamlit 챗봇입니다.

## 주요 기능

- **프로필 입력**: 나이, 성별, MBTI(선택), 1인 예산, 여행 스타일(관광·휴양·균형), 여행 기간, 관심사, 국내·해외 선호, 여행 시기, 추가 요구사항
- **맞춤 추천**: 여행지 TOP 3(소개, 추천 이유, 예상 비용, 베스트 시즌, 주요 명소·활동)와 맞춤 여행 팁, 주의사항 생성
- **후속 대화**: 이전 대화를 이어 받아 맛집, 교통, 숙소 등 추가 질문에 답변. 숙소·맛집·교통·다른 여행지 빠른 질문 버튼 제공
- **샘플 프로필**: 가족·커플·혼자 여행 프로필로 바로 시작
- **스트리밍 응답**: 답변을 생성되는 대로 표시

## 기술 스택

- Python, Streamlit
- Google Gemini API (`google-generativeai`, `gemini-2.5-flash`)

## 실행 방법

1. 패키지를 설치합니다.

   ```bash
   pip install -r requirements.txt
   ```

2. `.streamlit/secrets.toml`에 API 키를 넣습니다.

   ```toml
   GOOGLE_API_KEY = "your-api-key"
   ```

3. 앱을 실행합니다.

   ```bash
   streamlit run chatbot.py
   ```

GitHub Codespaces에서 열면 `.devcontainer` 설정에 따라 패키지 설치와 앱 실행(8501 포트)이 자동으로 진행됩니다.
