# T유형을 위한 F유형 대화 도우미 챗봇 🤖

Gemini API를 활용한 감정 소통 도우미 챗봇입니다. MBTI T유형의 사용자가 F유형과의 소통을 더 원활하게 할 수 있도록 도와주는 것이 목적입니다.

## 주요 기능 🌟

1. 일반 챗봇 대화
2. 어투/톤 체크 및 피드백
3. 상황별 칭찬/공감 메시지 생성

## 로컬 실행 방법 💻

1. 저장소 클론
```bash
git clone https://github.com/[your-username]/gemini_chatbot.git
cd gemini_chatbot
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 패키지 설치
```bash
pip install -r requirements.txt
```

4. `.streamlit/secrets.toml` 파일 생성 및 API 키 설정
```toml
[gcp]
gemini_api_key = "YOUR_API_KEY"
```

5. 애플리케이션 실행
```bash
streamlit run app.py
```

## Streamlit Cloud 배포 방법 🚀

1. [Streamlit Cloud](https://streamlit.io/cloud)에 접속하여 로그인

2. "New app" 버튼 클릭 후 GitHub 저장소 연결

3. Streamlit Cloud의 App Settings > Secrets 에서 다음 내용 추가:
```toml
[gcp]
gemini_api_key = "YOUR_API_KEY"
```

4. "Deploy!" 버튼을 클릭하여 배포 완료

## 주의사항 ⚠️

- API 키는 절대로 GitHub에 커밋하지 마세요.
- `.streamlit/secrets.toml` 파일은 로컬 개발용으로만 사용하세요.
- Streamlit Cloud에서는 반드시 Secrets 관리 기능을 통해 API 키를 설정하세요. 
