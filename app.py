import streamlit as st
import google.generativeai as genai
import pandas as pd
import json

# 페이지 설정
st.set_page_config(
    page_title="Gemini Chatbot",
    page_icon="🤖",
    layout="centered"
)

# API 키 설정 확인 및 안내
with st.sidebar:
    if "gcp" not in st.secrets:
        st.error("🔐 API 키 설정이 필요합니다!")
        st.markdown("""
        ### ⚠️ Gemini API 키 설정 안내
        
        이 앱은 Google Gemini API를 사용하며, 실행을 위해 API 키 설정이 필요합니다.
        
        ### ✅ 설정 방법
        Streamlit Cloud의 **Secrets** 탭에 아래 형식으로 등록하세요:
        """)
        
        st.code("""[gcp]
gemini_api_key = "YOUR_GEMINI_API_KEY\"""", language="toml")
        
        st.warning("API 키는 절대로 소스 코드에 직접 포함하지 마세요!")

try:
    # Gemini API 설정
    genai.configure(api_key=st.secrets["gcp"]["gemini_api_key"])
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    st.error("🚫 API 키가 올바르게 설정되지 않았습니다.")
    st.stop()

# 메인 타이틀과 설명
st.title("🤖 T 유형을 위한 F 유형 대화 도우미 챗봇")
st.markdown("""
이 챗봇은 감정형(F) 친구들과의 소통이 어려운 사고형(T)을 위한 맞춤형 도우미입니다.  
아래 탭에서 필요한 기능을 선택하세요!
""")

# 구분선
st.divider()

# 세션 상태 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "tone_history" not in st.session_state:
    st.session_state.tone_history = []
if "praise_history" not in st.session_state:
    st.session_state.praise_history = []

# 탭 생성
tab_chat, tab_tone, tab_praise = st.tabs(["💬 일반 챗봇", "🧪 어투·톤 체크", "🌷 칭찬/공감 생성"])

# 일반 챗봇 탭
with tab_chat:
    st.header("💬 일반 챗봇")
    st.markdown("""
    Gemini와 자유롭게 대화하면서 다양한 상황에 대한 조언을 받아보세요.
    """)
    
    # 채팅 기록 표시
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # 사용자 입력
    chat_input = st.chat_input("자유롭게 대화를 시작해보세요...")
    
    if chat_input:
        # 사용자 메시지 표시
        with st.chat_message("user"):
            st.write(chat_input)
        
        # 사용자 메시지 저장
        st.session_state.chat_history.append({"role": "user", "content": chat_input})
        
        try:
            # Gemini 모델에 메시지 전송
            response = model.generate_content(chat_input)
            
            # 모델 응답 표시
            with st.chat_message("assistant"):
                st.write(response.text)
            
            # 모델 응답 저장
            st.session_state.chat_history.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")

# 어투·톤 체크 탭
with tab_tone:
    st.header("🧪 어투·톤 체크")
    st.markdown("""
    ### 🎯 사용법
    아래 입력창에 '상대방에게 보내려는 메시지'를 입력하세요.  
    챗봇이 어투와 감정 톤을 분석하여 등급 및 피드백을 제공합니다.
    
    **예시 메시지:**
    > 너 왜 그랬어?
    
    > 조금 서운했지만, 다음엔 더 잘 얘기해보자 😊
    """)
    
    # 사용자 입력
    tone_input = st.text_area(
        "분석할 문장을 입력하세요",
        height=100,
        placeholder="예: 지금 바로 이것 좀 해주세요.",
        value="조금 서운했지만, 다음엔 더 잘 얘기해보자 😊"  # 기본 예시 문장
    )
    analyze_button = st.button("분석하기", type="primary")
    
    if analyze_button and tone_input:
        try:
            with st.spinner("문장을 분석하고 있습니다..."):
                # 분석 프롬프트 구성
                prompt = f"""당신은 JSON 응답만 제공하는 분석 시스템입니다.
                입력된 문장의 어투와 감정 톤을 분석하여 정확한 JSON 형식으로만 응답하세요.

                분석할 문장: "{tone_input}"

                아래 형식의 JSON으로만 응답하세요:
                {{
                    "emotional_tone": {{
                        "rating": "분석된 감정",
                        "reason": "평가 이유"
                    }},
                    "empathy_possibility": {{
                        "rating": "높음/보통/낮음",
                        "reason": "평가 이유"
                    }},
                    "tone": {{
                        "rating": "분석된 어투",
                        "reason": "평가 이유"
                    }},
                    "summary": "전체 분석을 한 문장으로 요약"
                }}"""

                response = model.generate_content(prompt, generation_config={
                    "temperature": 0.3,
                    "top_p": 0.8,
                    "top_k": 40
                })
                
                try:
                    # 응답 전처리
                    cleaned_response = response.text.strip()
                    # 응답에서 JSON 부분만 추출
                    if "```json" in cleaned_response:
                        cleaned_response = cleaned_response.split("```json")[1].split("```")[0].strip()
                    elif "```" in cleaned_response:
                        cleaned_response = cleaned_response.split("```")[1].strip()
                    
                    analysis = json.loads(cleaned_response)
                    
                    df = pd.DataFrame({
                        "분석 항목": ["감정 톤", "공감 가능성", "어투"],
                        "평가": [
                            analysis["emotional_tone"]["rating"],
                            analysis["empathy_possibility"]["rating"],
                            analysis["tone"]["rating"]
                        ],
                        "평가 이유": [
                            analysis["emotional_tone"]["reason"],
                            analysis["empathy_possibility"]["reason"],
                            analysis["tone"]["reason"]
                        ]
                    })
                    
                    st.table(df)
                    st.success(analysis["summary"])
                    
                except json.JSONDecodeError as e:
                    st.error(f"응답 형식이 올바르지 않습니다. 다시 시도해주세요. 오류: {str(e)}")
                    st.code(cleaned_response, language="json")
                    
        except Exception as e:
            st.error(f"분석 중 오류가 발생했습니다: {str(e)}")

# 칭찬/공감 생성 탭
with tab_praise:
    st.header("🌷 칭찬/공감 생성기")
    st.markdown("""
    ### 💡 사용법
    상대방이 보낸 말을 입력하면, 해당 문장에 적절한 공감 또는 칭찬 문장을 제안합니다.
    
    **예시 메시지:**
    > 오늘 진짜 힘들었어.
    
    > 네가 그랬다니 속상했겠다.
    """)
    
    # 사용자 입력
    praise_input = st.text_area(
        "상대방의 메시지나 상황을 입력하세요",
        height=100,
        placeholder="예: 오늘 발표 준비하느라 밤을 새웠어요.",
        value="오늘 진짜 힘들었어."  # 기본 예시 문장
    )
    generate_button = st.button("✨ 메시지 생성하기", type="primary")
    
    if generate_button and praise_input:
        try:
            with st.spinner("따뜻한 메시지를 생성하고 있습니다..."):
                prompt = f"""당신은 JSON 응답만 제공하는 메시지 생성 시스템입니다.
                입력된 메시지에 대한 칭찬과 공감 메시지를 생성하여 정확한 JSON 형식으로만 응답하세요.

                입력 메시지: "{praise_input}"

                아래 형식의 JSON으로만 응답하세요:
                {{
                    "praise": "칭찬 메시지 (1-2줄)",
                    "empathy": "공감 메시지 (1-2줄)"
                }}

                규칙:
                1. JSON 형식만 응답하세요
                2. 자연스러운 대화체로 작성하세요
                3. 다른 설명이나 텍스트를 포함하지 마세요"""

                response = model.generate_content(prompt, generation_config={
                    "temperature": 0.3,
                    "top_p": 0.8,
                    "top_k": 40
                })
                
                try:
                    # 응답 전처리
                    cleaned_response = response.text.strip()
                    # 응답에서 JSON 부분만 추출
                    if "```json" in cleaned_response:
                        cleaned_response = cleaned_response.split("```json")[1].split("```")[0].strip()
                    elif "```" in cleaned_response:
                        cleaned_response = cleaned_response.split("```")[1].strip()
                    
                    messages = json.loads(cleaned_response)
                    
                    st.divider()
                    st.success(f"💖 {messages['praise']}")
                    st.info(f"🌿 {messages['empathy']}")
                    
                except json.JSONDecodeError as e:
                    st.error(f"응답 형식이 올바르지 않습니다. 다시 시도해주세요. 오류: {str(e)}")
                    st.code(cleaned_response, language="json")
                    
        except Exception as e:
            st.error(f"메시지 생성 중 오류가 발생했습니다: {str(e)}")
