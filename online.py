import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import time

# 1. 터미널 스타일 디자인 및 색상 설정
st.set_page_config(page_title="SHOPPING MONITOR TERMINAL", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .status-text { 
        font-family: 'Courier New', monospace; 
        line-height: 1.6; 
        padding: 15px;
        background-color: #1a1c23;
        border-radius: 8px;
        border-left: 5px solid #4b4b4b;
    }
    .my-item { color: #FF0000; font-weight: bold; }      /* 우리 상품: 빨간색 */
    .comp-item { color: #FFFFFF; }                      /* 경쟁사: 흰색 */
    .orig-item { color: #3d9dfd; }                      /* 원부: 파란색 유지 */
    .query-title { color: #FFD700; font-weight: bold; margin-top: 20px; font-size: 1.1em; } 
    </style>
""", unsafe_allow_html=True)

def get_naver_rank(target, client_id, client_secret):
    url = "https://openapi.naver.com/v1/search/shop.json"
    headers = {
        "X-Naver-Client-Id": client_id, 
        "X-Naver-Client-Secret": client_secret,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    params = {"query": target["query"], "display": 40, "start": 1, "sort": "sim"}
    try:
        response = requests.get(url, headers=headers, params=params)
        return response.json().get('items', []) if response.status_code == 200 else []
    except:
        return []

# 2. 보안 설정 (Secrets)
try:
    C_ID = st.secrets["NAVER_CLIENT_ID"]
    C_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
except:
    st.error("⚠️ Streamlit Cloud 설정(Secrets)을 확인해주세요.")
    st.stop()

MONITORING_TARGETS = [
    {"query": "외장하드", "my_mall": "삼성공식파트너 쇼마젠시", "target_mall": ["삼성공식파트너 형연테크"], "target_mids": ["53122848087","53123371823","52997593981","52997593980","52997593979","52997593978","52997593983","52997593982","53122848088","53122848089","53122848090","53122848091","53122848092","57251692420","57251692421"]},
    {"query": "갤럭시워치7", "my_mall": "삼성파트너 쇼마젠시", "target_mall": ["삼성공식파트너 dmac", "삼성공식파트너 올인포케이"], "target_mids": []},
    {"query": "갤럭시워치8", "my_mall": "삼성파트너 쇼마젠시", "target_mall": ["삼성공식파트너 dmac", "삼성공식파트너 올인포케이"], "target_mids": ["55668557960", "55727507152", "55727496884", "55668573794"]},
    {"query": "갤럭시핏3", "my_mall": "삼성파트너 쇼마젠시", "target_mall": ["삼성공식파트너 dmac", "삼성공식파트너 올인포케이"], "target_mids": []}
    {"query": "스마트태그2", "my_mall": "삼성파트너 쇼마젠시", "target_mall": [], "target_mids": []}
]

st.title("🖥️ SHOPPING MONITOR TERMINAL")

# 결과 텍스트를 저장할 세션 초기화
if 'report_text' not in st.session_state:
    st.session_state.report_text = ""

if st.button("RUN MONITORING"):
    # 한국 시간 계산
    kst_now = datetime.utcnow() + timedelta(hours=9)
    # 💡 텍스트 초기화 (이 변수에는 오직 '결과 글자'만 담습니다)
    temp_report = f"📊 쇼핑 순위 리포트 ({kst_now.strftime('%Y-%m-%d %H:%M:%S')})\n"
    temp_report += "=" * 40 + "\n"
    
    for target in MONITORING_TARGETS:
        query = target["query"]
        st.markdown(f"<div class='query-title'>🔎 현재 검색 중: [{query}]</div>", unsafe_allow_html=True)
        temp_report += f"\n🔎 [{query}]\n"
        
        items = get_naver_rank(target, C_ID, C_SECRET)
        found_in_query = False
        
        display_html = "<div class='status-text'>"
        
        for idx, item in enumerate(items):
            rank = idx + 1
            mall_name = item.get('mallName', '')
            title = item.get('title', '').replace('<b>', '').replace('</b>', '')
            product_id = item.get('productId', '')

            # 내 상품 (빨간색)
            if target["my_mall"] in mall_name:
                display_html += f"✅ <span class='my-item'>[내 상품] {rank:2d}위</span> | {title[:45]}...<br>"
                temp_report += f"✅ [내 상품] {rank}위 | {title[:40]}\n"
                found_in_query = True
            
            # 경쟁사 (흰색)
            for tm in target["target_mall"]:
                if tm in mall_name:
                    display_html += f"🚨 <span class='comp-item'>[경쟁사] {rank:2d}위</span> | {title[:45]}...<br>"
                    temp_report += f"🚨 [경쟁사] {rank}위 | {title[:40]}\n"
                    found_in_query = True
            
            # 원부 (파란색)
            if product_id in target["target_mids"]:
                display_html += f"🎯 <span class='orig-item'>[원 부] {rank:2d}위</span> | {title[:45]}...<br>"
                temp_report += f"🎯 [원 부] {rank}위 | {title[:40]}\n"
                found_in_query = True
        
        if not found_in_query:
            display_html += "<span style='color:#777;'>❌ 40위 내 검색 결과 없음</span><br>"
            temp_report += "❌ 40위 내 결과 없음\n"
        
        display_html += "</div>"
        st.markdown(display_html, unsafe_allow_html=True)
        time.sleep(0.2)
    
    # 조회가 끝나면 세션 상태에 저장
    st.session_state.report_text = temp_report
    st.success(f"✅ 조회가 완료되었습니다. 아래 리포트를 복사하세요.")

# 📋 텍스트 복사 영역 (버튼 클릭 여부와 관계없이 세션에 값이 있으면 표시)
if st.session_state.report_text:
    st.write("---")
    st.subheader("📋 리포트 복사")
    st.text_area(
        label="복사 전용창 (우측 상단 아이콘 클릭)",
        value=st.session_state.report_text,
        height=300,
        key="copy_area_final"
    )
