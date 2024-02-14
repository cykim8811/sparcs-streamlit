import streamlit as st
import pandas as pd
import plotly.express as px

df = pd.read_csv("simple.csv")

df['Index'] = range(1, len(df) + 1)

df_long = pd.melt(df, id_vars=['Region', 'Index'], value_vars=['Total'])

st.title('대전시 구별 학교수')

fig = px.bar(df_long, x='Region', y='value', color='Region', title='',
             labels={'value': '학교 수', 'Region': '지역'}, hover_name='Region')

fig.update_traces(marker=dict(line=dict(color='rgb(8,48,107)', width=1.5)))
st.plotly_chart(fig, use_container_width=True)
