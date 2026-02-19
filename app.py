import io
import os
from dataclasses import dataclass
from typing import List, Set, Any

import pandas as pd
import streamlit as st
from PIL import Image


# =========================================================
# 0) Streamlit 설정
# =========================================================
st.set_page_config(
    page_title="MS 상세페이지 자동생성기 [FREE]",
    page_icon="🧷",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PASSWORD_FILE = "비번리스트.xlsx"
PRO_CONTACT_EMAIL = "misharpmail@naver.com"


# =========================================================
# 1) 목업 카피 (그대로)
# =========================================================
APP_BADGE = "MISHARP IMAGE GENERATOR V1-FREE VERSION"

APP_TITLE = "MS 상세페이지 자동생성기 [FREE]"  # ✅ 형준님이 말한 ‘가장 타이틀’
APP_SUBTITLE = "상세페이지 이미지를 자동으로 생성하여 디자이너의 단순업무시간을 대폭 줄여드립니다."

HOW_TO_QUICK = (
    "1. 이미지 업로드(최대 10개)   "
    "2. 이미지 간격 0~100PX 조정   "
    "3. 생성하기 버튼 클릭하면 끝!"
)

FREE_PREVIEW_NOTICE = "*FREE 버전에서 미리보기는 지원되지 않습니다."

ABOUT_1 = "MS 상세페이지 생성기는 20년차 여성의류 인터넷 쇼핑몰 대표가 사내에서 사용하기 위해 직접 제작한 프로그램으로"
ABOUT_2 = "실제 온라인 쇼핑몰 디자인 작업에 적용하고 있으며, 디자이너의 요구사항을 최대한 반영하여 구현한 최고의 툴입니다."
ABOUT_3 = "MS 업무툴을 통해 단순업무 시간은 줄이고 상세페이지의 퀄리티는 더욱 높이세요."

GUIDE_TITLE = "MS 상세페이지 생성기 사용안내"
GUIDE_LINES = [
    "1. 사전에 보정작업을 마친 상세페이지용 이미지를 파일선택 버튼으로 선택(최대 10개 가능.)",
    "   상세페이지 최적화를 위해 1개 상세페이지당 5개 이미지 구성 추천",
    "2. 이미지간격 버튼 이용해 이미지간 간격 조정(0~100PX까지 선택/1개 상세페이지당 동일 적용)",
    "3. 상세페이지 생성 시 최상단과 최하단은 100PX 여백은 고정 생성",
    "4. 생성하기 버튼 클릭 하면 상세페이지 완성",
    "5. 상세페이지 내에 텍스트를 구성하고자 하는 경우 텍스트 편집된 JPG 이미지를 함께 업로드해 주세요.",
    "6. 새 작업을 시작하기 위해서는 초기화를 클릭해주세요.",
]

PRO_SEC_TITLE = "PSD(고급개체 레이어)가 필요하신가요?"
PRO_SEC_DESC = "MS PRO는 수정가능한 상세페이지 PSD 다운로드가 가능합니다.(레이어/고급개체 기반)"
PRO_BULLETS = [
    "→ PSD로 빠르고 해상도 높은 작업이 필요할 때",
    "→ 고급개체(SMART OBJECTS) 레이어 작업이 필요할 때",
    "→ 반복적인 템플릿이 필요할 때",
    "→ 업로드 파일 미리보기 제공 등 좀더 다양한 기능이 필요할 때",
]
PRO_CLAIM = "MS PRO는 상세페이지 웹디자이너에게 최고의 도구가 되어줍니다."
PRO_TOOL_TITLE = "PRO 버전은 디자이너를 위한 최고의 툴도 아래와 같이 제공합니다."
PRO_TOOLS = [
    ("GIF 자동 생성기", "움직이는 룩북/배너용 GIF를 자동으로 만들어드립니다."),
    ("썸네일 메이커", "플랫폼 규격에 맞춘 썸네일을 빠르게 생성합니다."),
    ("이미지 자르기 툴", "비율 유지/중앙 기준 크롭으로 깔끔하게 정리합니다."),
]
FOOTER = "© MISHARP. All rights reserved."


# =========================================================
# 2) 비밀번호 엑셀 로딩
# =========================================================
@st.cache_data(show_spinner=False)
def load_passwords_from_excel() -> Set[str]:
    if not os.path.exists(PASSWORD_FILE):
        return set()

    df = pd.read_excel(PASSWORD_FILE)

    cols_lower = {str(c).strip().lower(): c for c in df.columns}
    col = cols_lower.get("password", df.columns[0])

    pw_series = (
        df[col]
        .astype(str)
        .str.strip()
        .replace({"nan": "", "None": "", "NONE": ""})
    )
    pw_list = [p for p in pw_series.tolist() if p]
    return set(pw_list)


# =========================================================
# 3) 상태/업로드 구조 (⚠️ 여기서 세션 마이그레이션으로 TypeError 제거)
# =========================================================
@dataclass
class Item:
    name: str
    data: bytes


def _is_uploaded_file(obj: Any) -> bool:
    return hasattr(obj, "name") and hasattr(obj, "getvalue")


def normalize_items(raw: Any) -> List[Item]:
    """
    세션에 남아있는 과거 버전 형태(UploadedFile 1개/리스트/None)를
    Item 리스트로 강제 변환해서 TypeError를 원천 차단합니다.
    """
    if raw is None:
        return []

    # 과거: UploadedFile 단일
    if _is_uploaded_file(raw):
        return [Item(name=raw.name, data=raw.getvalue())]

    # 리스트 형태
    if isinstance(raw, list):
        if len(raw) == 0:
            return []

        # 이미 Item 리스트
        if all(isinstance(x, Item) for x in raw):
            return raw

        # UploadedFile 리스트
        if all(_is_uploaded_file(x) for x in raw):
            return [Item(name=x.name, data=x.getvalue()) for x in raw]

        # 섞여있으면 안전하게 변환 가능한 것만
        out: List[Item] = []
        for x in raw:
            if isinstance(x, Item):
                out.append(x)
            elif _is_uploaded_file(x):
                out.append(Item(name=x.name, data=x.getvalue()))
        return out

    # 그 외 이상한 타입이면 초기화
    return []


def init_state():
    if "is_pro" not in st.session_state:
        st.session_state.is_pro = False
    if "show_pro_panel" not in st.session_state:
        st.session_state.show_pro_panel = False

    # 핵심: 기존 session_state.items를 강제로 정상화
    st.session_state.items = normalize_items(st.session_state.get("items"))


def add_uploads(files, clear_first: bool):
    if clear_first:
        st.session_state.items = []
    base = st.session_state.items or []
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
# 4) 이미지 처리 (변형 없음/중앙정렬)
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


def pil_to_jpg_bytes(img: Image.Image, quality: int = 95) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


# =========================================================
# 5) CSS — 글자 작음/가독성/타이틀 잘림 해결 (크기 크게!)
# =========================================================
def inject_css():
    st.markdown(
        """
        <style>
        .block-container{
            max-width: 1240px;
            padding-top: 24px;
            padding-bottom: 56px;
        }

        [data-testid="stAppViewContainer"]{
            background:
                radial-gradient(1200px 520px at 10% 0%, rgba(255, 228, 239, 0.68), transparent 60%),
                radial-gradient(1200px 520px at 90% 0%, rgba(224, 244, 255, 0.78), transparent 60%),
                linear-gradient(180deg, #ffffff 0%, #fbfbfd 100%);
        }

        .ms-card{
            border: 1px solid rgba(15, 23, 42, 0.09);
            border-radius: 20px;
            background: rgba(255,255,255,0.92);
            box-shadow: 0 10px 34px rgba(2, 6, 23, 0.08);
            padding: 22px 22px;
        }

        .ms-badge{
            display:inline-flex; align-items:center; gap:8px;
            padding:10px 14px; border-radius:999px;
            background: rgba(255,255,255,0.90);
            border: 1px solid rgba(15, 23, 42, 0.12);
            color: rgba(15, 23, 42, 0.72);
            font-size: 13px;
        }
        .ms-dot{
            width:10px;height:10px;border-radius:999px;
            background: linear-gradient(135deg,#ff7aa2,#7ac7ff);
        }

        /* ✅ 크기 크게: 타이틀 44 / 섹션 24 / 본문 16 */
        .ms-title{
            font-size: 44px;
            font-weight: 950;
            letter-spacing: -1px;
            line-height: 1.15;
            margin: 0;
            color: #0f172a;
            overflow: visible;
            white-space: normal;
        }
        .ms-subtitle{
            font-size: 16px;
            line-height: 1.75;
            margin: 10px 0 0 0;
            color: rgba(15, 23, 42, 0.78);
        }
        .ms-h3{
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
        .ms-small{
            font-size: 15px;
            line-height: 1.75;
            color: rgba(15,23,42,0.74);
        }
        .ms-mini{
            font-size: 14px;
            line-height: 1.7;
            color: rgba(15,23,42,0.66);
        }

        .ms-hero{
            border-radius: 20px;
            border: 1px solid rgba(15,23,42,0.10);
            background: linear-gradient(135deg, rgba(255,122,162,0.22), rgba(122,199,255,0.22));
            padding: 22px 22px;
        }
        .ms-hero-title{
            font-size: 26px;
            font-weight: 950;
            margin: 0 0 10px 0;
            color: #0f172a;
            letter-spacing: -0.6px;
        }

        div.stButton>button, div.stDownloadButton>button{
            border-radius: 14px !important;
            font-weight: 950 !important;
            padding: 0.70rem 1.10rem !important;
            border: 1px solid rgba(15,23,42,0.14) !important;
        }
        .ms-cta div.stButton>button{
            background: #0f172a !important;
            color: #ffffff !important;
        }

        .ms-file-name{
            font-size: 15px;
            color: rgba(15,23,42,0.82);
            overflow:hidden;
            text-overflow:ellipsis;
            white-space:nowrap;
            max-width: 740px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 6) UI 섹션 (목업 순서)
# =========================================================
def top_header():
    left, right = st.columns([0.78, 0.22], vertical_alignment="center")

    with left:
        st.markdown(
            f"""
            <div class="ms-badge">
              <span class="ms-dot"></span>
              <span>{APP_BADGE}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        if st.button("PRO 신청", use_container_width=True):
            st.session_state.show_pro_panel = not st.session_state.show_pro_panel

    if st.session_state.show_pro_panel:
        pro_passwords = load_passwords_from_excel()
        st.markdown('<div class="ms-card">', unsafe_allow_html=True)
        st.markdown('<div class="ms-h3">PRO 신청</div>', unsafe_allow_html=True)

        if not pro_passwords:
            st.error("비밀번호 파일을 읽지 못했습니다. 저장소 루트에 '비번리스트.xlsx'가 있는지 확인해주세요.")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        st.markdown('<div class="ms-mini">비밀번호를 입력하시면 PRO 기능이 활성화됩니다.</div>', unsafe_allow_html=True)
        pw = st.text_input("비밀번호 입력", type="password", placeholder="비밀번호를 입력해주세요.")
        c1, c2 = st.columns([0.32, 0.68], vertical_alignment="center")
        with c1:
            if st.button("확인", use_container_width=True):
                if pw and pw.strip() in pro_passwords:
                    st.session_state.is_pro = True
                    st.success("PRO 활성화 완료")
                else:
                    st.error("비밀번호가 올바르지 않습니다.")
        with c2:
            st.markdown(f'<div class="ms-mini">문의/발급: <b>{PRO_CONTACT_EMAIL}</b></div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


def banner_block():
    st.markdown(
        """
        <div class="ms-hero">
          <div class="ms-hero-title">디자이너의 단순 작업, 이제 ‘자동’으로.</div>
          <div class="ms-body">20년차 쇼핑몰 운영자가 현업에서 쓰려고 만든 상세페이지 업무툴입니다. <b>빠르고, 깔끔하고, 실수 없이.</b></div>
          <div style="height:10px"></div>
          <div class="ms-mini">FREE로 먼저 써보시고, 필요할 때 PRO로 확장하세요. (상단 <b>PRO 신청</b> 버튼에서 비밀번호 입력)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def title_block():
    st.markdown('<div class="ms-card">', unsafe_allow_html=True)
    st.markdown(f'<h1 class="ms-title">{APP_TITLE}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="ms-subtitle">{APP_SUBTITLE}</p>', unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="border:1px dashed rgba(15,23,42,0.18); border-radius:16px; padding:14px 14px; background: rgba(255,255,255,0.82);">
          <div class="ms-small"><b>사용방법</b></div>
          <div class="ms-small">{HOW_TO_QUICK}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def uploader_section():
    st.markdown('<div class="ms-card">', unsafe_allow_html=True)
    st.markdown('<div class="ms-h3">상세페이지 생성</div>', unsafe_allow_html=True)

    is_pro = st.session_state.is_pro
    max_files = 30 if is_pro else 10

    row = st.columns([0.55, 0.20, 0.25], vertical_alignment="bottom")
    with row[0]:
        st.markdown('<div class="ms-small"><b>파일선택</b></div>', unsafe_allow_html=True)
        st.markdown('<div class="ms-mini">(JPG, PNG)</div>', unsafe_allow_html=True)
    with row[1]:
        gap = st.slider("이미지 간격 0~100PX", 0, 100, 20, 1, key="gap_slider")
    with row[2]:
        st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="ms-cta">', unsafe_allow_html=True)
        gen_clicked = st.button("생성하기 (JPG)", use_container_width=True, key="gen_btn")
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

    # ✅ 여기서도 한 번 더 정규화 (세션 꼬임 재발 방지)
    st.session_state.items = normalize_items(st.session_state.get("items"))
    items: List[Item] = st.session_state.items

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="ms-small"><b>업로드 파일명</b></div>', unsafe_allow_html=True)

    if not items:
        st.markdown("<div class='ms-mini'>아직 업로드된 파일이 없습니다.</div>", unsafe_allow_html=True)
    else:
        for i, it in enumerate(items):
            cols = st.columns([0.62, 0.14, 0.12, 0.12], vertical_alignment="center")
            with cols[0]:
                st.markdown(f"<div class='ms-file-name'>{i+1}. {it.name}</div>", unsafe_allow_html=True)
            with cols[1]:
                if st.button("▲", key=f"up_{i}", use_container_width=True):
                    move_item(i, -1)
                    st.rerun()
            with cols[2]:
                if st.button("▼", key=f"down_{i}", use_container_width=True):
                    move_item(i, +1)
                    st.rerun()
            with cols[3]:
                if st.button("X", key=f"del_{i}", use_container_width=True):
                    delete_item(i)
                    st.rerun()

        c1, c2 = st.columns([0.25, 0.75], vertical_alignment="center")
        with c1:
            if st.button("초기화", use_container_width=True, key="reset_btn"):
                st.session_state.items = []
                st.rerun()
        with c2:
            if not is_pro:
                st.markdown(f"<div class='ms-mini'><b>{FREE_PREVIEW_NOTICE}</b></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='ms-mini'><b>PRO:</b> 업로드 이미지 미리보기 + 업로드 30개</div>", unsafe_allow_html=True)

    # PRO 미리보기
    if is_pro and items:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="ms-small"><b>업로드 미리보기 (PRO)</b></div>', unsafe_allow_html=True)
        thumbs = st.columns(5)
        for idx, it in enumerate(items[:20]):
            with thumbs[idx % 5]:
                try:
                    im = load_image(it.data)
                    st.image(im, use_container_width=True)
                except Exception:
                    st.caption("미리보기 실패")

    # 생성
    output_bytes = None
    if gen_clicked:
        if not items:
            st.error("이미지를 먼저 업로드해 주세요.")
        else:
            try:
                imgs = [load_image(it.data) for it in items]
                out = build_detail_image(imgs, gap=gap, pad_top_bottom=100)
                output_bytes = pil_to_jpg_bytes(out, quality=95)
                st.success("상세페이지 JPG 생성이 완료되었습니다.")
            except Exception as e:
                st.error(f"생성 중 오류가 발생했습니다: {e}")

    if output_bytes:
        st.download_button(
            "다운로드 (JPG)",
            data=output_bytes,
            file_name="misharp_detail.jpg",
            mime="image/jpeg",
            use_container_width=True,
            key="dl_btn",
        )

    st.markdown("</div>", unsafe_allow_html=True)


def about_block():
    st.markdown('<div class="ms-card">', unsafe_allow_html=True)
    st.markdown('<div class="ms-h3">이 툴은 누가 만들었나요?</div>', unsafe_allow_html=True)
    st.markdown(f"<div class='ms-small'><b>{ABOUT_1}</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ms-small'><b>{ABOUT_2}</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ms-small'><b>{ABOUT_3}</b></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def guide_block():
    st.markdown('<div class="ms-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="ms-h3">{GUIDE_TITLE}</div>', unsafe_allow_html=True)
    for line in GUIDE_LINES:
        st.markdown(f"<div class='ms-mini'>• {line}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def pro_block():
    st.markdown('<div class="ms-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="ms-h3">{PRO_SEC_TITLE}</div>', unsafe_allow_html=True)
    st.markdown(f"<div class='ms-small'><b>{PRO_SEC_DESC}</b></div>", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    for b in PRO_BULLETS:
        st.markdown(f"<div class='ms-mini'>{b}</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ms-small'><b>{PRO_CLAIM}</b></div>", unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ms-small'><b>{PRO_TOOL_TITLE}</b></div>", unsafe_allow_html=True)

    cols = st.columns(3)
    for i, (t, desc) in enumerate(PRO_TOOLS):
        with cols[i]:
            st.markdown(
                f"""
                <div style="border:1px solid rgba(15,23,42,0.14); border-radius:16px; padding:14px 14px; background: rgba(255,255,255,0.82);">
                  <div class="ms-small"><b>{t}</b></div>
                  <div class="ms-mini">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ms-mini'><b>사용 및 PRO 문의 : {PRO_CONTACT_EMAIL}</b></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def footer():
    st.markdown(
        f"<div class='ms-mini' style='text-align:center; padding: 18px 0;'>{FOOTER}</div>",
        unsafe_allow_html=True,
    )


# =========================================================
# 7) main
# =========================================================
def main():
    init_state()
    inject_css()

    top_header()
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    banner_block()
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ✅ “메인 타이틀”은 여기서 무조건 노출
    title_block()
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    uploader_section()
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    about_block()
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    guide_block()
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    pro_block()
    footer()


if __name__ == "__main__":
    main()
