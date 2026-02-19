import io
import os
from dataclasses import dataclass
from typing import List, Set

import pandas as pd
import streamlit as st
from PIL import Image


# =========================
# 0) 앱 기본 설정 (전체 페이지 느낌 = wide)
# =========================
st.set_page_config(
    page_title="MS 상세페이지 자동생성기",
    page_icon="🧷",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================
# 1) 비밀번호 엑셀 자동 로딩
# =========================
PASSWORD_FILE = "비번리스트.xlsx"
PRO_CONTACT_EMAIL = "misharpmail@naver.com"

@st.cache_data(show_spinner=False)
def load_passwords_from_excel() -> Set[str]:
    if not os.path.exists(PASSWORD_FILE):
        return set()

    df = pd.read_excel(PASSWORD_FILE)

    # "password" 컬럼이 있으면 우선 사용, 없으면 첫 번째 컬럼 사용
    cols_lower = {str(c).strip().lower(): c for c in df.columns}
    if "password" in cols_lower:
        col = cols_lower["password"]
    else:
        col = df.columns[0]

    pw_series = (
        df[col]
        .astype(str)
        .str.strip()
        .replace({"nan": "", "None": "", "NONE": ""})
    )

    pw_list = [p for p in pw_series.tolist() if p]
    return set(pw_list)


# =========================
# 2) UI 문구 (목업 기반)
# =========================
APP_BADGE = "MISHARP IMAGE GENERATOR V1-FREE VERSION"
APP_TITLE = "MS 상세페이지 자동생성기 [FREE]"
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


# =========================
# 3) 스타일(CSS) — FreeConvert 느낌 + 부드러운 여성톤
# =========================
def inject_css():
    st.markdown(
        """
        <style>
        /* 전체 폭/여백 (wide에서 너무 벌어지지 않게 1200px로 정리) */
        .block-container { padding-top: 1.2rem; padding-bottom: 2.5rem; max-width: 1200px; }
        header[data-testid="stHeader"] { background: transparent; }

        /* 배경 */
        [data-testid="stAppViewContainer"]{
            background:
                radial-gradient(1200px 600px at 10% 0%, rgba(255, 231, 239, 0.55), transparent 60%),
                radial-gradient(1200px 600px at 90% 0%, rgba(228, 245, 255, 0.65), transparent 60%),
                linear-gradient(180deg, #ffffff 0%, #fbfbfd 100%);
        }

        /* 배지 */
        .ms-badge {
            display:inline-flex; gap:8px; align-items:center;
            padding:8px 12px; border-radius:999px;
            border: 1px solid rgba(20,20,20,0.08);
            background: rgba(255,255,255,0.76);
            backdrop-filter: blur(8px);
            font-size: 12px;
            color: rgba(10,10,10,0.72);
        }
        .ms-dot{
            width:10px; height:10px; border-radius:999px;
            background: linear-gradient(135deg, #ff7aa2, #7ac7ff);
        }

        /* 카드 */
        .ms-card{
            border: 1px solid rgba(20,20,20,0.08);
            border-radius: 18px;
            background: rgba(255,255,255,0.82);
            box-shadow: 0 10px 30px rgba(20,20,20,0.06);
            padding: 18px 18px;
        }
        .ms-soft{
            border: 1px dashed rgba(20,20,20,0.15);
            border-radius: 14px;
            background: rgba(255,255,255,0.68);
            padding: 14px 14px;
        }

        /* 타이포 (목업 느낌: 큰/중간/본문/작은글) */
        .ms-h1{ font-size: 30px; font-weight: 850; letter-spacing:-0.6px; margin: 6px 0 6px 0; }
        .ms-h2{ font-size: 20px; font-weight: 850; letter-spacing:-0.4px; margin: 0 0 8px 0; }
        .ms-h3{ font-size: 16px; font-weight: 850; margin: 0 0 10px 0; }
        .ms-body{ font-size: 14px; color: rgba(10,10,10,0.76); line-height: 1.65; }
        .ms-small{ font-size: 12px; color: rgba(10,10,10,0.62); line-height: 1.55; }
        .ms-mini{ font-size: 11px; color: rgba(10,10,10,0.58); line-height: 1.55; }

        /* 버튼 */
        div.stButton>button, div.stDownloadButton>button{
            border-radius: 12px !important;
            border: 1px solid rgba(20,20,20,0.10) !important;
            padding: 0.58rem 0.95rem !important;
            font-weight: 800 !important;
        }
        div.stButton>button:hover, div.stDownloadButton>button:hover{
            border-color: rgba(255,122,162,0.45) !important;
            box-shadow: 0 10px 22px rgba(255,122,162,0.14) !important;
        }

        /* 파일 리스트 */
        .ms-file-name{
            font-size: 13px;
            color: rgba(10,10,10,0.75);
            overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
            max-width: 620px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================
# 4) 이미지 처리 (변형 없음, 중앙정렬)
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
    widths = [im.width for im in images]
    max_w = max(widths)

    heights = [im.height for im in images]
    total_h = pad_top_bottom + pad_top_bottom + sum(heights) + gap * (len(images) - 1)

    canvas = Image.new("RGB", (max_w, total_h), (255, 255, 255))

    y = pad_top_bottom
    for im in images:
        x = (max_w - im.width) // 2  # 중앙정렬, 리사이즈/변형 없음
        canvas.paste(im, (x, y))
        y += im.height + gap

    return canvas


def pil_to_jpg_bytes(img: Image.Image, quality: int = 95) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


# =========================
# 5) 상태 관리(업로드 리스트/PRO)
# =========================
@dataclass
class Item:
    name: str
    data: bytes


def init_state():
    if "items" not in st.session_state:
        st.session_state.items = []
    if "is_pro" not in st.session_state:
        st.session_state.is_pro = False
    if "show_pro_panel" not in st.session_state:
        st.session_state.show_pro_panel = False


def add_uploads(files, clear_first: bool):
    if clear_first:
        st.session_state.items = []
    for f in files:
        st.session_state.items.append(Item(name=f.name, data=f.getvalue()))


def move_item(idx: int, direction: int):
    items = st.session_state.items
    new_idx = idx + direction
    if new_idx < 0 or new_idx >= len(items):
        return
    items[idx], items[new_idx] = items[new_idx], items[idx]
    st.session_state.items = items


def delete_item(idx: int):
    items = st.session_state.items
    if 0 <= idx < len(items):
        items.pop(idx)
    st.session_state.items = items


# =========================
# 6) 섹션 UI
# =========================
def top_header(pro_passwords: Set[str]):
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
        st.markdown('<div class="ms-card">', unsafe_allow_html=True)
        st.markdown('<div class="ms-h3">PRO 비밀번호 입력</div>', unsafe_allow_html=True)

        if not pro_passwords:
            st.error("비밀번호 파일을 읽지 못했습니다. 저장소 루트에 '비번리스트.xlsx'가 있는지 확인해주세요.")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        st.markdown(
            '<div class="ms-mini">현재는 <b>수동 발급(비밀번호 리스트)</b> 방식으로 운영됩니다.</div>',
            unsafe_allow_html=True,
        )
        pw = st.text_input("비밀번호", type="password", placeholder="발급받은 비밀번호를 입력해 주세요.")
        c1, c2 = st.columns([0.35, 0.65], vertical_alignment="center")
        with c1:
            if st.button("확인", use_container_width=True):
                if pw and (pw.strip() in pro_passwords):
                    st.session_state.is_pro = True
                    st.success("PRO가 활성화되었습니다. (미리보기/확장 기능이 열렸습니다)")
                else:
                    st.error("비밀번호가 올바르지 않습니다.")
        with c2:
            st.markdown(
                f'<div class="ms-mini">문의/발급: <b>{PRO_CONTACT_EMAIL}</b></div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)


def banner_area():
    st.markdown(
        """
        <div class="ms-card" style="padding:0; overflow:hidden;">
          <div style="
              padding:18px 18px;
              background: linear-gradient(135deg, rgba(255,122,162,0.18), rgba(122,199,255,0.18));
              border-bottom: 1px solid rgba(20,20,20,0.06);
          ">
            <div class="ms-h2">디자이너의 단순 작업, 이제 ‘자동’으로.</div>
            <div class="ms-body">20년차 쇼핑몰 운영자가 현업에서 쓰려고 만든 상세페이지 업무툴입니다. <b>빠르고, 깔끔하고, 실수 없이</b>.</div>
          </div>
          <div style="display:flex; gap:10px; padding:14px 18px; align-items:center; justify-content:space-between;">
            <div class="ms-small">FREE로 먼저 써보시고, 필요할 때 PRO로 확장하세요.</div>
            <div style="font-size:12px; color: rgba(10,10,10,0.65);">상단의 <b>PRO 신청</b> 버튼에서 비밀번호 입력</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero():
    st.markdown('<div class="ms-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="ms-h1">{APP_TITLE}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ms-body">{APP_SUBTITLE}</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="ms-soft">
          <div class="ms-small"><b>사용방법</b></div>
          <div class="ms-small">{HOW_TO_QUICK}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def uploader_and_controls():
    st.markdown('<div class="ms-card">', unsafe_allow_html=True)

    is_pro = st.session_state.is_pro
    max_files = 30 if is_pro else 10

    title_cols = st.columns([0.55, 0.20, 0.25], vertical_alignment="bottom")
    with title_cols[0]:
        st.markdown('<div class="ms-h3">파일선택</div>', unsafe_allow_html=True)
        st.markdown('<div class="ms-mini">(JPG, PNG)</div>', unsafe_allow_html=True)
    with title_cols[1]:
        gap = st.slider("이미지 간격", min_value=0, max_value=100, value=20, step=1)
    with title_cols[2]:
        st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
        gen_clicked = st.button("생성하기 (JPG)", use_container_width=True)

    clear_first = st.checkbox("기존 목록 지우고 새로 추가", value=False)

    files = st.file_uploader(
        f"이미지 업로드 (최대 {max_files}개)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if files:
        if len(files) > max_files:
            st.warning(f"최대 {max_files}개까지 업로드 가능합니다. (현재 {len(files)}개)")
        else:
            add_uploads(files, clear_first=clear_first)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    items: List[Item] = st.session_state.items
    if items:
        st.markdown('<div class="ms-small"><b>업로드 파일명</b></div>', unsafe_allow_html=True)
        for i, it in enumerate(items):
            row = st.columns([0.62, 0.14, 0.12, 0.12], vertical_alignment="center")
            with row[0]:
                st.markdown(f"<div class='ms-file-name'>{i+1}. {it.name}</div>", unsafe_allow_html=True)
            with row[1]:
                if st.button("▲", key=f"up_{i}", use_container_width=True):
                    move_item(i, -1)
                    st.rerun()
            with row[2]:
                if st.button("▼", key=f"down_{i}", use_container_width=True):
                    move_item(i, +1)
                    st.rerun()
            with row[3]:
                if st.button("X", key=f"del_{i}", use_container_width=True):
                    delete_item(i)
                    st.rerun()

        c1, c2 = st.columns([0.25, 0.75], vertical_alignment="center")
        with c1:
            if st.button("초기화", use_container_width=True):
                st.session_state.items = []
                st.rerun()
        with c2:
            if not is_pro:
                st.markdown(f"<div class='ms-mini'><b>{FREE_PREVIEW_NOTICE}</b></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='ms-mini'><b>PRO:</b> 업로드 이미지 미리보기 + 더 많은 업로드 한도</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='ms-mini'>아직 업로드된 파일이 없습니다.</div>", unsafe_allow_html=True)

    # PRO 미리보기
    if is_pro and st.session_state.items:
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="ms-small"><b>업로드 미리보기 (PRO)</b></div>', unsafe_allow_html=True)
        thumbs = st.columns(5)
        for idx, it in enumerate(st.session_state.items[:20]):  # 과도한 렌더 방지
            with thumbs[idx % 5]:
                try:
                    im = load_image(it.data)
                    st.image(im, use_container_width=True)
                except Exception:
                    st.caption("미리보기 실패")

    # 생성 처리
    output_bytes = None
    output_name = None

    if gen_clicked:
        if not st.session_state.items:
            st.error("이미지를 먼저 업로드해 주세요.")
        else:
            try:
                imgs = [load_image(it.data) for it in st.session_state.items]
                out = build_detail_image(imgs, gap=gap, pad_top_bottom=100)
                output_bytes = pil_to_jpg_bytes(out, quality=95)
                output_name = "misharp_detail.jpg"
                st.success("상세페이지 JPG 생성이 완료되었습니다.")
            except Exception as e:
                st.error(f"생성 중 오류가 발생했습니다: {e}")

    if output_bytes:
        st.download_button(
            "다운로드 (JPG)",
            data=output_bytes,
            file_name=output_name,
            mime="image/jpeg",
            use_container_width=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


def about_and_guides():
    st.markdown('<div class="ms-card">', unsafe_allow_html=True)
    st.markdown('<div class="ms-h3">이 툴은 누가 만들었나요?</div>', unsafe_allow_html=True)
    st.markdown(f"<div class='ms-small'><b>{ABOUT_1}</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ms-small'><b>{ABOUT_2}</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ms-small'><b>{ABOUT_3}</b></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    st.markdown('<div class="ms-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="ms-h3">{GUIDE_TITLE}</div>', unsafe_allow_html=True)
    for line in GUIDE_LINES:
        st.markdown(f"<div class='ms-mini'>• {line}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def pro_section():
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="ms-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="ms-h3">{PRO_SEC_TITLE}</div>', unsafe_allow_html=True)
    st.markdown(f"<div class='ms-small'><b>{PRO_SEC_DESC}</b></div>", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    for b in PRO_BULLETS:
        st.markdown(f"<div class='ms-mini'>{b}</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ms-small'><b>{PRO_CLAIM}</b></div>", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ms-small'><b>{PRO_TOOL_TITLE}</b></div>", unsafe_allow_html=True)

    tcols = st.columns(3)
    for i, (t, desc) in enumerate(PRO_TOOLS):
        with tcols[i]:
            st.markdown(
                f"""
                <div class="ms-soft">
                  <div class="ms-small"><b>{t}</b></div>
                  <div class="ms-mini">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ms-mini'><b>사용 및 PRO 문의 : {PRO_CONTACT_EMAIL}</b></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def footer():
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='ms-mini' style='text-align:center; padding: 10px 0;'>{FOOTER}</div>",
        unsafe_allow_html=True,
    )


# =========================
# 7) main
# =========================
def main():
    init_state()
    inject_css()

    pro_passwords = load_passwords_from_excel()

    top_header(pro_passwords)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    banner_area()
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    hero()
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    uploader_and_controls()
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    about_and_guides()
    pro_section()
    footer()


if __name__ == "__main__":
    main()
