import pandas as pd
import streamlit as st

st.set_page_config(
page_title="시흥시 용도지역별 건축물 가능 여부 조회",
page_icon="🏢",
layout="wide"
)

DB_FILE = "zoning_db.xlsx"

@st.cache_data
def load_data():
return pd.read_excel(DB_FILE)

try:
df = load_data()
except Exception as e:
st.error(f"DB 파일을 읽을 수 없습니다.\n\n{e}")
st.stop()

st.title("🏢 시흥시 용도지역별 건축물 가능 여부 조회")

required_columns = [
"용도지역",
"건축물용도",
"가능여부"
]

missing = [
col for col in required_columns
if col not in df.columns
]

if missing:
st.error(f"필수 컬럼이 없습니다 : {missing}")
st.stop()

regions = sorted(
df["용도지역"]
.dropna()
.astype(str)
.unique()
)

selected_region = st.selectbox(
"용도지역 선택",
regions
)

region_df = df[
df["용도지역"].astype(str)
== selected_region
]

search_text = st.text_input(
"건축물 용도 검색",
placeholder="예 : 판매시설, 공장, 의료시설"
)

uses = sorted(
region_df["건축물용도"]
.dropna()
.astype(str)
.unique()
)

if search_text:
uses = [
u for u in uses
if search_text.lower() in u.lower()
]

if len(uses) == 0:
st.warning("검색 결과가 없습니다.")
st.stop()

selected_use = st.selectbox(
"건축물 용도 선택",
uses
)

result = region_df[
region_df["건축물용도"].astype(str)
== selected_use
]

if not result.empty:

```
row = result.iloc[0]

st.markdown("---")
st.subheader("조회 결과")

status = str(
    row.get("가능여부", "")
).strip()

if (
    "불가" in status
    or "불허" in status
):
    st.error(f"판정 : {status}")

elif (
    "가능" in status
    or "허용" in status
):
    st.success(f"판정 : {status}")

else:
    st.warning(f"판정 : {status}")

if "조건" in result.columns:

    condition = row.get("조건", "")

    if (
        pd.notna(condition)
        and str(condition).strip()
    ):
        st.info(
            f"조건 : {condition}"
        )

if "도시계획위원회 심의 대상" in result.columns:

    committee = row.get(
        "도시계획위원회 심의 대상",
        ""
    )

    if (
        pd.notna(committee)
        and str(committee).strip()
    ):
        st.write(
            f"도시계획위원회 심의 : {committee}"
        )

with st.expander("상세 정보 보기"):
    st.dataframe(
        result,
        use_container_width=True
    )
```
