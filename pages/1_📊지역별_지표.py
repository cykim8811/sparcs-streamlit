file_path = "private_institute.csv"

import pandas as pd

df = pd.read_csv(file_path, index_col=0)

import streamlit as st

st.set_page_config(
    page_title="대전 교육격차 지표",
    page_icon="👋",
)


all_regions = ["동구", "중구", "서구", "유성구", "대덕구"]
regions = []
with st.sidebar:
    with st.expander("지역 선택"):
        for region in all_regions:
            if st.checkbox(region, value=True):
                regions.append(region)


st.title("사교육기관 현황")

# 원본 데이터
with st.expander("원본 데이터"):
    st.subheader("원본 데이터")
    st.dataframe(df)
    st.write("AMTH: Average Monthly Teaching Hours")
    st.write("AMTF: Average Monthly Tution Fees(Won)")


institutes_count = df[df.index.isin(regions)]

# 지역별 지표
st.subheader("지역별 지표")
st.dataframe(institutes_count)


for t, s in [
    ("T.O.", "지역별 일시수용 능력인원"),
    ("Private Institutes", "지역별 사교육기관 수"),
    ("Instructors", "지역별 교사 수"),
    ("Classrooms", "지역별 강의실 수"),
]:
    st.subheader(s)
    st.bar_chart(
        pd.DataFrame(
            {
                s: pd.to_numeric(institutes_count[t]),
                "Categories": regions,
            }
        ).set_index("Categories")
    )
