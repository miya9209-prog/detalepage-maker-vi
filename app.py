import streamlit as st
from PIL import Image
import io
import os
import base64
import hashlib
from typing import List, Optional

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="MS 상세페이지 자동생성기",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================================================
# CONSTANTS
# =========================================================
MAX_FILES = 10

ASSETS_DIR = "assets"
AD_LEFT_PATH = os.path.join(ASSETS_DIR, "ad_left.png")
AD_RIGHT_PATH = os.path.join(ASSETS_DIR, "ad_right.png")
TOP_BANNER_PATH = os.path.join(ASSETS_DIR, "top_banner.png")

AD_W = 300
AD_H = 600

MISHARP_URL = "https://www.misharp.co.kr"
PRO_APPLY_URL = "https://www.misharp.co.kr"

UPLOADER_KEY = "uploader_files"
RESET_FLAG_KEY = "do_reset"

# =========================================================
# SESSION STATE INIT
# =========================================================
if "files" not in st.session_state:
    st.session_state["files"] = []  # list[(name, bytes, PIL)]
if "seen_hashes" not in st.session_state:
    st.session_state["seen_hashes"] = set()
if "result_bytes" not in st.session_state:
    st.session_state["result_bytes"] = None
if "result_filename" not in st.session_state:
    st.session_state["result_filename"] = "detail_page.jpg"
if RESET_FLAG_KEY not in st.session_state:
    st.session_state[RESET_FLAG_KEY] = False

# =========================================================
# SAFE RESET HANDLING (Streamlit 위젯 키 직접 할당 금지 회피)
# =========================================================
if st.session_state.get(RESET_FLAG_KEY, False):
    st.session_state["files"] = []
    st.session_state["seen_hashes"] = set()
    st.session_state["result_bytes"] = None
    st.session_state["result_filename"] = "detail_page.jpg"
    # file_uploader 위젯 키 제거 (다음 rerun에서 초기화)
    st.session_state.pop(UPLOADER_KEY, None)
    st.session_state[RESET_FLAG_KEY] = False

# =========================================================
# CSS (실서비스 마감)
# =========================================================
st.markdown(
    f"""
<style>
:root{{
  --bg:#ffffff;
  --card:#ffffff;
  --border:#e6e8ef;
  --text:#101828;
  --muted:#667085;
  --danger:#e60012;
  --primary:#111827;
  --shadow:0 10px 30px rgba(16,24,40,.07);

  --s1:16px; --s2:24px; --s3:32px; --s4:40px; --s5:56px;
}}

.stApp{{ background: var(--bg) !important; }}
.block-container{{
  max-width: 1320px;
  padding-top: var(--s3) !important;
  padding-bottom: 70px !important;
}}
html, body, [class*="css"] {{
  font-family: Pretendard, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans KR",
               "Apple SD Gothic Neo", "Malgun Gothic", Arial, sans-serif !important;
}}

/* =========================================================
   ✅ 1) "상단 흰박스" 원인: stTextInput 류 렌더링
   - 이 앱에서는 텍스트 입력창이 필요 없으니 통째로 숨김
   ========================================================= */
div[data-testid="stTextInput"] {{
  display: none !important;
}}

/* ---------- Header ---------- */
.header-wrap{{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: var(--s3);
  box-shadow: var(--shadow);
}}
.header-topline{{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap: 12px;
}}
.brand-small{{
  font-size: 13px;
  font-weight: 900;
  color: #475467;
}}
.pro-btn a{{ text-decoration:none; }}
.pro-btn .pill{{
  background: var(--primary);
  color: #fff;
  padding: 12px 18px;
  border-radius: 12px;
  font-weight: 950;
  min-width: 160px;
  text-align:center;
  display:inline-block;
  box-shadow: 0 8px 18px rgba(17,24,39,.18);
}}
.pro-btn .pill:hover{{
  filter: brightness(0.92);
}}

.main-title{{
  margin-top: 10px;
  font-size: 34px;
  font-weight: 950;
  color: var(--text);
  text-align:center;
}}
.sub-title{{
  margin-top: 8px;
  text-align:center;
  font-size: 15px;
  font-weight: 900;
  color: var(--danger);
}}
.guide{{
  margin-top: var(--s2);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: var(--s2);
  text-align:center;
  color: #344054;
  font-weight: 850;
  line-height: 1.55;
  background:#fff;
}}

/* ---------- Top banner ---------- */
.top-banner-wrap{{
  margin: var(--s4) auto var(--s4) auto;
  max-width: 1320px;
  border: 1px solid var(--border);
  border-radius: 14px;
  overflow:hidden;
  box-shadow: var(--shadow);
}}
.top-banner-wrap a{{ display:block; }}
.top-banner-wrap img{{
  width:100%;
  height:auto;
  display:block;
}}

/* ---------- Ads ---------- */
.ad-wrapper{{
  width:100%;
  display:flex;
  justify-content:center;
  margin-top: var(--s4);
}}
.ad-box{{
  width: 100%;
  max-width: {AD_W}px;
  height: {AD_H}px;               /* ✅ 고정 높이로 박스 유지 */
  border:1px solid var(--border);
  border-radius:14px;
  overflow:hidden;
  background:#fff;
  box-shadow: var(--shadow);
}}
.ad-box a{{ display:block; width:100%; height:100%; }}
.ad-box img{{
  width:100%;
  height:100%;
  object-fit: contain;            /* ✅ [수정] cover → contain (잘림 방지) */
  object-position: center;        /* ✅ [추가] 중앙정렬 */
  display:block;
}}

/* ---------- Work Area ---------- */
.section-card{{
  background:#fff;
  border:1px solid var(--border);
  border-radius:16px;
  box-shadow: var(--shadow);
  padding: var(--s3);
  margin-top: var(--s4);
}}
.section-title{{
  font-size: 22px;
  font-weight: 950;
  color: var(--text);
  margin-bottom: var(--s1);
}}
.small-muted{{
  font-size: 13px;
  color: var(--muted);
  font-weight: 800;
}}
.hr-soft{{
  height:1px;
  background: var(--border);
  margin: var(--s2) 0 var(--s2) 0;
}}

/* ---------- File uploader: 불필요한 라벨/빈 영역 제거 ---------- */
div[data-testid="stFileUploader"] label {{
  display:none !important;
}}
div[data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] {{
  display:none !important;
}}
div[data-testid="stFileUploader"] > div {{
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
  margin: 0 !important;
  min-height: 0 !important;
}}
div[data-testid="stFileUploaderDropzone"] {{
  border-radius: 14px !important;
  border: 1px solid var(--border) !important;
  background: #0b1220 !important;
  padding: 18px !important;
}}
div[data-testid="stFileUploaderDropzone"] * {{
  color: #fff !important;
}}
div[data-testid="stFileUploaderDropzone"] ul {{
  display:none !important;
}}
div[data-testid="stFileUploaderDropzone"] button {{
  background: rgba(255,255,255,.08) !important;
  border: 1px solid rgba(255,255,255,.18) !important;
  color: #fff !important;
  border-radius: 10px !important;
  font-weight: 900 !important;
}}
div[data-testid="stFileUploaderDropzone"] button:hover {{
  background: rgba(255,255,255,.14) !important;
}}

/* =========================================================
   ✅ 2) 버튼 hover 시 흰색으로 변하는 문제 해결
   ========================================================= */
.stButton>button{{
  border-radius: 12px !important;
  font-weight: 950 !important;
  height: 54px !important;
  border: 0 !important;
  background: var(--primary) !important;
  color: #fff !important;
}}
.stButton>button:hover{{
  background: var(--primary) !important;
  color: #fff !important;
  filter: brightness(0.92) !important;
}}
.stButton>button:active{{
  background: var(--primary) !important;
  color: #fff !important;
  filter: brightness(0.88) !important;
}}
.stButton>button:focus{{
  outline: none !important;
  box-shadow: 0 0 0 3px rgba(17,24,39,.12) !important;
}}

/* 다운로드 버튼도 동일 톤 */
div[data-testid="stDownloadButton"] > button{{
  background: var(--primary) !important;
  color: #fff !important;
  border: 0 !important;
  height: 52px !important;
  border-radius: 12px !important;
  font-weight: 950 !important;
}}
div[data-testid="stDownloadButton"] > button:hover{{
  background: var(--primary) !important;
  color: #fff !important;
  filter: brightness(0.92) !important;
}}

/* 파일 리스트 조작 버튼 */
.file-name{{
  font-weight: 900;
  color: #344054;
  font-size: 14px;
  overflow:hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 520px;
}}
.small-btn button{{
  height: 40px !important;
  min-width: 44px !important;
  padding: 0 12px !important;
  border-radius: 10px !important;
  background: var(--primary) !important;
  color: #fff !important;
  font-weight: 950 !important;
}}
.small-btn button:hover{{
  background: var(--primary) !important;
  color:#fff !important;
  filter: brightness(0.92) !important;
}}

/* ---------- Bottom sections ---------- */
.marketing{{
  margin-top: var(--s5);
  background:#fff;
  border:1px solid var(--border);
  border-radius:14px;
  padding: var(--s3);
  text-align:center;
  color: var(--danger);
  font-weight: 900;
  line-height: 1.65;
  box-shadow: var(--shadow);
}}
.tool-card{{
  background:#fff;
  border:1px solid var(--border);
  border-radius:14px;
  box-shadow: var(--shadow);
  padding: var(--s3);
  min-height: 160px;
}}
.tool-title{{
  font-size: 16px;
  font-weight: 950;
  color: var(--text);
  margin-bottom: 8px;
}}
.tool-desc{{
  font-size: 13px;
  color: #667085;
  font-weight: 780;
  line-height: 1.55;
}}
.bottom-cta{{
  text-align:center;
  margin-top: var(--s4);
}}
.bottom-cta a{{
  background: var(--primary);
  color:#fff;
  padding: 14px 42px;
  border-radius: 14px;
  font-weight: 950;
  font-size: 18px;
  text-decoration:none;
  display:inline-block;
  box-shadow: 0 10px 24px rgba(17,24,39,.22);
}}
.bottom-cta a:hover{{
  filter: brightness(0.92);
}}
.contact-box{{
  margin-top: var(--s3);
  text-align:center;
  background:#fff;
  border:1px solid var(--border);
  border-radius:14px;
  padding: var(--s3);
  box-shadow: var(--shadow);
}}
.contact-box .label{{
  font-size: 16px;
  font-weight: 950;
  color: var(--text);
}}
.contact-box .email{{
  font-size: 20px;
  font-weight: 950;
  color: var(--danger);
  margin-top: 6px;
}}
.copyright{{
  margin-top: var(--s3);
  text-align:center;
  font-size: 13px;
  color:#98A2B3;
  font-weight: 700;
}}
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# HELPERS
# =========================================================
def safe_open_image(file_bytes: bytes) -> Image.Image:
    img = Image.open(io.BytesIO(file_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    return img

def bytes_hash(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def add_uploaded_files(uploaded) -> None:
    if not uploaded:
        return
    for uf in uploaded:
        if len(st.session_state["files"]) >= MAX_FILES:
            break
        file_bytes = uf.read()
        h = bytes_hash(file_bytes)
        if h in st.session_state["seen_hashes"]:
            continue
        try:
            img = safe_open_image(file_bytes)
        except Exception:
            continue
        st.session_state["files"].append((uf.name, file_bytes, img))
        st.session_state["seen_hashes"].add(h)

def move_file(idx: int, direction: int) -> None:
    files = st.session_state["files"]
    new_idx = idx + direction
    if 0 <= idx < len(files) and 0 <= new_idx < len(files):
        files[idx], files[new_idx] = files[new_idx], files[idx]
        st.session_state["files"] = files

def rebuild_seen_hashes() -> None:
    st.session_state["seen_hashes"] = {bytes_hash(b) for (_n, b, _i) in st.session_state["files"]}

def remove_file(idx: int) -> None:
    files = st.session_state["files"]
    if 0 <= idx < len(files):
        files.pop(idx)
        st.session_state["files"] = files
        rebuild_seen_hashes()

def request_reset() -> None:
    st.session_state[RESET_FLAG_KEY] = True
    st.rerun()

def build_stacked_image(images: List[Image.Image], gap: int) -> Image.Image:
    widths, heights = zip(*(im.size for im in images))
    total_h = sum(heights) + gap * (len(images) - 1 if len(images) > 1 else 0)
    max_w = max(widths)
    canvas = Image.new("RGB", (max_w, total_h), (255, 255, 255))
    y = 0
    for im in images:
        canvas.paste(im, (0, y))
        y += im.height + gap
    return canvas

def img_to_data_uri(path: str) -> Optional[str]:
    if not os.path.exists(path):
        return None
    ext = os.path.splitext(path)[1].lower().replace(".", "")
    mime = "png" if ext == "png" else "jpeg"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/{mime};base64,{b64}"

def render_ad_box(img_path: str) -> None:
    uri = img_to_data_uri(img_path)
    st.markdown('<div class="ad-wrapper">', unsafe_allow_html=True)
    if uri:
        st.markdown(
            f"""
<div class="ad-box">
  <a href="{MISHARP_URL}" target="_blank" rel="noopener">
    <img src="{uri}" alt="ad">
  </a>
</div>
""",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
st.markdown(
    f"""
<div class="header-wrap">
  <div class="header-topline">
    <div class="brand-small">MISHARP DETAIL PAGE MAKER V1 - FREE VERSION</div>
    <div class="pro-btn">
      <a href="{PRO_APPLY_URL}" target="_blank" rel="noopener"><span class="pill">PRO신청</span></a>
    </div>
  </div>

  <div class="main-title">MS 상세페이지 자동생성기 [FREE]</div>
  <div class="sub-title">상세페이지 이미지를 자동으로 생성하여 디자이너의 단순업무시간을 대폭 줄여드립니다.</div>

  <div class="guide">
    <b>*사용방법*</b><br>
    1) 이미지 업로드(최대 10개) &nbsp;&nbsp; 2) 이미지 간격(0~300px) 조정 &nbsp;&nbsp; 3) 생성하기 버튼 클릭하면 끝!
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# =========================================================
# TOP BANNER (click -> misharp)
# =========================================================
top_uri = img_to_data_uri(TOP_BANNER_PATH)
if top_uri:
    st.markdown(
        f"""
<div class="top-banner-wrap">
  <a href="{MISHARP_URL}" target="_blank" rel="noopener">
    <img src="{top_uri}" alt="top banner">
  </a>
</div>
""",
        unsafe_allow_html=True,
    )

# =========================================================
# MAIN LAYOUT
# =========================================================
left_col, center_col, right_col = st.columns([1.2, 3, 1.2], gap="large")

with left_col:
    render_ad_box(AD_LEFT_PATH)

with right_col:
    render_ad_box(AD_RIGHT_PATH)

with center_col:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    st.markdown('<div class="section-title">파일선택</div>', unsafe_allow_html=True)
    st.markdown('<div class="small-muted">JPG/PNG 파일을 업로드하세요. 최대 10개까지 가능합니다.</div>', unsafe_allow_html=True)
    st.markdown('<div class="hr-soft"></div>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "이미지 업로드",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key=UPLOADER_KEY,
    )
    if uploaded:
        add_uploaded_files(uploaded)

    st.markdown("<div style='height: 22px;'></div>", unsafe_allow_html=True)

    cA, cB = st.columns([2, 1.2], gap="medium")
    with cA:
        gap = st.slider("이미지 간격 (0~300PX)", 0, 300, 50)
    with cB:
        generate_clicked = st.button("생성하기 (JPG)", use_container_width=True)

    st.markdown("<div style='height: 22px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title' style='font-size:16px;'>업로드 파일명</div>", unsafe_allow_html=True)

    if len(st.session_state["files"]) == 0:
        st.info("아직 업로드된 파일이 없습니다.")
    else:
        for i, (name, _bts, _img) in enumerate(st.session_state["files"]):
            row_cols = st.columns([6, 1.2, 1.2, 1.2], gap="small")
            with row_cols[0]:
                st.markdown(f"<div class='file-name'>{i+1}. {name}</div>", unsafe_allow_html=True)
            with row_cols[1]:
                st.markdown("<div class='small-btn'>", unsafe_allow_html=True)
                if st.button("▼", key=f"down_{i}", use_container_width=True):
                    move_file(i, +1)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with row_cols[2]:
                st.markdown("<div class='small-btn'>", unsafe_allow_html=True)
                if st.button("▲", key=f"up_{i}", use_container_width=True):
                    move_file(i, -1)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with row_cols[3]:
                st.markdown("<div class='small-btn'>", unsafe_allow_html=True)
                if st.button("X", key=f"remove_{i}", use_container_width=True):
                    remove_file(i)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='small-muted' style='margin-top: 22px;'>*FREE 버전에서 미리보기는 지원되지 않습니다.</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

    reset_cols = st.columns([1, 1, 1])
    with reset_cols[2]:
        st.button("초기화", use_container_width=True, on_click=request_reset)

    if generate_clicked:
        if len(st.session_state["files"]) == 0:
            st.warning("먼저 이미지를 업로드해주세요.")
        else:
            imgs = [t[2] for t in st.session_state["files"]]
            result_img = build_stacked_image(imgs, gap)
            buf = io.BytesIO()
            result_img.save(buf, format="JPEG", quality=95)
            st.session_state["result_bytes"] = buf.getvalue()
            st.session_state["result_filename"] = "detail_page.jpg"
            st.success("생성 완료! 바로 아래에서 저장하세요.")

    if st.session_state["result_bytes"]:
        st.download_button(
            label="저장하기",
            data=st.session_state["result_bytes"],
            file_name=st.session_state["result_filename"],
            mime="image/jpeg",
            use_container_width=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# BOTTOM SECTION
# =========================================================
st.markdown(
    """
<div class="marketing">
  MS 상세페이지 생성기는 20년차 여성의류 인터넷 쇼핑몰 대표가 사내에서 사용하기 위해 직접 제작한 프로그램으로<br>
  실제 온라인 쇼핑몰 디자인 작업에 적용하고 있으며, 디자이너의 요구사항을 최대한 반영하여 구현한 최고의 툴입니다.<br>
  MS 업무툴로 단순업무 시간은 줄이고 상세페이지의 퀄리티는 더 높이세요.
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("<div style='height: var(--s4);'></div>", unsafe_allow_html=True)

st.markdown(
    """
<div class="section-card">
  <div class="section-title">MS 상세페이지 생성기 사용안내</div>
  <div style="color:#344054; font-weight:750; line-height:1.8; font-size:14px;">
    1. 사전에 보정작업을 마친 상세페이지용 이미지를 파일선택 버튼으로 선택(최대 10개 가능)<br>
    2. 이미지 간격 버튼 이용해 이미지간 간격 조정(0~300PX 선택 / 1개 상세페이지당 일괄 적용)<br>
    3. 생성하기 버튼 클릭하면 상세페이지 완성<br>
    4. 상세페이지 내 텍스트를 구성하고자 하는 경우 텍스트 편집된 JPG 이미지를 만들어 추가하는 방식으로 활용<br>
    5. 새 작업을 시작하기 위해서는 초기화를 클릭
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("<div style='height: var(--s4);'></div>", unsafe_allow_html=True)

st.markdown(
    """
<div class="section-card">
  <div class="section-title">PSD(고급객체 레이어)가 필요하신가요?</div>
  <div style="color:#344054; font-weight:800; line-height:1.8; font-size:14px;">
    MS PRO는 수정 가능한 상세페이지 PSD 다운로드가 가능합니다. (레이어/고급객체 기반)<br><br>
    <span style="color:#e60012; font-weight:950;">→ PSD로 빠르고 해상도 높은 작업이 필요할 때</span><br>
    <span style="color:#e60012; font-weight:950;">→ 고급객체(SMART OBJECTS) 레이어 작업이 필요할 때</span><br>
    <span style="color:#e60012; font-weight:950;">→ 반복적인 템플릿이 필요할 때</span><br>
    <span style="color:#e60012; font-weight:950;">→ 업로드 파일 미리보기 제공 등 좀 더 다양한 기능이 필요할 때</span><br><br>
    MS PRO는 상세페이지 웹디자이너에게 최고의 도구가 되어줍니다.
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("<div style='height: var(--s4);'></div>", unsafe_allow_html=True)

st.markdown(
    "<div class='section-title' style='font-size:24px; font-weight:950; margin-top:0;'>PRO 버전은 디자이너를 위한 최고의 툴도 아래와 같이 제공합니다.</div>",
    unsafe_allow_html=True
)

st.markdown("<div style='height: var(--s2);'></div>", unsafe_allow_html=True)

t1, t2, t3 = st.columns(3, gap="medium")
with t1:
    st.markdown(
        """
<div class="tool-card">
  <div class="tool-title">GIF 자동 생성기</div>
  <div class="tool-desc">
    여러 이미지를 업로드하면 고화질 GIF를 자동으로 생성합니다.<br>
    프레임 간격/속도 최적화로 ‘움직이는 배너’ 제작 시간을 확 줄여드립니다.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
with t2:
    st.markdown(
        """
<div class="tool-card">
  <div class="tool-title">썸네일 메이커</div>
  <div class="tool-desc">
    쇼핑몰 썸네일 규격에 맞춰 자동 리사이즈/중앙정렬을 지원합니다.<br>
    여백/크롭 문제를 최소화해 ‘바로 업로드 가능한 썸네일’을 만들어드립니다.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
with t3:
    st.markdown(
        """
<div class="tool-card">
  <div class="tool-title">이미지 자르기 툴</div>
  <div class="tool-desc">
    상세페이지용 고정비율 컷팅과 흰여백 제거를 빠르게 처리합니다.<br>
    피사체 중심 유지 기준으로 작업 효율을 극대화합니다.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown(
    f"""
<div class="bottom-cta">
  <a href="{PRO_APPLY_URL}" target="_blank" rel="noopener">PRO 신청하기</a>
</div>

<div class="contact-box">
  <div class="label">사용 및 PRO 문의</div>
  <div class="email">misharpmail@naver.com</div>
</div>

<div class="copyright">
  © 2006-2026 MISHARP. All Rights Reserved.
</div>
""",
    unsafe_allow_html=True,
)
