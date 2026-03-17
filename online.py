import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# 1. 터미널 스타일 디자인 설정
st.set_page_config(page_title="Terminal Monitoring", layout="wide")
st.markdown("""
    <style>
    .reportview-container, .main { background: #0e1117; }
    .stCodeBlock, div[data-testid="stMarkdownContainer"] { color: #e0e0e0; font-family: 'Courier New', Courier, monospace; }
    h1, h2, h3 { color: #ffffff !important; }
    .stButton>button { background-color: #262730; color: white; border-radius: 5px; border: 1px solid #4b4b4b; }
    .status-text { font-family: 'Courier New', monospace; line-height: 1.6; }
    </style>
""", unsafe_allow_html=True)

def get_naver_rank(target, client_id, client_secret):
    url = "https://openapi.naver.com/v1/search/shop.json"
    headers = {
        "X-Naver-Client-Id": client_id, 
        "X-Naver-Client-Secret": client_secret,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    query = target["query"]
    my_mall = target["my_mall"]
    target_malls = target.get("target_mall", [])
    if isinstance(target_malls, str): target_malls = [target_malls]
    target_mids = target.get("target_mids", [])

    # 요청하신 대로 다시 40위까지로 설정
    params = {"query": query, "display": 40, "start": 1, "sort": "sim"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json().get('items', [])
    except:
        return []
    return []

# 2. 보안 설정: Secrets에서 값 가져오기 (사이드바 입력창 제거)
# st.secrets를 사용하면 코드에 직접 노출되지 않습니다.
try:
    C_ID = st.secrets["NAVER_CLIENT_ID"]
    C_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
except:
    st.error("⚠️ Streamlit Cloud 설정(Secrets)에서 API 키를 설정해주세요.")
    st.stop()

MONITORING_TARGETS = [
    {"query": "외장하드", "my_mall": "삼성공식파트너 쇼마젠시", "target_mall": ["삼성공식파트너 형연테크"], "target_mids": ["53122848087","53123371823","52997593981"]},
    {"query": "갤럭시워치7", "my_mall": "삼성파트너 쇼마젠시", "target_mall": ["삼성공식파트너 dmac", "삼성공식파트너 올인포케이"], "target_mids": []},
    {"query": "갤럭시워치8", "my_mall": "삼성파트너 쇼마젠시", "target_mall": ["삼성공식파트너 dmac", "삼성공식파트너 올인포케이"], "target_mids": ["55668557960", "55727507152", "55727496884", "55668573794"]},
    {"query": "갤럭시핏3", "my_mall": "삼성파트너 쇼마젠시", "target_mall": ["삼성공식파트너 dmac", "삼성공식파트너 올인포케이"], "target_mids": []}
]

st.title("🖥️ SHOPPING MONITOR TERMINAL")

if st.button("RUN MONITORING"):
    container = st.container()
    with container:
        for target in MONITORING_TARGETS:
            query = target["query"]
            st.markdown(f"**🔎 현재 검색 중: [{query}]**")
            
            items = get_naver_rank(target, C_ID, C_SECRET)
            found = False
            
            output_html = "<div class='status-text'>"
            for idx, item in enumerate(items):
                rank = idx + 1
                mall_name = item.get('mallName', '')
                title = item.get('title', '').replace('<b>', '').replace('</b>', '')
                product_id = item.get('productId', '')

                # 내 상품
                if target["my_mall"] in mall_name:
                    output_html += f"✅ [내 상품] {rank:2d}위 | {title[:40]}...<br>"
                    found = True
                
                # 경쟁사
                for tm in target["target_mall"]:
                    if tm in mall_name:
                        output_html += f"<span style='color:#ff4b4b;'>🚨 [경쟁사] {rank:2d}위</span> | {title[:40]}...<br>"
                        found = True
                
                # 원부
                if product_id in target["target_mids"]:
                    output_html += f"<span style='color:#3d9dfd;'>🎯 [원 부] {rank:2d}위</span> | {title[:40]}...<br>"
                    found = True
            
            if not found:
                output_html += "❌ 40위 내 검색 결과 없음<br>"
            
            output_html += "</div><br>"
            st.markdown(output_html, unsafe_allow_html=True)
            time.sleep(0.3)
