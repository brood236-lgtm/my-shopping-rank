import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import re
from collections import Counter

# 페이지 설정 (터미널 스타일)
st.set_page_config(page_title="AI Ranking Tracker", layout="wide")
st.markdown("""
    <style>
    body, .stApp { background-color: #000000; color: #00FF00; font-family: 'Courier New', Courier, monospace; }
    .stTextInput>div>div>input { background-color: #111111; color: #00FF00; border: 1px solid #00FF00; }
    .stButton>button { background-color: #00FF00; color: #000000; font-weight: bold; border-radius: 5px; }
    .stButton>button:hover { background-color: #00CC00; color: #000000; }
    .my-mall { color: #FF4136; font-weight: bold; } /* 내 쇼핑몰 빨간색 강조 */
    .comp-mall { color: #FFFFFF; } /* 경쟁사 흰색 강조 */
    h1, h2, h3, h4 { color: #00FF00 !important; }
    hr { border-top: 1px dashed #00FF00; }
    .insight-box { border: 1px solid #00FF00; padding: 10px; margin-top: 10px; background-color: #0a0a0a; }
    </style>
""", unsafe_allow_html=True)

# 설정값
MY_MALLS = ['삼성공식파트너 쇼마젠시', '삼성파트너 쇼마젠시']
COMP_MALLS = ['삼성공식파트너 형연테크', '삼성공식파트너 dmac', '삼성공식파트너 올인포케이']
STANDARD_KEYWORDS = ['외장하드', '갤럭시워치7', '갤럭시워치8', '갤럭시핏3','보조배터리','갤럭시S26','탭s11 보호필름']
# AI 추천 유도를 위한 대화형 프롬프트 추가
AI_PROMPTS = ['가벼운 삼성 외장하드 추천해줘', '부모님 선물용 갤럭시워치 추천', '가성비 운동용 스마트워치','기내 반입 가능한 고속충전 보조배터리']

def get_kst_time():
    tz = pytz.timezone('Asia/Seoul')
    return datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

def extract_keywords(title):
    """상품명에서 주요 특징(단어) 추출하여 리스트로 반환"""
    words = re.findall(r'[가-힣a-zA-Z0-9]+', title)
    # 불용어(의미 없는 단어) 제외
    stopwords = ['삼성', '정품', '공식', '파트너', '무료배송']
    return [w for w in words if w not in stopwords and len(w) > 1]

# --- [ 1. API 설정값 입력 ] ---
NAVER_CLIENT_ID = "z3Guexy_a5AiWXIDub2e"
NAVER_CLIENT_SECRET = "adgqyvVjXu"


# --- [ 2. 네이버 API 전용 검색 함수 ] ---
import requests
import re
import streamlit as st

# (이전 코드의 extract_keywords 등은 그대로 둡니다)

# --- [ 이 부분을 기존 코드 대신 통째로 붙여넣으세요 ] ---
def search_naver_shopping(keyword, max_rank=40):
    url = "https://openapi.naver.com/v1/search/shop.json"
    headers = {
        "X-Naver-Client-Id": "여기에_발급받은_ID_입력",
        "X-Naver-Client-Secret": "여기에_발급받은_Secret_입력"
    }
    params = {
        "query": keyword,
        "display": max_rank,
        "start": 1,
        "sort": "sim"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            
            results = []
            all_tags = []
            
            for idx, item in enumerate(items, 1):
                # 불필요한 HTML 태그 제거
                title = re.sub(r'<[^>]*>', '', item['title'])
                mall = item['mallName']
                
                if idx <= 5:
                    all_tags.extend(extract_keywords(title))
                    
                results.append({'rank': idx, 'title': title, 'mall': mall})
            
            return results, all_tags
        else:
            st.error(f"API 오류: {response.status_code}")
            return [], []
            
    except Exception as e:
        st.error(f"연결 오류: {e}")
        return [], []
# --------------------------------------------------------

st.title("🤖 스토어 AI 랭킹 & 인사이트 트래커 (Terminal Ver.)")
st.text(f"System Time (KST): {get_kst_time()}\nTarget: 쇼마젠시 vs 경쟁사 (형연테크, dmac, 올인포케이)")

tab1, tab2 = st.tabs(["일반 키워드 랭킹 (Top 40)", "AI 에이전트 프롬프트 분석 (Top 5)"])

# 결과 저장을 위한 텍스트 변수
report_text = f"[{get_kst_time()}] 랭킹 리포트\n\n"

with tab1:
    st.markdown("### [ Standard Keywords Tracking ]")
    if st.button("RUN STANDARD TRACKING"):
        with st.spinner("Tracking standard keywords..."):
            for kw in STANDARD_KEYWORDS:
                st.markdown(f"**> {kw}**")
                report_text += f"[{kw}]\n"
                
                results, _ = search_naver_shopping(kw, max_rank=40)
                found_count = 0
                
                for res in results:
                    mall = res['mall']
                    rank = res['rank']
                    title = res['title']
                    
                    if mall in MY_MALLS:
                        st.markdown(f"[{rank}위] <span class='my-mall'>{mall}</span> - {title}", unsafe_allow_html=True)
                        report_text += f"{rank}위: {mall} (내 쇼핑몰)\n"
                        found_count += 1
                    elif mall in COMP_MALLS:
                        st.markdown(f"[{rank}위] <span class='comp-mall'>{mall}</span> - {title}", unsafe_allow_html=True)
                        report_text += f"{rank}위: {mall} (경쟁사)\n"
                        found_count += 1
                
                if found_count == 0:
                    st.text("  No target malls found in Top 40.")
                st.markdown("<hr>", unsafe_allow_html=True)

with tab2:
    st.markdown("### [ AI Conversational Prompt Tracking ]")
    st.markdown("네이버 쇼핑 AI가 우선 노출시키는 상위 상품들의 특징(Keyword)을 역추적합니다.")
    
    if st.button("RUN AI PROMPT TRACKING"):
        with st.spinner("Analyzing AI Prompts..."):
            for prompt in AI_PROMPTS:
                st.markdown(f"**> Q: \"{prompt}\"**")
                
                results, tags = search_naver_shopping(prompt, max_rank=5)
                
                # 상위 노출 5개 리스트업
                for res in results[:5]:
                    mall = res['mall']
                    mall_style = "my-mall" if mall in MY_MALLS else ("comp-mall" if mall in COMP_MALLS else "")
                    
                    if mall_style:
                        st.markdown(f"- [{res['rank']}위] <span class='{mall_style}'>{mall}</span> : {res['title']}", unsafe_allow_html=True)
                    else:
                        st.text(f"- [{res['rank']}위] {mall} : {res['title']}")
                
                # AI 인사이트 도출 (공통 키워드 추출)
                if tags:
                    top_keywords = [word for word, count in Counter(tags).most_common(5)]
                    st.markdown("<div class='insight-box'>", unsafe_allow_html=True)
                    st.markdown("💡 **AI 랭킹 분석 인사이트 (상세페이지 적용 권장 키워드):**")
                    st.markdown(f"상위 노출 상품들은 공통적으로 **{', '.join(top_keywords)}** 등의 키워드를 강조하고 있습니다. 내 스토어의 상품명이나 속성 태그에 해당 단어들이 포함되어 있는지 확인하세요.")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("<hr>", unsafe_allow_html=True)

# 복사 전용 텍스트 에어리어 (코드 노출 없이 결과값만)
st.markdown("### [ Report Output ]")
st.text_area("Ctrl+C로 복사하여 보고용으로 사용하세요.", value=report_text, height=200)


try:
    # 프로그램이 끝까지 실행되었을 때 창이 닫히지 않게 함
    input("\n[작업 완료] 엔터를 누르면 창이 종료됩니다...")
except EOFError:
    # 환경에 따라 input이 작동하지 않을 경우를 대비
    pass
