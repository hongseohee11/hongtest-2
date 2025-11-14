import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="11월 과일 판매량", layout="centered")

st.title("📊 11월 과일 판매량")
st.write("다음은 11월 한 달 동안의 과일별 판매량 예시입니다.")

# 샘플 데이터 (11월)
data = {
    "과일": ["배", "사과", "메론", "딸기", "수박"],
    "판매량": [120, 95, 45, 80, 60],
}
df = pd.DataFrame(data)

with st.sidebar:
    st.header("옵션")
    show_values = st.checkbox("데이터 값 표시", value=True)
    show_percent = st.checkbox("원그래프에 비율 표시", value=True)

# 막대그래프
bar_fig = px.bar(df, x="과일", y="판매량", color="과일", text="판매량" if show_values else None,
                 title="11월 과일별 판매량 (막대그래프)")
bar_fig.update_layout(showlegend=False)
st.plotly_chart(bar_fig, use_container_width=True)

# 원그래프 2개: 하나는 원래 값, 하나는 비율(레이블에 백분율 표시)
col1, col2 = st.columns(2)
with col1:
    pie1 = px.pie(df, names="과일", values="판매량", title="원형 분포 (값)")
    if show_values:
        pie1.update_traces(textinfo="value+label")
    else:
        pie1.update_traces(textinfo="label")
    st.plotly_chart(pie1, use_container_width=True)

with col2:
    pie2 = px.pie(df, names="과일", values="판매량", title="원형 분포 (비율)")
    if show_percent:
        pie2.update_traces(textinfo="percent+label")
    else:
        pie2.update_traces(textinfo="label")
    st.plotly_chart(pie2, use_container_width=True)

# 데이터 테이블 및 다운로드
st.subheader("데이터 (표)")
st.dataframe(df.set_index("과일"))

csv = df.to_csv(index=False).encode("utf-8-sig")
st.download_button("CSV로 다운로드", csv, "11월_과일_판매량.csv", "text/csv")
