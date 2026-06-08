import streamlit as st
import pandas as pd
from pathlib import Path

# -------------------------------------------------
# ✅ 기본 설정
# -------------------------------------------------
st.set_page_config(
    page_title="시흥시 용도지역별 건축물 가능 여부 조회",
    page_icon="🏢",
    layout="wide"
)

BASE_DIR = Path(__file__).parent
DB_FILE = BASE_DIR / "zoning_db.xlsx"

# -------------------------------------------------
# ✅ 데이터 로딩
# -------------------------------------------------
@st.cache_data(show_spinner=False)
def load_data():
    if not DB_FILE.exists():
        return pd.DataFrame()

    df = pd.read_excel(DB_FILE, dtype=str)
    df.columns = df.columns.str.strip()
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
    return df

df = load_data()

# -------------------------------------------------
# ✅ 제목
# -------------------------------------------------
st.title("🏢 시흥시 용도지역별 건축물 가능 여부 조회")

# ✅ ✅ ✅ 제목 아래 고정 안내문 추가
st.info("""
ℹ️ 본 시스템은 시흥시 용도지역별 건축물 가능 여부를 간편 조회하기 위한 참고용 서비스입니다.

⚠️ 본 자료는 단순 조회용으로 정확한 사항은 반드시 해당 부서에 확인하시기 바랍니다.
""")

# -------------------------------------------------
# ✅ 파일 확인
# -------------------------------------------------
if df.empty:
    st.error("❌ zoning_db.xlsx 파일이 없거나 비어 있습니다.")
    st.stop()

# -------------------------------------------------
# ✅ 필수 컬럼 보정
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
# ✅ 건축물 검색
# -------------------------------------------------
search_text = st.text_input(
    "🔎 건축물 용도 검색",
    placeholder="예 : 판매시설, 공장, 의료시설"
)

uses = sorted(region_df["건축물용도"].dropna().unique())

if search_text:
    uses = [u for u in uses if search_text.lower() in u.lower()]

if not uses:
    st.warning("검색 결과가 없습니다.")
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

    # ✅ 지구단위구역 안내문
    if "지구단위" in selected_region:
        st.info("📌 지구단위구역은 해당지역 지구단위계획지침을 참고하시기 바랍니다.")

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

    # ✅ 도시계획위원회 심의 대상 표시
    if "도시계획위원회 심의 대상" in df.columns:
        committee = row.get("도시계획위원회 심의 대상", "")
        if pd.notna(committee) and str(committee).strip():
            st.write(f"📝 도시계획위원회 심의 : {committee}")

    # ✅ 상세 데이터 보기
    with st.expander("📊 상세 데이터 보기"):
        st.dataframe(result, use_container_width=True)
