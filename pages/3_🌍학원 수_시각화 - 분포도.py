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

with st.expander("원본 데이터"):
    st.dataframe(df)

# Change "학원주소" column to "lat" and "lon"

df["학원주소"] = df["학원주소"].apply(refine_address)

df["lat"] = None
df["lon"] = None

st.subheader("학원 분포 시각화")
if st.button("분석하기 - scatter", key=0):
    progress_bar = st.sidebar.progress(0)
    status_text = st.sidebar.empty()

    # def iterrows(i, idx):
    #     address = df.loc[idx, "학원주소"]
    #     crd = geocoding_kakao(address)
    #     df.loc[idx, "lat"] = crd["lat"]
    #     df.loc[idx, "lon"] = crd["lon"]
    #     status_text.text(f"{i+1}/{len(df)} Complete")
    #     progress_bar.progress((i + 1) / len(df))

    # for i, idx in enumerate(df.index):
    #     iterrows(i, idx)

    import asyncio
    import concurrent.futures

    progress = 0

    async def main():
        global progress
        with concurrent.futures.ThreadPoolExecutor() as pool:
            loop = asyncio.get_event_loop()
            futures = [
                loop.run_in_executor(pool, geocoding_kakao, address)
                for address in df["학원주소"]
            ]
            for i, future in zip(df.index, futures):
                crd = await future
                df.loc[i, "lat"] = crd["lat"]
                df.loc[i, "lon"] = crd["lon"]
                progress += 1
                progress_bar.progress(progress / len(df))
                status_text.text(f"{progress}/{len(df)} Complete")

    asyncio.run(main())

    df = df.dropna(subset=["lat", "lon"])

    color_map = {
        "서구": "#FF8911",
        "중구": "#BF3612",
        "동구": "#40A2E3",
        "유성구": "#126737",
        "대덕구": "#7F27FF",
    }

    def set_color(address):
        for region, color in color_map.items():
            if region in address:
                return color
        return "black"

    df["color"] = df["학원주소"].apply(set_color)

    df = df[["lat", "lon", "color"]]

    df_clean = df.reset_index(drop=True)

    st.write("학원 분포도")
    st.map(df_clean, use_container_width=True, color="color")

    # Color legend
    color_markdown = ""
    for region, color in color_map.items():
        color_markdown += f"<span style='color: {color}; font-size: 20px;'>■</span> {region}&nbsp;&nbsp;&nbsp;"
    st.markdown(color_markdown, unsafe_allow_html=True)

    st.write("2021.12.31 기준 대전광역시 학원 분포도입니다.")
    dje_url = "https://www.dje.go.kr/boardCnts/view.do?boardID=10395&boardSeq=3269037&lev=0&searchType=S&statusYN=W&page=1&s=dje&m=031401&opType=N&prntBoardID=0&prntBoardSeq=0&prntLev=0"
    st.write("데이터 출처: [대전광역시교육청](%s)" % dje_url)


if st.button("분석하기 - hexagon", key=1):
    progress_bar = st.sidebar.progress(0)
    status_text = st.sidebar.empty()

    # def iterrows(i, idx):
    #     address = df.loc[idx, "학원주소"]
    #     crd = geocoding_kakao(address)
    #     df.loc[idx, "lat"] = crd["lat"]
    #     df.loc[idx, "lon"] = crd["lon"]
    #     status_text.text(f"{i+1}/{len(df)} Complete")
    #     progress_bar.progress((i + 1) / len(df))

    # for i, idx in enumerate(df.index):
    #     iterrows(i, idx)

    import asyncio
    import concurrent.futures

    progress = 0

    async def main():
        global progress
        with concurrent.futures.ThreadPoolExecutor() as pool:
            loop = asyncio.get_event_loop()
            futures = [
                loop.run_in_executor(pool, geocoding_kakao, address)
                for address in df["학원주소"]
            ]
            for i, future in zip(df.index, futures):
                crd = await future
                df.loc[i, "lat"] = crd["lat"]
                df.loc[i, "lon"] = crd["lon"]
                progress += 1
                progress_bar.progress(progress / len(df))
                status_text.text(f"{progress}/{len(df)} Complete")

    asyncio.run(main())

    df = df.dropna(subset=["lat", "lon"])

    color_map = {
        "서구": "#FF8911",
        "중구": "#BF3612",
        "동구": "#40A2E3",
        "유성구": "#126737",
        "대덕구": "#7F27FF",
    }

    def set_color(address):
        for region, color in color_map.items():
            if region in address:
                return color
        return "black"

    df["color"] = df["학원주소"].apply(set_color)

    df = df[["lat", "lon", "color"]]

    df_clean = df.reset_index(drop=True)

    st.write("학원 분포도")

    # Draw heatmap

    import pydeck as pdk

    layer = pdk.Layer(
        "HexagonLayer",
        df_clean,
        get_position="[lon, lat]",
        auto_highlight=True,
        elevation_scale=50,
        pickable=True,
        elevation_range=[0, 300],
        extruded=True,
        coverage=1,
    )

    view_state = pdk.ViewState(
        longitude=127.3845,
        latitude=36.3504,
        zoom=10,
        min_zoom=5,
        max_zoom=15,
        pitch=40.5,
        bearing=-27.36,
    )

    st.pydeck_chart(
        pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            layers=[layer],
            initial_view_state=view_state,
        )
    )

    # Color legend
    color_markdown = ""
    for region, color in color_map.items():
        color_markdown += f"<span style='color: {color}; font-size: 20px;'>■</span> {region}&nbsp;&nbsp;&nbsp;"
    st.markdown(color_markdown, unsafe_allow_html=True)

    st.write("2021.12.31 기준 대전광역시 학원 분포도입니다.")
    dje_url = "https://www.dje.go.kr/boardCnts/view.do?boardID=10395&boardSeq=3269037&lev=0&searchType=S&statusYN=W&page=1&s=dje&m=031401&opType=N&prntBoardID=0&prntBoardSeq=0&prntLev=0"
    st.write("데이터 출처: [대전광역시교육청](%s)" % dje_url)


with open(cache_path, "w") as f:
    json.dump(cache, f)
