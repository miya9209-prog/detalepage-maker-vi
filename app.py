import streamlit as st
import pandas as pd
from PIL import Image
import io
import os

# =========================
# 기본 설정
# =========================

st.set_page_config(
    page_title="MS 상세페이지 자동생성기",
    page_icon="🧷",
    layout="centered"
)

# =========================
# 비밀번호 엑셀 자동 로딩
# =========================

PASSWORD_FILE = "비번리스트.xlsx"

@st.cache_data(show_spinner=False)
def load_passwords():
    if not os.path.exists(PASSWORD_FILE):
        st.error("비밀번호 파일이 존재하지 않습니다. (비번리스트.xlsx)")
        return set()

    df = pd.read_excel(PASSWORD_FILE)

    col = df.columns[0]
    passwords = (
        df[col]
        .astype(str)
        .str.strip()
        .replace({"nan": ""})
    )

    return set([p for p in passwords.tolist() if p])

PRO_PASSWORDS = load_passwords()

# =========================
# 세션 상태
# =========================

if "is_pro" not in st.session_state:
    st.session_state.is_pro = False

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

# =========================
# 상단 타이틀
# =========================

st.markdown("## MS 상세페이지 자동생성기 [FREE]")
st.markdown("20년차 온라인 쇼핑몰 대표가 직접 제작한 상세페이지 업무툴입니다.")
st.markdown("---")

# =========================
# PRO 로그인
# =========================

st.markdown("### 🔒 PRO 신청")

pw = st.text_input("비밀번호 입력", type="password")

if st.button("확인"):
    if pw and pw.strip() in PRO_PASSWORDS:
        st.session_state.is_pro = True
        st.success("PRO 활성화 완료")
    else:
        st.error("비밀번호가 올바르지 않습니다.")

st.markdown("---")

# =========================
# 업로드 영역
# =========================

max_files = 30 if st.session_state.is_pro else 10

uploaded = st.file_uploader(
    f"이미지 업로드 (최대 {max_files}개)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if uploaded:
    if len(uploaded) > max_files:
        st.warning(f"최대 {max_files}개까지만 업로드 가능합니다.")
    else:
        st.session_state.uploaded_files = uploaded

gap = st.slider("이미지 간격 (px)", 0, 100, 20)

# =========================
# 이미지 합치기 함수
# =========================

def build_detail_image(images, gap, pad=100):

    widths = [im.width for im in images]
    max_w = max(widths)

    heights = [im.height for im in images]
    total_h = pad + pad + sum(heights) + gap * (len(images) - 1)

    canvas = Image.new("RGB", (max_w, total_h), (255, 255, 255))

    y = pad
    for im in images:
        x = (max_w - im.width) // 2
        canvas.paste(im, (x, y))
        y += im.height + gap

    return canvas

# =========================
# 미리보기 (PRO만)
# =========================

if st.session_state.is_pro and st.session_state.uploaded_files:
    st.markdown("### 업로드 미리보기 (PRO)")
    cols = st.columns(4)
    for i, f in enumerate(st.session_state.uploaded_files):
        img = Image.open(f)
        cols[i % 4].image(img, use_container_width=True)

# =========================
# 생성 버튼
# =========================

if st.button("상세페이지 생성 (JPG)"):

    if not st.session_state.uploaded_files:
        st.error("이미지를 업로드해주세요.")
    else:
        images = []

        for f in st.session_state.uploaded_files:
            img = Image.open(f)

            if img.mode == "RGBA":
                bg = Image.new("RGB", img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[-1])
                img = bg

            images.append(img)

        result = build_detail_image(images, gap)

        buf = io.BytesIO()
        result.save(buf, format="JPEG", quality=95)

        st.success("상세페이지 생성 완료")

        st.download_button(
            "다운로드",
            data=buf.getvalue(),
            file_name="misharp_detail.jpg",
            mime="image/jpeg"
        )

# =========================
# 초기화 버튼
# =========================

if st.button("초기화"):
    st.session_state.uploaded_files = []
    st.rerun()

st.markdown("---")
st.markdown("© MISHARP")
