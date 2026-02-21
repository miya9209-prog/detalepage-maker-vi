import streamlit as st
from PIL import Image
import io
import os
import base64
from typing import List, Optional, Tuple

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
PRO_APPLY_URL = "#"  # 필요시 교체

UPLOADER_KEY = "uploader_files"
RESET_FLAG_KEY = "do_reset"

# =========================================================
# SESSION STATE INIT
# =========================================================
if "files" not in st.session_state:
    st.session_state["files"] = []  # List[Tuple[name, bytes, PIL.Image]]
if "seen_keys" not in st.session_state:
    st.session_state["seen_keys"] = set()  # set of (name, size)
if "result_bytes" not in st.session_state:
    st.session_state["result_bytes"] = None
if "result_filename" not in st.session_state:
    st.session_state["result_filename"] = "detail_page.jpg"
if RESET_FLAG_KEY not in st.session_state:
    st.session_state[RESET_FLAG_KEY] = False

# =========================================================
# ✅ SAFE RESET HANDLING (위젯 생성 전에만 uploader key 삭제)
# =========================================================
if st.session_state.get(RESET_FLAG_KEY, False):
    # 1) 커스텀 상태 초기화
    st.session_state["files"] = []
    st.session_state["seen_keys"] = set()
    st.session_state["result_bytes"] = None
    st.session_state["result_filename"] = "detail_page.jpg"

    # 2) uploader 위젯 상태 삭제(위젯 생성 "이전"이라 안전)
    st.session_state.pop(UPLOADER_KEY, None)

    # 3) 플래그 해제
    st.session_state[RESET_FLAG_KEY] = False

# =========================================================
# CSS
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
  --accent:#ffcc00;
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

/* ---------- Ads (빈칸 제거: aspect-ratio) ---------- */
.ad-wrapper{{
  width:100%;
  display:flex;
  justify-content:center;
  margin-top: var(--s4);
}}
.ad-box{{
  width: 100%;
  max-width: {AD_W}px;
  aspect-ratio: {AD_W} / {AD_H};
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
  object-fit: cover;
  display:block;
}}
.ad-empty{{
  width:100%;
  height:100%;
  display:flex;
  align-items:center;
  justify-content:center;
  text-align:center;
  padding: 14px;
  color:#98A2B3;
  font-weight: 900;
  line-height:1.4;
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

/* 업로더 큰 흰박스/내장 목록 숨김 */
div[data-testid="stFileUploader"] label {{ display:none !important; }}
div[data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] {{ display:none !important; }}
div[data-testid="stFileUploader"] > div {{
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
  margin: 0 !important;
}}
div[data-testid="stFileUploaderDropzone"] {{
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
  margin: 0 !important;
}}
div[data-testid="stFileUploaderDropzone"] ul {{ display:none !important; }}

/* buttons */
.stButton>button{{
  border-radius: 12px !important;
  font-weight: 950 !important;
  height: 54px !important;
}}
div[data-testid="stButton"]#generate_btn > button{{
  background: var(--accent) !important;
  color: #111 !important;
  border: 0 !important;
}}
div[data-testid="stButton"]#reset_btn > button{{
  background: #fff !important;
  color: #111 !important;
  border: 1px solid var(--border) !important;
}}
div[data-testid="stDownloadButton"] > button{{
  background: var(--primary) !important;
  color: #fff !important;
  border: 0 !important;
  height: 52px !important;
  border-radius: 12px !important;
  font-weight: 950 !important;
}}

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

def file_key(name: str, size: int) -> Tuple[str, int]:
    return (name, int(size))

def add_uploaded_files(uploaded) -> None:
    """✅ rerun 되어도 같은 파일은 추가되지 않도록 seen_keys로 중복 방지"""
    if not uploaded:
        return

    for uf in uploaded:
        if len(st.session_state["files"]) >= MAX_FILES:
            break

        k = file_key(uf.name, getattr(uf, "size", 0) or 0)
        if k in st.session_state["seen_keys"]:
            continue  # ✅ 이미 등록된 파일이면 스킵

        file_bytes = uf.read()
        try:
            img = safe_open_image(file_bytes)
        except Exception:
            continue

        st.session_state["files"].append((uf.name, file_bytes, img))
        st.session_state["seen_keys"].add(k)

def move_file(idx: int, direction: int) -> None:
    files = st.session_state["files"]
    new_idx = idx + direction
    if 0 <= idx < len(files) and 0 <= new_idx < len(files):
        files[idx], files[new_idx] = files[new_idx], files[idx]
        st.session_state["files"] = files

def remove_file(idx: int) -> None:
    files = st.session_state["files"]
    if 0 <= idx < len(files):
        name, _b, _img = files[idx]
        # seen_keys에서도 제거(같은 파일 다시 업로드 가능하도록)
        # size는 uploader 없이 알기 어려워서 name 기반 삭제는 위험 -> 일단 전체 재구축 방식으로 안전하게 처리
        files.pop(idx)
        st.session_state["files"] = files

        # ✅ seen_keys 재구축(현재 files 기준으로)
        new_seen = set()
        for (n, bts, _i) in st.session_state["files"]:
            new_seen.add((n, len(bts)))  # bytes 길이로 대체 키
        st.session_state["seen_keys"] = new_seen

def request_reset() -> None:
    # ✅ 위젯 키를 직접 건드리지 말고 플래그만 세팅
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
    try:
        ext = os.path.splitext(path)[1].lower().replace(".", "")
        mime = "png" if ext == "png" else "jpeg"
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/{mime};base64,{b64}"
    except Exception:
        return None

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
    else:
        st.markdown(
            f"""
<div class="ad-box">
  <div class="ad-empty">
    광고 이미지 없음<br><br>
    <b>{AD_W} x {AD_H}px</b><br>
    {img_path}
  </div>
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
      <a href="{PRO_APPLY_URL}" target="_blank"><span class="pill">PRO신청</span></a>
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
        # ✅ 0~300으로 확장
        gap = st.slider("이미지 간격 (0~300PX)", 0, 300, 50)
    with cB:
        st.markdown("<div id='generate_btn'></div>", unsafe_allow_html=True)
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
        st.markdown("<div id='reset_btn'></div>", unsafe_allow_html=True)
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
