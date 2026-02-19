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
    layout="wide"
)

# =========================
# 비밀번호 로딩
# =========================

PASSWORD_FILE = "비번리스트.xlsx"

@st.cache_data(show_spinner=False)
def load_passwords():
    if not os.path.exists(PASSWORD_FILE):
        return set()
    df = pd.read_excel(PASSWORD_FILE)
    col = df.columns[0]
    return set(df[col].astype(str).str.strip())

PRO_PASSWORDS = load_passwords()

# =========================
# 세션 초기화
# =========================

if "is_pro" not in st.session_state:
    st.session_state.is_pro = False

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

# =========================
# 🎨 디자인 CSS (목업 기반 재설계)
# =========================

st.markdown("""
<style>

.block-container {
    max-width: 1180px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

body {
    background: linear-gradient(180deg, #fafafa 0%, #f4f6f9 100%);
}

/* 상단 배지 */
.badge {
    font-size: 12px;
    padding: 6px 12px;
    background: #f1f3f6;
    border-radius: 20px;
    display: inline-block;
    margin-bottom: 20px;
    color: #666;
}

/* 히어로 */
.hero {
    background: linear-gradient(135deg, #ffdce6, #dceeff);
    padding: 30px;
    border-radius: 18px;
    margin-bottom: 30px;
}

.hero h1 {
    font-size: 28px;
    font-weight: 800;
    margin-bottom: 8px;
}

.hero p {
    font-size: 15px;
    color: #333;
}

/* 카드 */
.card {
    background: #ffffff;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.05);
    margin-bottom: 30px;
}

/* 버튼 */
div.stButton > button {
    border-radius: 14px !important;
    font-weight: 700 !important;
    padding: 0.6rem 1.2rem !important;
}

/* 강조 버튼 */
.primary-btn button {
    background: #0f172a !important;
    color: white !important;
}

/* 업로드 박스 강조 */
section[data-testid="stFileUploader"] {
    border-radius: 16px !important;
}

/* 제목 계층 */
.section-title {
    font-size: 20px;
    font-weight: 800;
    margin-bottom: 12px;
}

.small-text {
    font-size: 13px;
    color: #666;
}

</style>
""", unsafe_allow_html=True)

# =========================
# 상단 영역
# =========================

col1, col2 = st.columns([0.8, 0.2])

with col1:
    st.markdown('<div class="badge">MISHARP IMAGE GENERATOR V1 - FREE VERSION</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
    if st.button("PRO 신청"):
        st.session_state.show_pro = True
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# 히어로
# =========================

st.markdown("""
<div class="hero">
<h1>디자이너의 단순 작업, 이제 자동으로.</h1>
<p>20년차 쇼핑몰 운영자가 현업에서 쓰려고 만든 상세페이지 업무툴입니다. 빠르고, 깔끔하고, 실수 없이.</p>
</div>
""", unsafe_allow_html=True)

# =========================
# 사용방법 카드
# =========================

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">사용방법</div>', unsafe_allow_html=True)
st.markdown("""
1. 이미지 업로드 (최대 10개)<br>
2. 이미지 간격 0~100px 조정<br>
3. 생성하기 버튼 클릭하면 끝
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# =========================
# 업로드 카드
# =========================

st.markdown('<div class="card">', unsafe_allow_html=True)

st.markdown('<div class="section-title">상세페이지 생성</div>', unsafe_allow_html=True)

max_files = 30 if st.session_state.is_pro else 10

uploaded = st.file_uploader(
    f"이미지 업로드 (최대 {max_files}개)",
    type=["jpg","jpeg","png"],
    accept_multiple_files=True
)

if uploaded:
    st.session_state.uploaded_files = uploaded

gap = st.slider("이미지 간격(px)", 0, 100, 20)

st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
generate = st.button("생성하기 (JPG)")
st.markdown('</div>', unsafe_allow_html=True)

# =========================
# 생성 로직
# =========================

def build_detail(images, gap):
    widths = [im.width for im in images]
    max_w = max(widths)
    total_h = 200 + sum([im.height for im in images]) + gap*(len(images)-1)

    canvas = Image.new("RGB", (max_w, total_h), (255,255,255))
    y = 100
    for im in images:
        x = (max_w - im.width)//2
        canvas.paste(im, (x,y))
        y += im.height + gap
    return canvas

if generate:
    if not st.session_state.uploaded_files:
        st.error("이미지를 업로드해주세요.")
    else:
        imgs = []
        for f in st.session_state.uploaded_files:
            img = Image.open(f)
            if img.mode == "RGBA":
                bg = Image.new("RGB", img.size, (255,255,255))
                bg.paste(img, mask=img.split()[-1])
                img = bg
            imgs.append(img)

        result = build_detail(imgs, gap)

        buf = io.BytesIO()
        result.save(buf, format="JPEG", quality=95)

        st.success("상세페이지 생성 완료")

        st.download_button(
            "다운로드",
            data=buf.getvalue(),
            file_name="misharp_detail.jpg",
            mime="image/jpeg"
        )

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# 하단 소개
# =========================

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">이 툴은 누가 만들었나요?</div>', unsafe_allow_html=True)
st.markdown("""
20년차 여성의류 온라인 쇼핑몰 대표가 사내에서 사용하기 위해 직접 제작한 프로그램입니다.<br>
단순 반복 업무는 줄이고, 상세페이지 퀄리티는 더 높이세요.
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div class='small-text' style='text-align:center;'>© MISHARP</div>", unsafe_allow_html=True)
