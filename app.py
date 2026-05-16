"""
Streamlit 웹 UI — Gemma 4 강의 복습 퀴즈 생성기
================================================
quiz_generator.py를 그대로 import해서 한 30줄로 웹 UI 추가.

실행:
    streamlit run app.py
    → http://localhost:8501
"""
import json
import time
from pathlib import Path

import streamlit as st

from quiz_generator import (
    MODEL,
    extract_text_from_pdf,
    generate_quiz_stream,
    parse_quiz,
)

# ============================================================
# 페이지 설정
# ============================================================
st.set_page_config(
    page_title="Gemma 4 퀴즈 생성기",
    page_icon="📚",
    layout="centered",
)

ACCENT = "#8C1D40"

# ============================================================
# 다국어 (i18n)
# ============================================================
LANGS = {
    "한국어": {
        "title": "Gemma 4 퀴즈 생성기",
        "subtitle": "강의자료 → 복습 퀴즈 · 100% 로컬 · 외부 API 0회",
        "sidebar_input": "입력",
        "sidebar_lang": "언어 / Language",
        "input_mode": "입력 방식",
        "mode_pdf": "PDF 업로드",
        "mode_txt": "TXT 업로드",
        "mode_paste": "텍스트 직접 입력",
        "uploader_label": "강의자료 파일",
        "uploader_drop": "여기에 파일을 드롭하거나 파일 선택을 눌러 업로드",
        "uploader_browse": "파일 선택",
        "uploader_limit": "파일당 200MB",
        "paste_label": "강의자료 텍스트 (복사해서 붙여넣기)",
        "paste_placeholder": "여기에 강의 노트, 책 발췌, 위키 글 등을 붙여넣으세요...",
        "btn_generate": "퀴즈 생성",
        "model_label": "모델",
        "footer_caption": "로컬 Ollama · Wi-Fi 없어도 동작",
        "status_running": "Gemma 4 호출 중... (약 1분 30초)",
        "status_done": "✅ 생성 완료",
        "status_pdf": "📄 PDF 읽는 중",
        "status_chars": "글자 추출",
        "status_calling": "🤖 Gemma 4 호출 중...",
        "status_elapsed": "완료",
        "topic_prefix": "📚 주제 —",
        "question": "문제",
        "expander": "정답 / 해설 보기",
        "answer": "✓ 정답",
        "explanation": "💡 해설",
        "info_default": "ℹ️ 미리 생성된 sample.pdf 결과를 표시 중입니다. 사이드바에서 다른 자료 업로드 가능.",
        "warn_no_input": "사이드바에서 강의자료를 입력하고 '퀴즈 생성'을 누르세요.",
        "info_pdf_truncated": "ℹ️ 안정적인 출력을 위해 PDF의 앞 30페이지만 분석하여 퀴즈를 생성했습니다.",
        "type_mcq": "객관식",
        "type_short": "단답형",
        "choose_answer": "답을 선택하세요",
        "enter_answer": "답을 입력하세요",
        "answer_placeholder": "여기에 답 입력 후 Enter",
        "show_answer": "정답 보기",
        "correct": "✓ 정답!",
        "wrong": "✗ 오답 — 정답:",
        "answer_was": "정답:",
        "progress_label": "Gemma 4 토큰 생성 중",
        "progress_done": "✓ 생성 완료",
        "raw_expander": "원본 응답 (JSON) 보기",
    },
    "English": {
        "title": "Gemma 4 Quiz Generator",
        "subtitle": "Lecture material → Review Quiz · 100% local · Zero external API",
        "sidebar_input": "Input",
        "sidebar_lang": "언어 / Language",
        "input_mode": "Input mode",
        "mode_pdf": "Upload PDF",
        "mode_txt": "Upload TXT",
        "mode_paste": "Paste text",
        "uploader_label": "Lecture file",
        "uploader_drop": "Drag and drop a file here, or click 'Browse files'",
        "uploader_browse": "Browse files",
        "uploader_limit": "200MB per file",
        "paste_label": "Lecture text (paste here)",
        "paste_placeholder": "Paste lecture notes, book excerpt, wiki article, etc...",
        "btn_generate": "Generate quiz",
        "model_label": "Model",
        "footer_caption": "Local Ollama · Works without Wi-Fi",
        "status_running": "Calling Gemma 4... (~1m 30s)",
        "status_done": "✅ Done",
        "status_pdf": "📄 Reading PDF",
        "status_chars": "chars extracted",
        "status_calling": "🤖 Calling Gemma 4...",
        "status_elapsed": "Done",
        "topic_prefix": "📚 Topic —",
        "question": "Q",
        "expander": "Show answer / explanation",
        "answer": "✓ Answer",
        "explanation": "💡 Explanation",
        "info_default": "ℹ️ Showing pre-generated result for sample.pdf. Upload different material from the sidebar.",
        "warn_no_input": "Provide lecture material in the sidebar and click 'Generate quiz'.",
        "info_pdf_truncated": "ℹ️ For stable output, only the first 30 pages of the PDF were analyzed.",
        "choose_answer": "Choose an answer",
        "enter_answer": "Enter your answer",
        "answer_placeholder": "Type answer and press Enter",
        "show_answer": "Show answer",
        "correct": "✓ Correct!",
        "wrong": "✗ Wrong — answer:",
        "answer_was": "Answer:",
        "progress_label": "Gemma 4 generating tokens",
        "progress_done": "✓ Done",
        "raw_expander": "Show raw response (JSON)",
        "type_mcq": "Multiple choice",
        "type_short": "Short answer",
    },
}

# 언어 선택 (사이드바 최상단)
lang_name = st.sidebar.selectbox(
    "🌐 언어 / Language",
    options=list(LANGS.keys()),
    index=0,
    key="lang",
)
T = LANGS[lang_name]


# ============================================================
# Streamlit 네이티브 영어 라벨을 한국어로 덮어쓰기 (CSS)
# Streamlit이 다국어 지원 안 해서 file_uploader 안쪽 텍스트는 영어로 박혀 있음.
# ::after pseudo-element로 가리고 우리 한국어 라벨을 위에 표시.
# ============================================================
if lang_name == "한국어":
    st.markdown(
        f"""
        <style>
        /* 드롭존 안내 문구 교체 */
        [data-testid="stFileUploaderDropzoneInstructions"] > div > span {{
            visibility: hidden;
        }}
        [data-testid="stFileUploaderDropzoneInstructions"] > div > span::before {{
            content: "{T['uploader_drop']}";
            visibility: visible;
            display: block;
        }}
        /* 파일 크기 제한 안내 */
        [data-testid="stFileUploaderDropzoneInstructions"] > div > small {{
            visibility: hidden;
        }}
        [data-testid="stFileUploaderDropzoneInstructions"] > div > small::before {{
            content: "{T['uploader_limit']}";
            visibility: visible;
            display: block;
        }}
        /* "Browse files" 버튼 — file_uploader 안쪽으로만 한정 (다른 버튼 안 건드리게) */
        [data-testid="stFileUploaderDropzone"] [data-testid="stBaseButton-secondary"] {{
            font-size: 0;
        }}
        [data-testid="stFileUploaderDropzone"] [data-testid="stBaseButton-secondary"]::before {{
            content: "{T['uploader_browse']}";
            font-size: 14px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 상단 헤더
# ============================================================
st.markdown(
    f"<h1 style='color:{ACCENT};margin-bottom:0'>{T['title']}</h1>"
    f"<p style='color:#6B6B6B;margin-top:4px'>{T['subtitle']}</p>",
    unsafe_allow_html=True,
)
st.divider()


# ============================================================
# 결과 렌더 함수
# ============================================================
def _norm(s: str) -> str:
    return (s or "").strip().lower()


def render_quiz(quiz: dict, key_prefix: str = "q") -> None:
    st.markdown(f"#### {T['topic_prefix']} {quiz.get('topic', '')}")
    for i, q in enumerate(quiz.get("questions", []), 1):
        qtype = q.get("type", "")
        question = q.get("question", "")
        answer = q.get("answer", "")
        explanation = q.get("explanation", "")

        with st.container(border=True):
            st.markdown(f"**[{T['question']} {i}] ({qtype})**")
            st.markdown(question)

            if qtype == "객관식":
                choices = q.get("choices", [])
                selected = st.radio(
                    T["choose_answer"],
                    options=choices,
                    key=f"{key_prefix}_{i}",
                    index=None,
                    label_visibility="collapsed",
                )
                if selected is not None:
                    if _norm(selected) == _norm(answer) or _norm(answer) in _norm(selected):
                        st.success(T["correct"])
                    else:
                        st.error(f"{T['wrong']} {answer}")
                    if explanation:
                        st.info(f"💡 {explanation}")

            else:  # 단답형 — 자동 채점은 위험(부분 일치/표현 차이), '정답 보기'로
                col1, col2 = st.columns([3, 1])
                with col1:
                    user_ans = st.text_input(
                        T["enter_answer"],
                        key=f"{key_prefix}_{i}_in",
                        placeholder=T["answer_placeholder"],
                        label_visibility="collapsed",
                    )
                with col2:
                    show = st.button(T["show_answer"], key=f"{key_prefix}_{i}_btn", use_container_width=True)
                if show or user_ans:
                    st.markdown(f"**{T['answer_was']}** {answer}")
                    if explanation:
                        st.info(f"💡 {explanation}")


# ============================================================
# 사이드바 — 입력
# ============================================================
MODES = ["pdf", "txt", "paste"]

with st.sidebar:
    st.markdown(f"### {T['sidebar_input']}")
    mode = st.radio(
        T["input_mode"],
        options=MODES,
        format_func=lambda m: T[f"mode_{m}"],
        horizontal=False,
    )

    pdf = txt = pasted = None
    if mode == "pdf":
        pdf = st.file_uploader(T["uploader_label"], type=["pdf"])
    elif mode == "txt":
        txt = st.file_uploader(T["uploader_label"], type=["txt", "md"])
    else:
        pasted = st.text_area(
            T["paste_label"],
            placeholder=T["paste_placeholder"],
            height=240,
        )

    run = st.button(T["btn_generate"], type="primary", use_container_width=True)

    st.divider()
    st.caption(f"{T['model_label']}: `{MODEL}`")
    st.caption(T["footer_caption"])


# ============================================================
# 메인 영역
# ============================================================
default_quiz = Path("sample.quiz.json")

# 입력 소스 결정
source_text = None
source_label = None
pdf_truncated = False
if mode == "pdf" and pdf is not None:
    from pypdf import PdfReader
    tmp = Path(f"/tmp/_st_{pdf.name}")
    tmp.write_bytes(pdf.read())
    total_pages = len(PdfReader(str(tmp)).pages)
    pdf_truncated = total_pages > 30
    source_text = extract_text_from_pdf(str(tmp))
    source_label = pdf.name
elif mode == "txt" and txt is not None:
    source_text = txt.read().decode("utf-8", errors="replace")
    source_label = txt.name
elif mode == "paste" and pasted and pasted.strip():
    source_text = pasted.strip()
    source_label = T["mode_paste"]

EXPECTED_CHARS = 2200   # sample.pdf 30p 기준 ~1900자, 여유 두고 2200

if run and source_text:
    with st.status(T["status_running"], expanded=True) as status:
        st.write(f"{T['status_pdf']}: {source_label}")
        st.write(f"   → {len(source_text):,} {T['status_chars']}")
        st.write(T["status_calling"])

        progress_bar = st.progress(0, text=T["progress_label"])
        raw_placeholder = st.empty()
        t0 = time.time()
        last_render = 0.0
        final_acc = ""
        for acc in generate_quiz_stream(source_text):
            final_acc = acc
            now = time.time()
            if now - last_render > 0.1:
                pct = min(int(len(acc) / EXPECTED_CHARS * 100), 99)
                elapsed = now - t0
                progress_bar.progress(
                    pct,
                    text=f"{T['progress_label']} — {len(acc):,}자 · {elapsed:.0f}초",
                )
                raw_placeholder.code(acc, language="json", wrap_lines=True)
                last_render = now
        elapsed_total = time.time() - t0
        progress_bar.progress(100, text=f"{T['progress_done']} — {len(final_acc):,}자 · {elapsed_total:.1f}초")
        raw_placeholder.empty()
        with raw_placeholder.expander(T["raw_expander"]):
            st.code(final_acc, language="json", wrap_lines=True)
        status.update(label=T["status_done"], state="complete")

    try:
        quiz = parse_quiz(final_acc)
    except json.JSONDecodeError as e:
        st.error(f"❌ 모델 응답 파싱 실패: {e}. 다시 시도하거나 입력을 짧게 해보세요.")
        if default_quiz.exists():
            st.info("ℹ️ 백업 결과(sample.quiz.json)로 대체합니다.")
            quiz = json.loads(default_quiz.read_text(encoding="utf-8"))
        else:
            st.stop()
    st.session_state["quiz"] = quiz
    st.session_state["pdf_truncated"] = pdf_truncated
    st.session_state["from_default"] = False

# session_state에 quiz 있으면 재사용 (라디오 클릭 등 rerun 시)
if "quiz" in st.session_state:
    if st.session_state.get("from_default"):
        st.info(T["info_default"])
    elif st.session_state.get("pdf_truncated"):
        st.info(T["info_pdf_truncated"])
    render_quiz(st.session_state["quiz"])

elif default_quiz.exists():
    st.session_state["quiz"] = json.loads(default_quiz.read_text(encoding="utf-8"))
    st.session_state["from_default"] = True
    st.session_state["pdf_truncated"] = False
    st.info(T["info_default"])
    render_quiz(st.session_state["quiz"])

else:
    st.warning(T["warn_no_input"])
