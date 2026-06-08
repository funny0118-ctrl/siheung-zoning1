import streamlit as st
import pandas as pd
from pathlib import Path

# -------------------------------------------------
# ✅ 기본 설정 (반드시 최상단)
# -------------------------------------------------
st.set_page_config(
    page_title="시흥시 용도지역별 건축물 가능 여부 조회",
    page_icon="🏢",
    layout="wide"
)

# -------------------------------------------------
# ✅ DB 경로 (Streamlit Cloud 대응)
# -------------------------------------------------
BASE_DIR = Path(__file__).parent
DB_FILE = BASE_DIR / "zoning_db.xlsx"

# -------------------------------------------------
# ✅ 데이터 로딩 (캐시 적용)
# -------------------------------------------------
@st.cache_data(show_spinner=False)
def load_data():
    if not DB_FILE.exists():
        return pd.DataFrame()

    df = pd.read_excel(DB_FILE, dtype=str)

    # ✅ 컬럼 공백 제거
    df.columns = df.columns.str.strip()

    # ✅ 문자열 값 공백 제거
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)

    return df

df = load_data()

# -------------------------------------------------
# ✅ 타이틀
# -------------------------------------------------
st.title("🏢 시흥시 용도지역별 건축물 가능 여부 조회")

# -------------------------------------------------
# ✅ 파일 없을 경우
# -------------------------------------------------
if df.empty:
    st.error("❌ zoning_db.xlsx 파일이 없거나 비어 있습니다.")
    st.stop()

# -------------------------------------------------
# ✅ 필수 컬럼 자동 보정
# -------------------------------------------------
required_columns = ["용도지역", "건축물용도", "가능여부"]

for col in required_columns:
    if col not in df.columns:
        df[col] = ""

# -------------------------------------------------
# ✅ 용도지역 선택
# -------------------------------------------------
regions = sorted(df["용도지역"].dropna().unique())

if not regions:
    st.warning("등록된 용도지역이 없습니다.")
    st.stop()

selected_region = st.selectbox(
    "📍 용도지역 선택",
    regions
)

region_df = df[df["용도지역"] == selected_region]

# -------------------------------------------------
# ✅ 검색창
# -------------------------------------------------
search_text = st.text_input(
    "🔎 건축물 용도 검색",
    placeholder="예 : 판매시설, 공장, 의료시설"
)

uses = sorted(region_df["건축물용도"].dropna().unique())

if search_text:
    uses = [u for u in uses if search_text.lower() in u.lower()]

if not uses:
    st.warning("검색 결과가 없습니다. 다른 검색어를 입력하세요.")
    st.stop()

selected_use = st.selectbox(
    "🏗 건축물 용도 선택",
    uses
)

# -------------------------------------------------
# ✅ 결과 조회
# -------------------------------------------------
result = region_df[region_df["건축물용도"] == selected_use]

if not result.empty:

    row = result.iloc[0]

    st.markdown("---")
    st.subheader("📋 조회 결과")

    status = str(row.get("가능여부", "")).strip()

    if "불가" in status or "불허" in status:
        st.error(f"🚫 판정 : {status}")
    elif "가능" in status or "허용" in status:
        st.success(f"✅ 판정 : {status}")
    else:
        st.info(f"ℹ 판정 : {status if status else '정보 없음'}")

    # ✅ 조건 표시
    if "조건" in df.columns:
        condition = row.get("조건", "")
        if pd.notna(condition) and str(condition).strip():
            st.info(f"📌 조건 : {condition}")

    # ✅ 심의 여부 표시
    if "도시계획위원회 심의 대상" in df.columns:
        committee = row.get("도시계획위원회 심의 대상", "")
        if pd.notna(committee) and str(committee).strip():
            st.write(f"📝 도시계획위원회 심의 : {committee}")

    # ✅ 상세 데이터
    with st.expander("📊 상세 데이터 보기"):
        st.dataframe(result, use_container_width=True)
