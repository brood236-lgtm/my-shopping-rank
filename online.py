import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# 페이지 설정 (웹 브라우저 탭 이름과 아이콘)
st.set_page_config(page_title="쇼핑 순위 모니터링", page_icon="📊", layout="wide")

def get_naver_rank(target, client_id, client_secret):
    url = "https://openapi.naver.com/v1/search/shop.json"
    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
    
    query = target["query"]
    my_mall = target["my_mall"]
    target_malls = target.get("target_mall", [])
    if isinstance(target_malls, str): target_malls = [target_malls]
    target_mids = target.get("target_mids", [])

    params = {"query": query, "display": 100, "start": 1, "sort": "sim"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            items = response.json().get('items', [])
            results = []
            for idx, item in enumerate(items):
                rank = idx + 1
                mall_name = item.get('mallName', '')
                title = item.get('title', '').replace('<b>', '').replace('</b>', '')
                product_id = item.get('productId', '')

                if my_mall and (my_mall in mall_name):
                    results.append({"검색어": query, "순위": f"{rank}위", "구분": "✅ 내 쇼핑몰", "쇼핑몰명": mall_name, "상품명": title, "raw_rank": rank})
                
                for tm in target_malls:
                    if tm and (tm in mall_name):
                        results.append({"검색어": query, "순위": f"{rank}위", "구분": "🚨 경쟁사", "쇼핑몰명": mall_name, "상품명": title, "raw_rank": rank})
                        break
                
                if product_id in target_mids:
                    results.append({"검색어": query, "순위": f"{rank}위", "구분": "🎯 원부", "쇼핑몰명": mall_name, "상품명": title, "raw_rank": rank})
            return results
    except:
        return []
    return []

# === 사이드바 설정 ===
st.sidebar.title("⚙️ 설정")
CLIENT_ID = st.sidebar.text_input("네이버 Client ID", value="z3Guexy_a5AiWXIDub2e", type="password")
CLIENT_SECRET = st.sidebar.text_input("네이버 Client Secret", value="adgqyvVjXu", type="password")

# 🎯 모니터링 타겟 설정
MONITORING_TARGETS = [
    {"query": "외장하드", "my_mall": "삼성공식파트너 쇼마젠시", "target_mall": ["삼성공식파트너 형연테크"], "target_mids": ["53122848087","53123371823","52997593981"]},
    {"query": "갤럭시워치7", "my_mall": "삼성파트너 쇼마젠시", "target_mall": ["삼성공식파트너 dmac", "삼성공식파트너 올인포케이"], "target_mids": []},
    {"query": "갤럭시워치8", "my_mall": "삼성파트너 쇼마젠시", "target_mall": ["삼성공식파트너 dmac", "삼성공식파트너 올인포케이"], "target_mids": ["55668557960", "55727507152"]},
    {"query": "갤럭시핏3", "my_mall": "삼성파트너 쇼마젠시", "target_mall": ["삼성공식파트너 dmac", "삼성공식파트너 올인포케이"], "target_mids": []}
]

# === 메인 화면 ===
st.title("📊 실시간 쇼핑 순위 대시보드")
st.write(f"업데이트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if st.button("🚀 지금 순위 확인하기"):
    all_data = []
    progress_bar = st.progress(0)
    
    for i, target in enumerate(MONITORING_TARGETS):
        res = get_naver_rank(target, CLIENT_ID, CLIENT_SECRET)
        all_data.extend(res)
        progress_bar.progress((i + 1) / len(MONITORING_TARGETS))
        time.sleep(0.5)

    if all_data:
        df = pd.DataFrame(all_data).sort_values(by=['검색어', 'raw_rank'])
        display_df = df.drop(columns=['raw_rank'])

        # 결과 테이블 표시
        st.success("조회가 완료되었습니다!")
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # 엑셀 다운로드 버튼
        csv = display_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(label="📥 결과 엑셀(CSV) 다운로드", data=csv, file_name=f"순위결과_{datetime.now().strftime('%m%d_%H%M')}.csv", mime='text/csv')
    else:
        st.warning("40위 내에 일치하는 상품이 없습니다.")