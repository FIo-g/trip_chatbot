import streamlit as st
import google.generativeai as genai

# 페이지 설정
st.set_page_config(
    page_title="AI 여행지 추천 챗봇",
    page_icon="✈️",
    layout="wide"
)

# 제목 및 설명
st.title("✈️ AI 여행지 추천 챗봇")
st.caption("당신에게 딱 맞는 여행지를 AI가 추천해드립니다!")

# API 키 설정
def configure_genai():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            return True
        else:
            st.error("❌ API 키가 설정되지 않았습니다. `.streamlit/secrets.toml` 파일에 GEMINI_API_KEY를 추가하세요.")
            st.info("""
            ### 설정 방법:
            1. `.streamlit/secrets.toml` 파일 생성
            2. 다음 내용 추가: `GEMINI_API_KEY = "your-api-key"`
            """)
            return False
    except Exception as e:
        st.error(f"❌ API 설정 오류: {str(e)}")
        return False

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None
if "recommendation_count" not in st.session_state:
    st.session_state.recommendation_count = 0

# MBTI 타입
MBTI_TYPES = [
    "모르겠음",
    "INTJ", "INTP", "ENTJ", "ENTP",
    "INFJ", "INFP", "ENFJ", "ENFP",
    "ISTJ", "ISFJ", "ESTJ", "ESFJ",
    "ISTP", "ISFP", "ESTP", "ESFP"
]

# 사이드바 - 사용자 정보 입력
with st.sidebar:
    st.header("👤 여행자 프로필")
    
    with st.form("user_profile_form"):
        st.subheader("기본 정보")
        age = st.slider("나이", 10, 80, 30)
        gender = st.radio("성별", ["남성", "여성", "기타"], horizontal=True)
        mbti = st.selectbox("MBTI (선택사항)", MBTI_TYPES)
        
        st.subheader("💰 예산")
        budget = st.select_slider(
            "예산 범위 (1인 기준)",
            options=["50만원 이하", "50-100만원", "100-200만원", "200-300만원", "300만원 이상"],
            value="100-200만원"
        )
        
        st.subheader("🏖️ 여행 스타일")
        travel_style = st.radio(
            "선호하는 여행 방식",
            ["관광 위주", "휴양 위주", "균형있게"],
            help="관광: 명소 방문, 체험 활동 / 휴양: 휴식, 힐링"
        )
        
        travel_duration = st.select_slider(
            "여행 기간",
            options=["1-2일", "3-4일", "5-7일", "1-2주", "2주 이상"],
            value="3-4일"
        )
        
        st.subheader("❤️ 관심사")
        interests = st.multiselect(
            "관심있는 것들 (복수 선택 가능)",
            ["음식/미식", "역사/문화", "자연/풍경", "쇼핑", "스포츠/액티비티", 
             "예술/박물관", "나이트라이프", "사진촬영", "현지체험", "축제/이벤트"],
            default=["음식/미식", "자연/풍경"]
        )
        
        st.subheader("🌍 여행 선호도")
        destination_type = st.radio(
            "선호 여행지",
            ["국내", "해외", "상관없음"],
            horizontal=True
        )
        
        season = st.selectbox(
            "여행 시기",
            ["봄 (3-5월)", "여름 (6-8월)", "가을 (9-11월)", "겨울 (12-2월)", "상관없음"]
        )
        
        st.subheader("✍️ 추가 정보")
        additional_info = st.text_area(
            "특별한 요구사항이나 고려사항",
            placeholder="예: 아이와 함께, 반려동물 동반, 휠체어 접근 가능, 채식주의자 등",
            height=100
        )
        
        submitted = st.form_submit_button("🎯 여행지 추천받기", type="primary", use_container_width=True)
        
        if submitted:
            if interests:
                st.session_state.user_profile = {
                    "age": age,
                    "gender": gender,
                    "mbti": mbti if mbti != "모르겠음" else None,
                    "budget": budget,
                    "travel_style": travel_style,
                    "duration": travel_duration,
                    "interests": interests,
                    "destination_type": destination_type,
                    "season": season,
                    "additional": additional_info
                }
                st.session_state.recommendation_count += 1
                st.success("✅ 프로필이 저장되었습니다!")
                st.session_state.messages.append({
                    "role": "system",
                    "content": "generate_recommendation"
                })
                st.rerun()
            else:
                st.error("최소 하나 이상의 관심사를 선택해주세요!")
    
    st.divider()
    
    # 초기화 버튼
    if st.button("🔄 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.session_state.recommendation_count = 0
        st.rerun()
    
    # 사용 팁
    with st.expander("💡 사용 팁"):
        st.markdown("""
        1. **정확한 정보 입력**: 더 자세한 정보를 입력할수록 맞춤형 추천을 받을 수 있습니다.
        2. **추가 질문**: 추천받은 여행지에 대해 궁금한 점을 자유롭게 물어보세요.
        3. **대체 추천**: 마음에 들지 않으면 다른 여행지를 요청하세요.
        """)

# 메인 영역
# 프로필 요약 표시
if st.session_state.user_profile:
    profile = st.session_state.user_profile
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("예산", profile['budget'])
    with col2:
        st.metric("여행 기간", profile['duration'])
    with col3:
        st.metric("여행 스타일", profile['travel_style'])
    
    st.info(f"🎯 관심사: {', '.join(profile['interests'])}")

# 대화 표시
st.subheader("💬 대화")

# 대화 내역 표시
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message("assistant"):
            st.write(message["content"])
    elif message["role"] == "system" and message["content"] == "generate_recommendation":
        # 여행지 추천 생성
        if configure_genai():
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                profile = st.session_state.user_profile
                
                # 추천 타입 결정
                if st.session_state.recommendation_count == 1:
                    recommendation_type = "처음"
                else:
                    recommendation_type = "대체"
                
                prompt = f"""
                당신은 전문 여행 컨설턴트입니다. 다음 프로필을 가진 여행자에게 {recommendation_type} 여행지를 추천해주세요.
                
                [여행자 프로필]
                • 나이: {profile['age']}세 {profile['gender']}
                {'• MBTI: ' + profile['mbti'] if profile['mbti'] else ''}
                • 예산: {profile['budget']} (1인 기준)
                • 여행 기간: {profile['duration']}
                • 여행 스타일: {profile['travel_style']}
                • 관심사: {', '.join(profile['interests'])}
                • 선호 지역: {profile['destination_type']}
                • 여행 시기: {profile['season']}
                {'• 특별 요구사항: ' + profile['additional'] if profile['additional'] else ''}
                
                다음 형식으로 3곳의 여행지를 추천해주세요:
                
                1. **추천 여행지 TOP 3**
                   각 여행지마다:
                   - 여행지명과 간단한 소개
                   - 추천 이유 (프로필과 연결)
                   - 예상 비용
                   - 베스트 시즌
                   - 주요 명소/활동 3가지
                
                2. **맞춤형 여행 팁**
                   - 이 프로필에 특별히 도움되는 팁 3가지
                
                3. **추가 고려사항**
                   - 주의사항이나 준비물
                
                친근하고 열정적인 톤으로 작성하되, 구체적이고 실용적인 정보를 제공해주세요.
                이모지를 적절히 사용해서 읽기 쉽게 만들어주세요.
                """
                
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    
                    # 스트리밍 시도
                    try:
                        response = model.generate_content(prompt, stream=True)
                        for chunk in response:
                            if chunk.text:
                                full_response += chunk.text
                                message_placeholder.markdown(full_response + "▌")
                        message_placeholder.markdown(full_response)
                    except:
                        # 스트리밍 실패시 일반 응답
                        response = model.generate_content(prompt)
                        full_response = response.text
                        message_placeholder.markdown(full_response)
                    
                    # 응답 저장
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": full_response
                    })
                    # system 메시지 제거
                    st.session_state.messages = [m for m in st.session_state.messages if not (m["role"] == "system")]
                    
            except Exception as e:
                st.error(f"추천 생성 중 오류가 발생했습니다: {str(e)}")

# 사용자 입력
if st.session_state.user_profile:
    user_input = st.chat_input("여행지에 대해 더 알고 싶은 것을 물어보세요... (예: 현지 맛집, 교통편, 숙소 추천 등)")
    
    if user_input:
        # 사용자 메시지 표시
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.write(user_input)
        
        # AI 응답 생성
        if configure_genai():
            try:
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                
                # 대화 히스토리 구성
                history = ""
                for msg in st.session_state.messages[-10:]:  # 최근 10개 메시지
                    if msg["role"] != "system":
                        history += f"{msg['role']}: {msg['content']}\n\n"
                
                profile = st.session_state.user_profile
                
                prompt = f"""
                당신은 전문 여행 컨설턴트입니다.
                
                [여행자 프로필]
                • 나이: {profile['age']}세 {profile['gender']}
                • 예산: {profile['budget']}
                • 관심사: {', '.join(profile['interests'])}
                • 여행 스타일: {profile['travel_style']}
                
                [이전 대화]
                {history}
                
                [사용자 질문]
                {user_input}
                
                위 정보를 바탕으로 친근하고 도움이 되는 답변을 제공해주세요.
                구체적인 정보와 실용적인 팁을 포함해주세요.
                """
                
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    
                    # 스트리밍 시도
                    try:
                        response = model.generate_content(prompt, stream=True)
                        for chunk in response:
                            if chunk.text:
                                full_response += chunk.text
                                message_placeholder.markdown(full_response + "▌")
                        message_placeholder.markdown(full_response)
                    except:
                        # 스트리밍 실패시 일반 응답
                        response = model.generate_content(prompt)
                        full_response = response.text
                        message_placeholder.markdown(full_response)
                    
                    # 응답 저장
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": full_response
                    })
                    
            except Exception as e:
                st.error(f"응답 생성 중 오류가 발생했습니다: {str(e)}")
                with st.chat_message("assistant"):
                    error_msg = "죄송합니다. 응답을 생성하는 중 오류가 발생했습니다. 다시 시도해주세요."
                    st.write(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

    # 빠른 질문 버튼들
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🏨 숙소 추천"):
            st.session_state.messages.append({"role": "user", "content": "추천한 여행지의 숙소를 추천해주세요. 가격대별로 알려주세요."})
            st.rerun()
    
    with col2:
        if st.button("🍜 맛집 정보"):
            st.session_state.messages.append({"role": "user", "content": "현지 맛집과 꼭 먹어봐야 할 음식을 추천해주세요."})
            st.rerun()
    
    with col3:
        if st.button("🚗 교통 정보"):
            st.session_state.messages.append({"role": "user", "content": "여행지까지 가는 방법과 현지 교통수단에 대해 알려주세요."})
            st.rerun()
    
    with col4:
        if st.button("🔄 다른 여행지"):
            st.session_state.recommendation_count += 1
            st.session_state.messages.append({"role": "system", "content": "generate_recommendation"})
            st.rerun()

else:
    st.info("👈 왼쪽 사이드바에서 여행자 정보를 입력하고 '여행지 추천받기' 버튼을 눌러주세요!")
    
    # 샘플 프로필 제공
    st.subheader("🎭 샘플 프로필로 시작하기")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👨‍👩‍👧‍👦 가족 여행", use_container_width=True):
            st.session_state.user_profile = {
                "age": 40,
                "gender": "남성",
                "mbti": "ISFJ",
                "budget": "200-300만원",
                "travel_style": "균형있게",
                "duration": "5-7일",
                "interests": ["음식/미식", "자연/풍경", "현지체험"],
                "destination_type": "해외",
                "season": "여름 (6-8월)",
                "additional": "초등학생 자녀 2명과 함께하는 가족여행"
            }
            st.session_state.recommendation_count += 1
            st.session_state.messages.append({"role": "system", "content": "generate_recommendation"})
            st.rerun()
    
    with col2:
        if st.button("👫 커플 여행", use_container_width=True):
            st.session_state.user_profile = {
                "age": 28,
                "gender": "여성",
                "mbti": "ENFP",
                "budget": "100-200만원",
                "travel_style": "휴양 위주",
                "duration": "3-4일",
                "interests": ["음식/미식", "사진촬영", "나이트라이프"],
                "destination_type": "해외",
                "season": "가을 (9-11월)",
                "additional": "연인과 함께하는 로맨틱한 여행"
            }
            st.session_state.recommendation_count += 1
            st.session_state.messages.append({"role": "system", "content": "generate_recommendation"})
            st.rerun()
    
    with col3:
        if st.button("🎒 혼자 여행", use_container_width=True):
            st.session_state.user_profile = {
                "age": 25,
                "gender": "남성",
                "mbti": "INTP",
                "budget": "50-100만원",
                "travel_style": "관광 위주",
                "duration": "1-2주",
                "interests": ["역사/문화", "예술/박물관", "현지체험"],
                "destination_type": "국내",
                "season": "봄 (3-5월)",
                "additional": "혼자서 천천히 둘러보는 여행"
            }
            st.session_state.recommendation_count += 1
            st.session_state.messages.append({"role": "system", "content": "generate_recommendation"})
            st.rerun()

# 푸터
st.divider()
st.caption("🤖 Powered by Gemini AI | 여행 정보는 참고용이며, 실제 상황과 다를 수 있습니다.")