import pandas as pd
import streamlit as st

st.set_page_config(
page_title="시흥시 용도지역별 건축물 가능 여부 조회",
layout="wide"
)

st.title("시흥시 용도지역별 건축물 가능 여부 조회")

# 엑셀 자동 로드

DB_FILE = "zoning_db.xlsx"

try:
df = pd.read_excel(DB_FILE)
except Exception as e:
st.error(f"DB 파일을 읽을 수 없습니다.\n{e}")
st.stop()

required = ["건축물용도", "용도지역", "가능여부", "조건"]
missing = [c for c in required if c not in df.columns]

if missing:
st.error(f"필수 컬럼이 없습니다: {missing}")
st.stop()

regions = sorted(df["용도지역"].dropna().astype(str).unique())
region = st.selectbox("용도지역", regions)

선택한 용도지역의 건축물 용도 목록

uses = sorted(
df[df["용도지역"].astype(str) == region]["건축물용도"]
.dropna()
.astype(str)
.unique()
)

검색창

search_text = st.text_input(
"건축물 용도 검색",
placeholder="예: 판매시설, 공장, 의료시설"
)

검색어 필터링

if search_text:
filtered_uses = [
u for u in uses
if search_text.lower() in str(u).lower()
]
else:
filtered_uses = uses

검색 결과 선택

use = st.selectbox(
"건축물 용도 선택",
filtered_uses
)
result = df[
(df["용도지역"].astype(str) == region)
& (df["건축물용도"].astype(str) == use)
]

if not result.empty:

```
row = result.iloc[0]

st.subheader("조회 결과")

status = str(row.get("가능여부", ""))

if "불가" in status or "불허" in status:
    st.error(f"판정 : {status}")
elif "가능" in status or "허용" in status:
    st.success(f"판정 : {status}")
else:
    st.warning(f"판정 : {status}")

condition = row.get("조건", "")
if pd.notna(condition) and str(condition).strip():
    st.info(f"조건 : {condition}")

st.dataframe(result, use_container_width=True)
```
