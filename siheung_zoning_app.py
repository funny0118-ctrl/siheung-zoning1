
import pandas as pd
import streamlit as st

st.set_page_config(page_title="시흥시 용도지역별 건축물 가능 여부 조회", layout="wide")

st.title("시흥시 용도지역별 건축물 가능 여부 조회")

uploaded_file = st.file_uploader("DB 엑셀 파일 업로드", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    required = ["건축물용도", "용도지역", "가능여부", "조건", "도시계획위원회 심의 대상"]
    missing = [c for c in required if c not in df.columns]

    if missing:
        st.error(f"필수 컬럼이 없습니다: {missing}")
    else:
        regions = sorted(df["용도지역"].dropna().astype(str).unique())
        region = st.selectbox("용도지역", regions)

        uses = sorted(df["건축물용도"].dropna().astype(str).unique())
        use = st.selectbox("건축물 용도", uses)

        if st.button("조회"):
            result = df[
                (df["용도지역"].astype(str) == region)
                & (df["건축물용도"].astype(str) == use)
            ]

            if result.empty:
                st.warning("해당 자료가 없습니다.")
            else:
                row = result.iloc[0]

                st.subheader("조회 결과")
                st.write(f"**판정:** {row.get('가능여부','')}")

                condition = row.get("조건", "")
                if pd.notna(condition) and str(condition).strip():
                    st.write(f"**조건:** {condition}")

                if "대분류" in row.index:
                    st.write(f"**대분류:** {row['대분류']}")

                st.dataframe(result, use_container_width=True)
else:
    st.info("변환된 DB 엑셀 파일을 업로드하세요.")
