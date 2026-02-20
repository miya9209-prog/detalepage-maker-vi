import io
import os
from dataclasses import dataclass
from typing import Any, List, Set, Tuple

import pandas as pd
import streamlit as st
from PIL import Image

# =========================
# 0) PAGE
# =========================
st.set_page_config(
    page_title="misharp detalepage maker v1",
    page_icon="🧷",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PASSWORD_FILE = "비번리스트.xlsx"
PRO_CONTACT_EMAIL = "misharpmail@naver.com"

# =========================
# 1) MOCKUP COPY (고정)
# =========================
TOP_LEFT_TEXT = "MISHARP DETAIL PAGE MAKER V1-FREE VERSION"

MAIN_TITLE = "MS 상세페이지 자동생성기 [FREE]"
MAIN_SUB_RED = "상세페이지 이미지를 자동으로 생성하여 디자이너의 단순업무시간을 대폭 줄여드립니다."

HOWTO_ONELINE = "1. 이미지 업로드(최대 10개)   2. 이미지 간격 0~100PX 조정   3. 생성하기 버튼 클릭하면 끝!"
FREE_NOTICE = "*FREE 버전에서 미리보기는 지원되지 않습니다."

MID_RED_1 = (
    "MS 상세페이지 생성기는 20년차 여성의류 인터넷 쇼핑몰 대표가 사내에서 사용하기 위해 직접 제작한 프로그램으로\n"
    "실제 온라라인 쇼핑몰 디자인 작업에 적용하고 있으며, 디자이너의 요구사항을 최대한 반영하여 구현한 최고의 툴 입니다.\n\n"
    "MS 업무툴을 통해 단순업무 시간은 줄이고 상세페이지의 퀄리티는 더욱 높이세요."
)

GUIDE_TITLE = "MS 상세페이지 생성기 사용안내"
GUIDE_LINES = [
    "1. 사전에 보정작업을 마친 상세페이지이용 이미지를 파일선택 버튼으로 선택(최대 10개 가능.)",
    "   상세페이지 최적화를 위해 1개 상세페이지당 5개 이미지 구성 추천",
    "2. 이미지간격 버튼 이용해 이미지간 간격 조정(0~100PX까지 선택/1개 상세페이지당 일괄 적용)",
    "3. 상세페이지 생성 시 최상단과 최하단은 100PX 여백은 고정 생성",
    "4. 생성하기 버튼 클릭 하면 상세페이지 완성",
    "5. 상세페이지 내에 텍스트를 구성하고자 하는 경우 텍스트 편집된 JPG 이미지를 만들어 추가하는 방식으로 활용하세요.",
    "6. 새 작업을 시작하기 위해서는 초기화를 클릭해주세요.",
]

PSD_TITLE = "PSD(고급개체 레이어)가 필요하신가요?"
PSD_DESC = "MS PRO는 수정가능한 상세페이지 PSD 다운로드가 가능합니다.(레이어/고급개체 기반)"
PSD_BULLETS = [
    "→PSD로 빠르고 해상도 높은 작업이 필요할 때",
    "→고급개체(SMART OBJECTS) 레이어 작업이 필요할 때",
    "→반복적인 템플릿이 필요할 때",
    "→업로드 파일 미리보기 제공 등 좀 더 다양한 기능이 필요할 때",
]
PSD_BOTTOM = "MS PRO는 상세페이지 웹디자이너에게 최고의 도구가 되어줍니다."

PRO_TOOL_TITLE = "PRO 버전은 디자이너를 위한 최고의 툴도 아래와 같이 제공합니다."
PRO_TOOLS: List[Tuple[str, str]] = [
    ("GIF 자동 생성기", "간략설명"),
    ("썸메일 메이커", "간략설명"),
    ("이미지 자르기 툴", "간략설명"),
]

FOOTER_COPY = "카피라이트 문구"

# =========================
# 2) PRO 비번 로드
# =========================
@st.cache_data(show_spinner=False)
def load_passwords_from_excel() -> Set[str]:
    if not os.path.exists(PASSWORD_FILE):
        return set()
    df = pd.read_excel(PASSWORD_FILE)
    cols_lower = {str(c).strip().lower(): c for c in df.columns}
    col = cols_lower.get("password", df.columns[0])
    vals = df[col].astype(str).str.strip().replace({"nan": "", "None": "", "NONE": ""})
    return set([v for v in vals.tolist() if v])

# =========================
# 3) STATE (TypeError 완전 차단)
# =========================
@dataclass
class Item:
    name: str
    data: bytes

def _is_uploaded_file(obj: Any) -> bool:
    return hasattr(obj, "name") and hasattr(obj, "getvalue")

def force_items_list() -> List[Item]:
    raw = st.session_state.get("items", None)

    if raw is None:
        st.session_state["items"] = []
        return []

    if isinstance(raw, list) and all(isinstance(x, Item) for x in raw):
        return raw

    if _is_uploaded_file(raw):
        items = [Item(name=raw.name, data=raw.getvalue())]
        st.session_state["items"] = items
        return items

    if isinstance(raw, list):
        out: List[Item] = []
        for x in raw:
            if isinstance(x, Item):
                out.append(x)
            elif _is_uploaded_file(x):
                out.append(Item(name=x.name, data=x.getvalue()))
        st.session_state["items"] = out
        return out

    st.session_state["items"] = []
    return []

def init_state():
    if "is_pro" not in st.session_state:
        st.session_state["is_pro"] = False
    if "show_pro_panel" not in st.session_state:
        st.session_state["show_pro_panel"] = False
    force_items_list()

def add_uploads(files, clear_first: bool):
    items = [] if clear_first else force_items_list()
    for f in files:
        items.append(Item(name=f.name, data=f.getvalue()))
    st.session_state["items"] = items

def move_item(idx: int, direction: int):
    items = force_items_list()
    new_idx = idx + direction
    if new_idx < 0 or new_idx >= len(items):
        return
    items[idx], items[new_idx] = items[new_idx], items[idx]
    st.session_state["items"] = items

def delete_item(idx: int):
    items = force_items_list()
    if 0 <= idx < len(items):
        items.pop(idx)
    st.session_state["items"] = items

# =========================
# 4) IMAGE BUILD
# =========================
def load_image(file_bytes: bytes) -> Image.Image:
    img = Image.open(io.BytesIO(file_bytes))
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1])
        img = bg
    return img

def build_detail_image(images: List[Image.Image], gap: int, pad_top_bottom: int = 100) -> Image.Image:
    max_w = max(im.width for im in images)
    total_h = pad_top_bottom * 2 + sum(im.height for im in images) + gap * (len(images) - 1)
    canvas = Image.new("RGB", (max_w, total_h), (255, 255, 255))
    y = pad_top_bottom
    for im in images:
        x = (max_w - im.width) // 2
        canvas.paste(im, (x, y))
        y += im.height + gap
    return canvas

# =========================
# 5) CSS (상단 여백/타이틀/드롭존 축소/불필요 박스 제거)
# =========================
def inject_css():
    st.markdown(
        """
        <style>
        /* ✅ 상단 여백 확보(타이틀 안 잘리게) */
        .block-container{max-width:1240px; padding-top:72px; padding-bottom:52px;}

        [data-testid="stAppViewContainer"]{
          background:
            radial-gradient(1100px 520px at 18% 0%, rgba(255, 228, 241, 0.60), transparent 60%),
            radial-gradient(1100px 520px at 85% 0%, rgba(224, 246, 255, 0.65), transparent 60%),
            linear-gradient(180deg, #ffffff 0%, #fbfbfd 100%);
        }

        /* 목업 박스 */
        .box{
          border:1px solid rgba(15,23,42,0.55);
          border-radius:10px;
          background:#fff;
          padding:14px 16px;
        }
        .box-thin{
          border:1px solid rgba(15,23,42,0.35);
          border-radius:10px;
          background:#fff;
          padding:10px 12px;
        }

        /* 타이포 */
        .t-center{text-align:center;}
        .h-title{font-size:44px; font-weight:950; margin:0; color:#0b0f1a; letter-spacing:-0.6px;}
        .sub-red{margin-top:8px; font-size:15px; font-weight:900; color:#d81b1b;}
        .h2{font-size:26px; font-weight:950; margin:0 0 10px 0; color:#0b0f1a;}
        .body{font-size:15px; line-height:1.75; color:#0b0f1a;}
        .mini{font-size:13px; line-height:1.65; color:rgba(15,23,42,0.75);}

        /* 광고배너(좌/우) */
        .ad{
          height: 430px;
          border-radius:10px;
          background: rgba(15,23,42,0.06);
          border:1px solid rgba(15,23,42,0.20);
          display:flex;
          align-items:flex-start;
          justify-content:center;
          padding-top:18px;
          font-weight:900;
          color:rgba(15,23,42,0.70);
        }

        /* 버튼 */
        div.stButton>button{
          border-radius:6px !important;
          font-weight:950 !important;
          padding:0.62rem 0.95rem !important;
          border:1px solid rgba(15,23,42,0.45) !important;
        }
        div.stButton>button[kind="primary"]{
          background:#ffe600 !important;
          color:#0b0f1a !important;
          border:1px solid rgba(15,23,42,0.55) !important;
        }

        /* ✅ 파일업로더 '큰 박스'를 목업처럼 최대한 축소 */
        [data-testid="stFileUploader"] section{
          padding:10px 10px !important;
        }
        [data-testid="stFileUploader"]{
          border:1px solid rgba(15,23,42,0.55) !important;
          border-radius:4px !important;
          background:#fff !important;
        }
        [data-testid="stFileUploader"] small{display:none !important;} /* limit 문구 숨김 */
        [data-testid="stFileUploader"] svg{display:none !important;}   /* 구름 아이콘 숨김 */
        [data-testid="stFileUploader"] div[role="button"]{
          background:#fff !important;
          border-radius:0px !important;
        }

        /* ✅ 체크박스(검은 네모) 숨기기: '기존 목록 지우고' 옵션은 Advanced로 내림 */
        .adv-hide label {display:none !important;}
        </style>
        """,
        unsafe_allow_html=True,
    )

# =========================
# 6) UI
# =========================
def top_bar():
    a, b = st.columns([0.78, 0.22], vertical_alignment="center")
    with a:
        st.markdown(f"<div class='mini'><b>{TOP_LEFT_TEXT}</b></div>", unsafe_allow_html=True)
    with b:
        if st.button("PRO신청", use_container_width=True):
            st.session_state["show_pro_panel"] = not st.session_state["show_pro_panel"]

    if st.session_state["show_pro_panel"]:
        passwords = load_passwords_from_excel()
        st.markdown(
            f"""
            <div class="box">
              <div class="h2">PRO신청</div>
              <div class="mini"><b>사용 및 PRO 문의 : {PRO_CONTACT_EMAIL}</b></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not passwords:
            st.error("비번리스트.xlsx를 찾지 못했습니다. app.py와 같은 위치(저장소 루트)에 업로드되어야 합니다.")
            return

        pw = st.text_input("비밀번호 입력", type="password", placeholder="발급받은 비밀번호 입력")
        if st.button("확인", use_container_width=False, key="pro_ok"):
            if pw and pw.strip() in passwords:
                st.session_state["is_pro"] = True
                st.success("PRO 활성화 완료")
            else:
                st.error("비밀번호가 올바르지 않습니다.")

def hero():
    st.markdown(
        f"""
        <div class="t-center">
          <h1 class="h-title">{MAIN_TITLE}</h1>
          <div class="sub-red">{MAIN_SUB_RED}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="box t-center">
          <div class="body"><b>*사용방법*</b></div>
          <div class="body" style="margin-top:6px;"><b>{HOWTO_ONELINE}</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def work_area():
    left_ad, center, right_ad = st.columns([0.16, 0.68, 0.16], vertical_alignment="top")

    with left_ad:
        st.markdown("<div class='ad'>광고배너영역</div>", unsafe_allow_html=True)
    with right_ad:
        st.markdown("<div class='ad'>광고배너영역</div>", unsafe_allow_html=True)

    with center:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # 1행: 파일선택 / (JPG,PNG) / 이미지간격 / 생성하기
        c1, c2, c3, c4 = st.columns([0.32, 0.16, 0.22, 0.30], vertical_alignment="center")

        is_pro = st.session_state.get("is_pro", False)
        max_files = 30 if is_pro else 10

        with c1:
            st.markdown("<div class='mini'><b>파일선택</b></div>", unsafe_allow_html=True)
            files = st.file_uploader(
                "",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True,
                label_visibility="collapsed",
                key="uploader",
            )

        with c2:
            st.markdown("<div class='mini' style='margin-top:18px;'><b>(JPG, PNG)</b></div>", unsafe_allow_html=True)

        with c3:
            st.markdown("<div class='mini'><b>이미지 간격</b> <span class='mini'>(0~100PX)</span></div>", unsafe_allow_html=True)
            gap = st.number_input("", min_value=0, max_value=100, value=int(st.session_state.get("gap_val", 20)), step=1, key="gap_val")

        with c4:
            st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
            gen = st.button("생성하기 (JPG)", type="primary", use_container_width=True)

        # ✅ Advanced 옵션으로 내림(검은 네모 제거)
        with st.expander("고급 옵션", expanded=False):
            clear_first = st.checkbox("기존 목록 지우고 새로 추가", value=False, key="clear_first")
        clear_first_val = bool(st.session_state.get("clear_first", False))

        if files:
            if len(files) > max_files:
                st.warning(f"최대 {max_files}개까지 업로드 가능합니다. (현재 {len(files)}개)")
            else:
                add_uploads(files, clear_first_val)

        items = force_items_list()

        # 업로드 파일명 박스
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        st.markdown("<div class='box'>", unsafe_allow_html=True)
        st.markdown("<div class='body'><b>업로드 파일명</b></div>", unsafe_allow_html=True)
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        colL, colR = st.columns(2, vertical_alignment="top")
        left_items = items[:5]
        right_items = items[5:10]

        def render_list(target_col, offset, subset: List[Item]):
            with target_col:
                if not subset:
                    st.markdown("<div class='mini'>-</div>", unsafe_allow_html=True)
                for j, it in enumerate(subset):
                    i = offset + j
                    r1, r2, r3, r4 = st.columns([0.55, 0.15, 0.15, 0.15], vertical_alignment="center")
                    with r1:
                        st.markdown(f"<div class='mini'>파일{i+1}</div>", unsafe_allow_html=True)
                    with r2:
                        if st.button("▼", key=f"down_{i}", use_container_width=True):
                            move_item(i, +1)
                            st.rerun()
                    with r3:
                        if st.button("▲", key=f"up_{i}", use_container_width=True):
                            move_item(i, -1)
                            st.rerun()
                    with r4:
                        if st.button("X", key=f"del_{i}", use_container_width=True):
                            delete_item(i)
                            st.rerun()

        render_list(colL, 0, left_items)
        render_list(colR, 5, right_items)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='mini'><b>{FREE_NOTICE}</b></div>", unsafe_allow_html=True)

        # 초기화 버튼: 박스 우하단 느낌
        rbtn = st.columns([0.82, 0.18], vertical_alignment="center")
        with rbtn[1]:
            if st.button("초기화", use_container_width=True, key="reset_btn"):
                st.session_state["items"] = []
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # 생성/다운로드
        if gen:
            items = force_items_list()
            if not items:
                st.error("이미지를 먼저 업로드해 주세요.")
            else:
                imgs = [load_image(it.data) for it in items]
                out = build_detail_image(imgs, gap=int(gap), pad_top_bottom=100)
                buf = io.BytesIO()
                out.save(buf, format="JPEG", quality=95, optimize=True)

                st.download_button(
                    "다운로드 (JPG)",
                    data=buf.getvalue(),
                    file_name="misharp_detail.jpg",
                    mime="image/jpeg",
                    use_container_width=True,
                    key="download_btn",
                )

def mid_red_block():
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="box" style="background:rgba(15,23,42,0.04);">
          <div class="body" style="white-space:pre-line; color:#d81b1b; font-weight:950; text-align:center;">
            {MID_RED_1}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def guide_block():
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    lines_html = "".join([f"<div class='mini'>{ln}</div>" for ln in GUIDE_LINES])
    st.markdown(
        f"""
        <div class="box">
          <div class="h2">{GUIDE_TITLE}</div>
          {lines_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

def psd_block():
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    bullets_html = "".join([f"<div class='mini' style='color:#d81b1b; font-weight:950;'>{b}</div>" for b in PSD_BULLETS])
    st.markdown(
        f"""
        <div class="box">
          <div class="h2">{PSD_TITLE}</div>
          <div class="body"><b>{PSD_DESC}</b></div>
          <div style="height:8px"></div>
          {bullets_html}
          <div style="height:8px"></div>
          <div class="body"><b>{PSD_BOTTOM}</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def pro_tools_block():
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='h2'>{PRO_TOOL_TITLE}</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, vertical_alignment="top")
    cols = [c1, c2, c3]
    for i, (name, desc) in enumerate(PRO_TOOLS):
        with cols[i]:
            st.markdown(
                f"""
                <div class="box-thin">
                  <div class="body"><b>{name}</b></div>
                  <div class="mini">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='mini'><b>사용 및 PRO 문의 : {PRO_CONTACT_EMAIL}</b></div>", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    if st.button("PRO신청", use_container_width=False, key="pro_bottom"):
        st.session_state["show_pro_panel"] = True
        st.rerun()

def footer():
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='mini' style='text-align:left;'>{FOOTER_COPY}</div>", unsafe_allow_html=True)

def main():
    init_state()
    inject_css()

    top_bar()
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    hero()
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    work_area()

    mid_red_block()
    guide_block()
    psd_block()
    pro_tools_block()
    footer()

if __name__ == "__main__":
    main()
