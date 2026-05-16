"""
Gemma 4 로컬 LLM 강의 복습 퀴즈 생성기
=========================================
PDF 강의자료를 읽고 복습용 자가 점검 퀴즈를 자동 생성합니다.

사용법:
    python quiz_generator.py <PDF 경로>
    python quiz_generator.py sample.pdf
"""

import json
import re
import sys
import time
from pathlib import Path

import ollama
from pypdf import PdfReader


# ============================================================
# 설정
# ============================================================

MODEL = "gemma4:e2b"
# MODEL = "gemma4:e4b"   # 더 큰 모델 — 디스크 9.6GB 필요

NUM_MCQ = 5
NUM_SHORT = 3
MAX_PAGES = 30   # num_ctx 16K~32K 안에 들어오게 페이지 상한


QUIZ_SCHEMA = {
    "type": "object",
    "properties": {
        "topic": {
            "type": "string",
            "description": "강의자료의 핵심 주제 한 줄"
        },
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["객관식", "단답형"]},
                    "question": {"type": "string"},
                    "choices": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "answer": {"type": "string"},
                    "explanation": {"type": "string"}
                },
                "required": ["type", "question", "answer", "explanation"]
            }
        }
    },
    "required": ["topic", "questions"]
}


# ============================================================
# 시스템 프롬프트: 퀴즈 출제자 페르소나
# ============================================================

SYSTEM_PROMPT = f"""당신은 대학교 학생의 시험 대비를 돕는 친절한 조교입니다.

주어진 강의자료를 읽고, 학생이 핵심 개념을 제대로 이해했는지 스스로 점검할 수 있는 복습 퀴즈를 만듭니다.

[중요 출력 형식]
- 사고 과정 보여주지 말고 바로 JSON으로만 답하세요.
- 마크다운 코드 블록(```)으로 감싸지 마세요. 순수 JSON만 출력.
- 정확한 형식: {{"topic": "주제 한 줄", "questions": [{{"type": "객관식", "question": "문제", "choices": ["보기1","보기2","보기3","보기4"], "answer": "정답", "explanation": "해설"}}, ...]}}

[출제 규칙]
- 객관식 {NUM_MCQ}문제 + 단답형 {NUM_SHORT}문제, 총 {NUM_MCQ + NUM_SHORT}문제
- 객관식: 보기 4개, 정답 외 3개는 학생이 헷갈릴 만한 그럴듯한 오답
- 단답형: choices 필드 생략 가능, 한 단어 또는 한 문장 이내 답
- 모든 문제는 반드시 강의자료에 명시된 내용에만 근거할 것 (추측 금지)
- 단순 암기보다 개념 이해를 묻는 문제 위주
- 정답과 함께 1~2문장 짜리 해설을 반드시 포함
- 모든 텍스트는 한국어로 작성
"""


def _extract_json(s: str) -> str:
    """모델 응답에서 JSON 부분만 추출 (markdown fence / 잡문 / 다중 객체 안전)."""
    # ```json ... ``` 블록 우선
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", s, re.DOTALL)
    if m:
        return m.group(1)
    # 첫 { 부터 시작해서 raw_decode로 첫 객체만 잘라냄 (모델이 두 개 뱉어도 안전)
    start = s.find("{")
    if start < 0:
        return s
    try:
        decoder = json.JSONDecoder()
        _, end = decoder.raw_decode(s[start:])
        return s[start : start + end]
    except json.JSONDecodeError:
        # raw_decode 실패 — 마지막 } 까지 폴백
        end = s.rfind("}")
        if end > start:
            return s[start : end + 1]
        return s


# ============================================================
# 1단계: PDF 텍스트 추출
# ============================================================

def extract_text_from_pdf(pdf_path: str, max_pages: int = MAX_PAGES) -> str:
    """PDF에서 페이지별 텍스트를 추출하고 합칩니다 (앞 max_pages 페이지만)."""
    reader = PdfReader(pdf_path)
    pages = []
    for i, page in enumerate(reader.pages[:max_pages], 1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append(f"--- Page {i} ---\n{text}")
    return "\n\n".join(pages)


# ============================================================
# 2단계: Gemma 4 호출 (JSON 스키마 강제)
# ============================================================

def generate_quiz(lecture_text: str) -> dict:
    """강의 텍스트를 받아 JSON 형식 퀴즈를 반환합니다."""
    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "아래 강의자료를 읽고 복습 퀴즈를 만들어 주세요.\n\n"
                    "=== 강의자료 시작 ===\n"
                    f"{lecture_text}\n"
                    "=== 강의자료 끝 ==="
                ),
            },
        ],
        format=QUIZ_SCHEMA,
        think=False,
        options={
            "temperature": 0.3,   # 창의성보다 정확성 — 강의자료 밖 내용 만들지 않게
            "num_ctx": 32768,
            "num_predict": 4000,
        },
    )
    raw = response["message"]["content"]
    return json.loads(_extract_json(raw))


def _chat_kwargs(lecture_text: str) -> dict:
    return dict(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "아래 강의자료를 읽고 복습 퀴즈를 만들어 주세요.\n\n"
                    "=== 강의자료 시작 ===\n"
                    f"{lecture_text}\n"
                    "=== 강의자료 끝 ==="
                ),
            },
        ],
        format=QUIZ_SCHEMA,
        think=False,
        options={
            "temperature": 0.3,
            "num_ctx": 32768,
            "num_predict": 4000,
        },
    )


def generate_quiz_stream(lecture_text: str):
    """누적된 응답 텍스트를 chunk마다 yield. 호출자가 마지막 acc로 parse_quiz() 호출."""
    acc = ""
    for chunk in ollama.chat(stream=True, **_chat_kwargs(lecture_text)):
        delta = chunk.get("message", {}).get("content", "")
        if delta:
            acc += delta
            yield acc


def parse_quiz(raw: str) -> dict:
    return json.loads(_extract_json(raw))


# ============================================================
# 3단계: 예쁘게 출력
# ============================================================

def print_quiz(quiz: dict) -> None:
    """터미널에 보기 좋게 출력합니다."""
    line = "=" * 60
    print(f"\n{line}")
    print(f"  📚  주제: {quiz.get('topic', '(주제 미정)')}")
    print(line)

    for i, q in enumerate(quiz.get("questions", []), 1):
        qtype = q.get("type", "")
        print(f"\n[문제 {i}] ({qtype})")
        print(f"  Q. {q.get('question', '')}")
        if qtype == "객관식":
            for j, c in enumerate(q.get("choices", []), 1):
                print(f"     {j}) {c}")
        print(f"  ✓ 정답: {q.get('answer', '')}")
        print(f"  💡 해설: {q.get('explanation', '')}")

    print(f"\n{line}\n")


# ============================================================
# 메인
# ============================================================

def main():
    input_path = Path(sys.argv[1] if len(sys.argv) > 1 else "sample.pdf")

    if not input_path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {input_path}")
        sys.exit(1)

    if input_path.suffix.lower() in (".txt", ".md"):
        print(f"📄 텍스트 파일 읽는 중: {input_path}")
        text = input_path.read_text(encoding="utf-8")
    else:
        print(f"📄 PDF 읽는 중: {input_path}")
        text = extract_text_from_pdf(str(input_path))
    print(f"   → {len(text):,} 글자 추출")

    print(f"\n🤖 Gemma 4 ({MODEL})로 퀴즈 생성 중... (10~60초)")
    t0 = time.time()
    quiz = generate_quiz(text)
    elapsed = time.time() - t0
    print(f"   → 완료 ({elapsed:.1f}초)")

    print_quiz(quiz)

    # 결과를 JSON으로도 저장 (백업/공유용)
    out_path = Path(pdf_path).with_suffix(".quiz.json")
    out_path.write_text(json.dumps(quiz, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"💾 JSON 저장: {out_path}\n")


if __name__ == "__main__":
    main()
