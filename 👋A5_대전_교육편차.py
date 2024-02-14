import pandas as pd
import streamlit as st
import folium
from folium import GeoJsonTooltip
from streamlit_folium import folium_static
import geopandas as gpd
import plotly.express as px

st.title('여러가지 지표로 알아보는 대전 교육편차')

data_path = 'student_number.csv'
df = pd.read_csv(data_path)

filter_option = st.selectbox('필터링 기준:', ['학원수', '학생수', '유학수'])
show_ratio = st.checkbox('전체 비중으로 보기', value=True)

if show_ratio:
    total = df[filter_option].sum()
    df['ratio'] = df[filter_option] / total * 100
    fig = px.bar(df, x='지역', y='ratio', color='지역', labels={'ratio': f'{filter_option} 비율(%)'},
                 title=f'지역별 {filter_option} 비율')
else:
    fig = px.bar(df, x='지역', y=filter_option, color='지역', labels={'value': filter_option}, title=f'지역별 {filter_option}')

st.plotly_chart(fig)


def create_map(df, geojson_path, centers, filter_option, show_ratio):
    m = folium.Map(location=[36.3504, 127.3845], zoom_start=11)

    folium.GeoJson(
        geojson_path,
        name="구",
        style_function=lambda feature: {'fillColor': get_color(feature['properties']['sggnm']),
                                        'color': 'grey',
                                        'weight': 1,
                                        'fillOpacity': 0.4},
        tooltip=GeoJsonTooltip(fields=['sggnm'], aliases=['구'], localize=True)
    ).add_to(m)

    for index, row in df.iterrows():
        district = row['지역']
        value = row['ratio'] if show_ratio else row[filter_option]

        folium.Circle(
            location=centers[district],
            radius=value * (100 if show_ratio else 1),
            color=get_color(district),
            fill=True,
            fill_color=get_color(district),
            fill_opacity=0.6,
            tooltip=f"{district}: {filter_option} {value:.2f}" + ("%" if show_ratio else ""),
        ).add_to(m)

    return m


def get_color(district):
    colors = {
        '동구': 'blue',
        '중구': 'green',
        '서구': 'red',
        '유성구': 'purple',
        '대덕구': 'orange'
    }
    return colors.get(district, 'gray')


geojson_path = 'daejeon.geojson'
gdf = gpd.read_file(geojson_path)
gdf['center'] = gdf.geometry.centroid
centers = {row['sggnm']: [row['center'].y, row['center'].x] for index, row in gdf.iterrows()}

m = create_map(df, geojson_path, centers, filter_option, show_ratio)
folium_static(m)
