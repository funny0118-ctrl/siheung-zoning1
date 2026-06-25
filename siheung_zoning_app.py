import streamlit as st
import pandas as pd
from pathlib import Path

# =========================================================
# 기본설정
# =========================================================

st.set_page_config(
    page_title="시흥시 용도지역별 건축물 가능 여부 조회",
    page_icon="🏢",
    layout="wide"
)

BASE_DIR = Path(__file__).parent

DB_FILE = BASE_DIR / "zoning_db.xlsx"

PARCEL_FILE = BASE_DIR / "parcel_zone_app_ready.xlsx"



# =========================================================
# zoning DB
# =========================================================

@st.cache_data(show_spinner=False)
def load_zoning():

    if not DB_FILE.exists():
        return pd.DataFrame()

    df = pd.read_excel(
        DB_FILE,
        dtype=str
    )

    df.columns = df.columns.str.strip()

    df = df.apply(
        lambda x:
        x.str.strip()
        if x.dtype=="object"
        else x
    )

    return df


df = load_zoning()



# =========================================================
# parcel DB
# =========================================================


@st.cache_data(show_spinner=False)
def load_parcel():

    if not PARCEL_FILE.exists():
        return pd.DataFrame()


    p = pd.read_excel(

        PARCEL_FILE,

        dtype=str

    )


    p.columns = p.columns.str.strip()



    p = p.apply(

        lambda x:

        x.str.strip()

        if x.dtype=="object"

        else x

    )



    return p



parcel_df = load_parcel()




# =========================================================
# 제목
# =========================================================


st.title(

"🏢 시흥시 용도지역별 건축물 가능 여부 조회"

)



st.info(

"""
ℹ️ 본 시스템은 시흥시 도시계획조례에 따른 참고용 서비스입니다.

건축허가 및 인허가 가능 여부를 보장하지 않습니다.

반드시 해당부서에 확인하시기 바랍니다.
"""

)





# =========================================================
# 파일 확인
# =========================================================


if df.empty:

    st.error(

        "zoning_db.xlsx 없음"

    )

    st.stop()



if parcel_df.empty:


    st.error(

        "parcel_zone_app_ready.xlsx 없음"

    )


    st.stop()





# =========================================================
# 지번검색
# =========================================================


st.subheader(

"📌 지번검색"

)




addr = st.text_input(

    "검색주소 입력",

    placeholder="예 : 포동 342"

)




if addr=="":


    st.stop()




parcel = parcel_df[


    parcel_df["검색주소"]

    ==


    addr

]





if parcel.empty:


    st.error(

        "등록되지 않은 지번"

    )


    st.stop()




zones = [



    z.strip()



    for z



    in



    parcel.iloc[0]["용도지역"]

    .split(",")



]





selected_region = st.selectbox(

    "📍 용도지역",

    zones

)




st.success(

f"선택 용도지역 : {selected_region}"

)





region_df = df[


    df["용도지역"]

    ==


    selected_region


]
# =========================================================
# 건축물 대분류 선택
# =========================================================

categories = sorted(

    region_df["대분류"]

    .dropna()

    .unique()

)


selected_category = st.selectbox(

    "🏢 건축물 대분류",

    ["전체"] + list(categories)

)



if selected_category != "전체":


    region_df = region_df[


        region_df["대분류"]

        ==


        selected_category


    ]



# =========================================================
# 건축물 검색
# =========================================================


search_text = st.text_input(

    "🔎 건축물 용도 검색",

    placeholder="예 : 판매시설"

)



uses = sorted(


    region_df["건축물용도"]

    .dropna()

    .unique()

)



if search_text:


    uses = [


        u


        for u


        in uses


        if


        search_text.lower()


        in


        u.lower()


    ]





if not uses:


    st.warning(

        "검색 결과가 없습니다."

    )



    st.stop()




selected_use = st.selectbox(


    "🏗 건축물 용도 선택",


    uses

)




# =========================================================
# 조회
# =========================================================


result = region_df[


    region_df["건축물용도"]

    ==


    selected_use


]



if result.empty:


    st.warning(

        "자료가 없습니다."

    )


    st.stop()




row = result.iloc[0]
# =========================================================
# 조회 결과
# =========================================================

st.markdown("---")

st.subheader("📋 조회 결과")


# -----------------------------
# 지번정보
# -----------------------------

st.write(
    f"📌 검색주소 : {addr}"
)


# 개발제한구역

gb = parcel.iloc[0].get(
    "개발제한구역",
    ""
)

if pd.notna(gb):

    if str(gb).strip():

        st.info(

            f"🌳 개발제한구역 : {gb}"

        )



# -----------------------------
# 가능여부
# -----------------------------


status = str(

    row.get(

        "가능여부",

        ""

    )

).strip()



if (

    "불가"

    in

    status

):


    st.error(

        f"🚫 판정 : {status}"

    )



elif (

        "가능"

        in

        status

):


    st.success(

        f"✅ 판정 : {status}"

    )



else:


    st.info(

        f"ℹ 판정 : {status}"

    )




# -----------------------------
# 조건
# -----------------------------


condition = row.get(

    "조건",

    ""

)



if pd.notna(

        condition

):



    if str(

            condition

    ).strip():



        st.info(


            f"📌 조건 : {condition}"


        )



# -----------------------------
# 도시계획위원회
# -----------------------------


committee = row.get(

    "도시계획위원회 심의 대상",

    ""

)


if pd.notna(

        committee

):



    if str(

            committee

    ).strip():



        st.write(

            f"📝 도시계획위원회 심의 : {committee}"

        )




# -----------------------------
# 상세 데이터
# -----------------------------


with st.expander(

        "📊 상세 데이터 보기"

):



    st.dataframe(

        result,

        use_container_width=True

    )



# =========================================================
# 하단 안내문
# =========================================================

st.markdown("---")



st.caption(

"※ 본 서비스는 시흥시 도시계획조례를 기준으로 제공되는 참고용 자료입니다."

)



st.caption(

"※ 지구단위계획구역의 경우 해당 지역의 지구단위계획 결정도서 및 시행지침을 반드시 확인하시기 바랍니다."

)



st.caption(

"※ 건축허가 및 인허가 가능 여부를 보장하지 않으며, 반드시 관련 부서와 협의하시기 바랍니다."

)