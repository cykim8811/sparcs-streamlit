import streamlit as st
import requests
import os
import json


import pandas as pd

KAKAO_API_KEY = "3878037d9682629310b102d07e8f69e2"

st.set_page_config(
    page_title="대전 교육격차 시각화 - 분포도",
    page_icon="🌍",
)


cache = {}
cache_path = "kakao_cache.json"
if os.path.exists(cache_path):
    with open(cache_path, "r") as f:
        cache = json.load(f)
else:
    cache = {}


def geocoding_kakao(address):
    global cache

    if address in cache:
        return cache[address]

    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": address}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if data["meta"]["total_count"] == 0:
        return {"lat": None, "lon": None}
    crd = {
        "lat": float(data["documents"][0]["y"]),
        "lon": float(data["documents"][0]["x"]),
    }
    cache[address] = crd
    return crd


def refine_address(address):
    # Find match until it finds
    # SPACE + NUMBER + SPACE
    # or SPACE + NUMBER + "-" + NUMBER + SPACE
    import re

    match = re.search(r"(\s\d+)|(\s\d+-\d+)", address)
    if match:
        return address[: match.end()]


st.title("지역격차 시각화")

with st.sidebar:
    sample_rate = st.slider("샘플링 비율", 0.01, 0.05, 0.01)


df_west = pd.read_csv("서부교육지원청+학원+현황(2023.12.31.).csv")
df_east = pd.read_csv("동부교육지원청+학원+현황(2023.12.31.).csv")

df_west_len = len(df_west)
df_east_len = len(df_east)

df_west = df_west.sample(frac=sample_rate)
df_east = df_east.sample(frac=sample_rate)

df = pd.concat([df_west, df_east])

with st.sidebar:
    st.markdown(
        f"""
    ### 전체 학원 수: {df_west_len + df_east_len}
    - 서부교육지원청: {df_west_len}
    - 동부교육지원청: {df_east_len}
    """
    )
    st.write(f"Cached Data Size: {len(cache)}")


df["학원주소"] = df["학원주소"].apply(refine_address)

df["lat"] = None
df["lon"] = None

st.subheader("학원 분포 시각화")
if st.button("분석하기", key="map"):
    color_map = {
        "서구": "#FF8911",
        "중구": "#BF3612",
        "동구": "#40A2E3",
        "유성구": "#126737",
        "대덕구": "#7F27FF",
    }

    def categorize_address(address):
        for region in color_map:
            if region in address:
                return region
        return "기타"

    df["region"] = df["학원주소"].apply(categorize_address)

    address_count = df["region"].value_counts()

    crd = {}
    for address in color_map:
        crd[address] = geocoding_kakao("대전광역시 " + address)

    circle_chart = pd.DataFrame(crd).T

    circle_chart["count"] = address_count * 30
    circle_chart["color"] = circle_chart.index.map(lambda x: color_map[x] + "B0")

    circle_chart = circle_chart.sort_values("count", ascending=True)

    st.map(circle_chart, color="color", size="count", use_container_width=True)

    # Color legend
    color_markdown = ""
    for region, color in color_map.items():
        color_markdown += f"<span style='color: {color}; font-size: 20px;'>■</span> {region}&nbsp;&nbsp;&nbsp;"
    st.markdown(color_markdown, unsafe_allow_html=True)

    st.dataframe(address_count)

