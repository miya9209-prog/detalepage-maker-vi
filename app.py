import io
import os
from dataclasses import dataclass
from typing import Any, List, Set

import pandas as pd
import streamlit as st
from PIL import Image


# =========================================================
# 0) PAGE / TITLE (요청: 타이틀 교체)
# =========================================================
APP_PAGE_TITLE = "misharp detalepage maker v1"  # ✅ 요청 반영
st.set_page_config(
    page_title=APP_PAGE_TITLE,
    page_icon="🧷",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PASSWORD_FILE = "비번리스트.xlsx"
PRO_CONTACT_EMAIL = "misharpmail@naver.com"


# =========================================================
# 1) MOCKUP COPY (PDF 기반 고정)
# =========================================================
BADGE_TEXT = "MISHARP DETAIL PAGE MAKER V1-FREE VERSION"  # 목업 상단 배지

# 목업 하단에 있던 문구들이지만, 사용성을 위해 “메인 타이틀 영역”에 배치
MAIN_TITLE = "misharp detalepage maker v1"  # ✅ 요청 반영 (기존 'MS 상세페이지 자동생성기 [FREE]' 대신)
MAIN_SUBTITLE = "상세페이지 이미지를 자동으로 생성하여 디자이너의 단순업무시간을 대폭 줄여드립니다."

HOWTO_LINE = "*사용방법*  1. 이미지 업로드(최대 10개)  2. 이미지 간격 0~100PX 조정  3. 생성하기 버튼 클릭하면 끝!"

FREE_PREVIEW_NOTICE = "*FREE 버전에서 미리보기는 지원되지 않습니다."

ABOUT_BLOCK = [
    "MS 상세페이지 생성기는 20년차 여성의류 인터넷 쇼핑몰 대표가 사내에서 사용하기 위해 직접 제작한 프로그램으로",
    "실제 온라라인 쇼핑몰 디자인 작업에 적용하고 있으며, 디자이너의 요구사항을 최대한 반영하여 구현한 최고의 툴입니다.",
    "MS 업무툴을 통해 단순업무 시간은 줄이고 상세페이지의 퀄리티는 더욱 높이세요.",
]

GUIDE_TITLE = "MS 상세페이지 생성기 사용안내"
GUIDE_LINES = [
    "1. 사전에 보정작업을 마친 상세페이지용 이미지를 파일선택 버튼으로 선택(최대 10개 가능.)",
    "   상세페이지 최적화를 위해 1개 상세페이지당 5개 이미지 구성 추천",
    "2. 이미지간격 버튼 이용해 이미지간 간격 조정(0~100PX까지 선택/1개 상세페이지당 일괄 적용)",
    "3. 상세페이지 생성 시 최상단과 최하단은 100PX 여백은 고정 생성",
    "4. 생성하기 버튼 클릭 하면 상세페이지 완성",
    "5. 상세페이지 내에 텍스트를 구성하고자 하는 경우 텍스트 편집된 JPG 이미지를 만들어 추가하는 방식으로 활용하세요.",
    "6. 새 작업을 시작하기 위해서는 초기화를 클릭해주세요.",
]

PRO_TITLE = "PSD(고급개체 레이어)가 필요하신가요?"
PRO_DESC = "MS PRO는 수정가능한 상세페이지 PSD 다운로드가 가능합니다.(레이어/고급개체 기반)"
PRO_BULLETS = [
    "→PSD로 빠르고 해상도 높은 작업이 필요할 때",
    "→고급개체(SMART OBJECTS) 레이어 작업이 필요할 때",
    "→반복적인 템플릿이 필요할 때",
    "→업로드 파일 미리보기 제공 등 좀더 다양한 기능이 필요할 때",
]
PRO_CLAIM = "MS PRO는 상세페이지 웹디자이너에게 최고의 도구가 되어줍니다."
PRO_TOOL_TITLE = "PRO 버전은 디자이너를 위한 최고의 툴도 아래와 같이 제공합니다."

PRO_TOOLS = [
    ("GIF 자동 생성기", "간략설명"),
    ("썸메일 메이커", "간략설명"),
    ("이미지 자르기 툴", "간략설명"),
]

FOOTER_COPY = "카피라이트 문구"


# =========================================================
# 2) PASSWORD LOAD
# =========================================================
@st.cache_data(show_spinner=False)
def load_passwords_from_excel() -> Set[str]:
    if not os.path.exists(PASSWORD_FILE):
        return set()
    df = pd.read_excel(PASSWORD_FILE)
    # password 컬럼 있으면 사용, 없으면 첫 컬럼
    cols_lower = {str(c).strip().lower(): c for c in df.columns}
    col = cols_lower.get("password", df.columns[0])
    pw = (
        df[col].astype(str).str.strip()
        .replace({"nan": "", "None": "", "NONE": ""})
    )
    return set([p for p in pw.tolist() if p])


# =========================================================
# 3) STATE NORMALIZE (TypeError 원천차단)
# =========================================================
@dataclass
class Item:
    name: str
    data: bytes


def _is_uploaded_file(obj: Any) -> bool:
    return hasattr(obj, "name") and hasattr(obj, "getvalue")


def normalize_items(raw: Any) -> List[Item]:
    if raw is None:
        return []
    if isinstance(raw, list):
        if len(raw) == 0:
            return []
        if all(isinstance(x, Item) for x in raw):
            return raw
        out: List[Item] = []
        for x in raw:
            if isinstance(x, Item):
                out.append(x)
            elif _is_uploaded_file(x):
                out.append(Item(name=x.name, data=x.getvalue()))
        return out
    if _is_uploaded_file(raw):
        return [Item(name=raw.name, data=raw.getvalue())]
    return []


def init_state():
    if "is_pro" not in st.session_state:
        st.session_state.is_pro = False
    if "show_pro_panel" not in st.session_state:
        st.session_state.show_pro_panel = False
    st.session_state.items = normalize_items(st.session_state.get("items"))


def add_uploads(files, clear_first: bool):
    base = [] if clear_first else (st.session_state.items or [])
    for f in files:
        base.append(Item(name=f.name, data=f.getvalue()))
    st.session_state.items = base


def move_item(idx: int, direction: int):
    items = st.session_state.items or []
    new_idx = idx + direction
    if new_idx < 0 or new_idx >= len(items):
        return
    items[idx], items[new_idx] = items[new_idx], items[idx]
    st.session_state.items = items


def delete_item(idx: int):
    items = st.session_state.items or []
    if 0 <= idx < len(items):
        items.pop(idx)
    st.session_state.items = items


# =========================================================
# 4) IMAGE BUILD (변형 없음/중앙정렬/상하 100px)
# =========================================================
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


def to_jpg_bytes(img: Image.Image, quality: int = 95) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


# =========================================================
# 5) CSS (목업 톤: 흰 바탕 + 부드러운 파스텔, 글씨 크게/또렷)
# =========================================================
def inject_css():
    st.markdown(
        """
        <style>
        .block-container{
            max-width: 1240px;
            padding-top: 18px;
            padding-bottom: 52px;
        }
        [data-testid="stAppViewContainer"]{
            background:
                radial-gradient(1100px 520px at 18% 0%, rgba(255, 228, 241, 0.75), transparent 60%),
                radial-gradient(1100px 520px at 85% 0%, rgba(224, 246, 255, 0.82), transparent 60%),
                linear-gradient(180deg, #ffffff 0%, #fbfbfd 100%);
        }
        .ms-card{
            border: 1px solid rgba(15, 23, 42, 0.10);
            border-radius: 20px;
            background: rgba(255,255,255,0.93);
            box-shadow: 0 10px 30px rgba(2, 6, 23, 0.07);
            padding: 22px 22px;
        }
        .ms-badge{
            display:inline-flex; align-items:center; gap:8px;
            padding:10px 14px; border-radius:999px;
            background: rgba(255,255,255,0.92);
            border: 1px solid rgba(15, 23, 42, 0.12);
            color: rgba(15, 23, 42, 0.78);
            font-size: 13px;
            font-weight: 800;
        }
        .ms-dot{width:10px;height:10px;border-radius:999px;background:linear-gradient(135deg,#ff7aa2,#7ac7ff);}
        .ms-title{
            font-size: 42px;
            font-weight: 950;
            letter-spacing: -0.8px;
            line-height: 1.18;
            margin: 0;
            color: #0f172a;
        }
        .ms-subtitle{
            font-size: 17px;
            line-height: 1.75;
            margin: 10px 0 0 0;
            color: rgba(15,23,42,0.78);
        }
        .ms-h2{
            font-size: 24px;
            font-weight: 950;
            margin: 0 0 12px 0;
            color: #0f172a;
        }
        .ms-body{
            font-size: 16px;
            line-height: 1.75;
            color: rgba(15,23,42,0.78);
        }
        .ms-mini{
            font-size: 14px;
            line-height: 1.7;
            color: rgba(15,23,42,0.66);
        }
        .ms-note{
            border:1px dashed rgba(15,23,42,0.18);
            border-radius:16px;
            padding:14px 14px;
            background: rgba(255,255,255,0.86);
        }
        .ad-banner{
            border-radius: 20px;
            border: 1px solid rgba(15,23,42,0.10);
            background: linear-gradient(135deg, rgba(255,122,162,0.22), rgba(122,199,255,0.22));
            padding: 22px 22px;
        }
        .ad-title{
            font-size: 26px;
            font-weight: 950;
            margin: 0 0 10px 0;
            color:#0f172a;
        }
        .ms-file{
            font-size: 15px;
            color: rgba(15,23,42,0.82);
            overflow:hidden;
            text-overflow:ellipsis;
            white-space:nowrap;
            max-width: 760px;
        }
        div.stButton>button, div.stDownloadButton>button{
            border-radius: 14px !important;
            font-weight: 950 !important;
            padding: 0.70rem 1.10rem !important;
            border: 1px solid rgba(15,23,42,0.14) !important;
        }
        .cta div.stButton>button{
            background: #0f172a !important;
            color: #ffffff !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 6) UI (목업 배치 그대로)
# =========================================================
def header_area():
    left, right = st.columns([0.78, 0.22], vertical_alignment="center")
    with left:
        st.markdown(
            f'<div class="ms-badge"><span class="ms-dot"></span><span>{BADGE_TEXT}</span></div>',
            unsafe_allow_html=True,
        )
    with right:
        if st.button("PRO신청", use_container_width=True):
            st.session_state.show_pro_panel = not st.session_state.show_pro_panel

    if st.session_state.show_pro_panel:
        passwords = load_passwords_from_excel()
        st.markdown('<div class="ms-card">', unsafe_allow_html=True)
        st.markdown('<div class="ms-h2">PRO신청</div>', unsafe_allow_html=True)
        if not passwords:
            st.error("비번리스트.xlsx를 찾지 못했습니다. 저장소 루트(app.py와 같은 위치)에 업로드되어야 합니다.")
            st.markdown("</div>", unsafe_allow_html=True)
            return
        pw = st.text_input("비밀번호 입력", type="password", placeholder="발급받은 비밀번호 입력")
        c1, c2 = st.columns([0.32, 0.68], vertical_alignment="center")
        with c1:
            if st.button("확인", use_container_width=True):
                if pw and pw.strip() in passwords:
                    st.session_state.is_pro = True
                    st.success("PRO 활성화 완료")
                else:
                    st.error("비밀번호가 올바르지 않습니다.")
        with c2:
            st.markdown(f'<div class="ms-mini"><b>사용 및 PRO 문의 : {PRO_CONTACT_EMAIL}</b></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def ad_banner_area():
    # 목업의 “광고배너영역”을 실제 배너로 구현
    st.markdown(
        """
        <div class="ad-banner">
          <div class="ad-title">광고배너영역</div>
          <div class="ms-body"><b>20년차 쇼핑몰 운영자가 현업에서 쓰려고 만든 상세페이지 업무툴</b>입니다. 빠르고, 깔끔하고, 실수 없이.</div>
          <div style="height:10px"></div>
          <div class="ms-mini">FREE로 먼저 써보시고, 필요할 때 PRO로 확장하세요. (상단 PRO신청 버튼)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def title_and_howto_area():
    st.markdown('<div class="ms-card">', unsafe_allow_html=True)
    st.markdown(f"<h1 class='ms-title'>{MAIN_TITLE}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='ms-subtitle'>{MAIN_SUBTITLE}</p>", unsafe_allow_html=True)
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ms-note'><div class='ms-body'>{HOWTO_LINE}</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def maker_area():
    st.markdown('<div class="ms-card">', unsafe_allow_html=True)

    # 목업: (JPG, PNG) + 이미지간격(0~100PX) + 생성하기(JPG)
    is_pro = st.session_state.is_pro
    max_files = 30 if is_pro else 10

    top = st.columns([0.45, 0.30, 0.25], vertical_alignment="bottom")
    with top[0]:
        st.markdown("<div class='ms-mini'><b>(JPG, PNG)</b></div>", unsafe_allow_html=True)
    with top[1]:
        gap = st.slider("이미지 간격 (0~100PX)", 0, 100, 20, 1, key="gap")
    with top[2]:
        st.markdown("<div class='cta'>", unsafe_allow_html=True)
        gen = st.button("생성하기 (JPG)", use_container_width=True, key="gen")
        st.markdown("</div>", unsafe_allow_html=True)

    clear_first = st.checkbox("기존 목록 지우고 새로 추가", value=False, key="clear_first")

    files = st.file_uploader(
        f"이미지 업로드 (최대 {max_files}개)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="uploader",
    )
    if files:
        if len(files) > max_files:
            st.warning(f"최대 {max_files}개까지 업로드 가능합니다. (현재 {len(files)}개)")
        else:
            add_uploads(files, clear_first)

    # 세션 정규화 (TypeError 원천 차단)
    st.session_state.items = normalize_items(st.session_state.get("items"))
    items: List[Item] = st.session_state.items

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='ms-body'><b>업로드 파일명</b></div>", unsafe_allow_html=True)

    if items:
        for i, it in enumerate(items):
            row = st.columns([0.62, 0.12, 0.12, 0.14], vertical_alignment="center")
            with row[0]:
                st.markdown(f"<div class='ms-file'>파일{i+1}  {it.name}</div>", unsafe_allow_html=True)
            with row[1]:
                if st.button("▼", key=f"down_{i}", use_container_width=True):
                    move_item(i, +1)
                    st.rerun()
            with row[2]:
                if st.button("▲", key=f"up_{i}", use_container_width=True):
                    move_item(i, -1)
                    st.rerun()
            with row[3]:
                if st.button("X", key=f"del_{i}", use_container_width=True):
                    delete_item(i)
                    st.rerun()
    else:
        st.markdown("<div class='ms-mini'>업로드된 파일이 없습니다.</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns([0.65, 0.35], vertical_alignment="center")
    with c1:
        st.markdown(f"<div class='ms-mini'><b>{FREE_PREVIEW_NOTICE}</b></div>", unsafe_allow_html=True)
    with c2:
        if st.button("초기화", use_container_width=True, key="reset"):
            st.session_state.items = []
            st.rerun()

    # 생성 처리
    out_bytes = None
    if gen:
        if not items:
            st.error("이미지를 먼저 업로드해 주세요.")
        else:
            imgs = [load_image(it.data) for it in items]
            out = build_detail_image(imgs, gap=gap, pad_top_bottom=100)
            out_bytes = to_jpg_bytes(out, quality=95)
            st.success("상세페이지 JPG 생성 완료")

    if out_bytes:
        st.download_button(
            "다운로드 (JPG)",
            data=out_bytes,
            file_name="misharp_detail.jpg",
            mime="image/jpeg",
            use_container_width=True,
            key="download",
        )

    st.markdown("</div>", unsafe_allow_html=True)


def about_and_guide_area():
    # 목업의 “소개 + 사용안내”
    st.markdown('<div class="ms-card">', unsafe_allow_html=True)
    for line in ABOUT_BLOCK:
        st.markdown(f"<div class='ms-body'><b>{line}</b></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    st.markdown('<div class="ms-card">', unsafe_allow_html=True)
    st.markdown(f"<div class='ms-h2'>{GUIDE_TITLE}</div>", unsafe_allow_html=True)
    for line in GUIDE_LINES:
        st.markdown(f"<div class='ms-mini'>• {line}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def pro_area():
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    st.markdown('<div class="ms-card">', unsafe_allow_html=True)
    st.markdown(f"<div class='ms-h2'>{PRO_TITLE}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ms-body'><b>{PRO_DESC}</b></div>", unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    for b in PRO_BULLETS:
        st.markdown(f"<div class='ms-mini'>{b}</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ms-body'><b>{PRO_CLAIM}</b></div>", unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ms-body'><b>{PRO_TOOL_TITLE}</b></div>", unsafe_allow
