Status: Lab — not production

# Gemma 4 강의 복습 퀴즈 생성기

PDF / 텍스트 강의자료를 입력하면 복습용 자가 점검 퀴즈를 자동으로 생성합니다.
**외부 API 호출 없이 로컬 노트북에서 직접 실행됩니다.**

> 2026 소프트웨어학부 1학기 세미나 발표 자료로 시작된 학습용 도구입니다.
> 발표 슬라이드는 [`gemma4-seminar.pptx`](./gemma4-seminar.pptx)를 참고해 주십시오.

---

## Currently implemented

- **CLI 퀴즈 생성기** (`quiz_generator.py`): PDF / TXT / MD 입력 → Gemma 4 (Ollama) 호출 → JSON 스키마 강제 → 객관식 5문제 + 단답형 3문제 출력
- **Streamlit 웹 UI** (`app.py`): 파일 업로드 / 텍스트 직접 입력 3가지 모드, 결과 JSON 다운로드
- **JSON 스키마 강제 디코딩** (`format=QUIZ_SCHEMA`): 모델 출력 형식 일탈을 Ollama 측에서 차단
- **JSON 추출 폴백** (`_extract_json`): 마크다운 펜스 / 잡문 / 다중 객체 응답에 대한 안전 파서
- **시연 사전 체크 스크립트** (`precheck.sh`): Ollama 서버 / 모델 / 워밍업 / Streamlit / 패키지 점검
- **OS별 셋업 가이드**: [SETUP_macos.md](./SETUP_macos.md), [SETUP_windows.md](./SETUP_windows.md)

## Planned

- 영문 README 추가 (Supporting tier 승격 조건)
- 단위 테스트 (현재 `pytest` 환경만 존재, 실제 테스트 0개)
- 멀티모달 입력 (`pdf2image` + Pillow는 의존성에만 선언, 미사용)

## Design intent

- **로컬 LLM 한정** — 강의자료 저작권 보호와 학생 데이터 외부 유출 방지가 1차 목적. 외부 API 호출 경로는 의도적으로 두지 않습니다.
- **JSON 스키마 강제** — 프롬프트 엔지니어링만으로는 출력 형식이 흔들립니다. Ollama의 `format=` 파라미터로 스키마를 강제해 파싱 실패율을 0에 가깝게 유지합니다.
- **시스템 프롬프트 = 페르소나** — "친절한 조교" 페르소나가 결과 품질의 큰 비중을 차지합니다. 출제 규칙은 강의자료에 명시된 내용에만 근거하도록 명시적으로 박았습니다.
- **`think=False`** — Gemma 4의 thinking 모드는 응답 길이만 늘리고 JSON 출력 안정성을 해쳤습니다. 명시적으로 끕니다.
- **`temperature=0.3`** — 창의성보다 강의자료 충실도를 우선합니다.

## Non-goals

- **클라우드 LLM 통합** (OpenAI / Anthropic / Gemini API) — 위 "로컬 LLM 한정" 원칙과 충돌합니다.
- **자동 채점 / LMS 연동** — 학생 자가 점검 도구이며, 평가 시스템이 아닙니다.
- **프로덕션 배포** — Lab 단계 학습용 도구입니다. SLA / 모니터링 / 사용자 인증 없음.
- **대규모 강의자료 처리** — `MAX_PAGES=30` 상한으로 `num_ctx=32768` 범위를 보장합니다. 그 이상은 분할 입력 필요.

## Redacted

- 외부 학생 / 강사 / 강의자료 식별자
- 시연 대상 강의명 및 기관명

---

## 사전 준비 (한 번만)

```bash
# 1) Ollama 설치
brew install --cask ollama-app                    # macOS
curl -fsSL https://ollama.com/install.sh | sh     # Linux
# Windows: https://ollama.com/download/windows

# 2) Gemma 4 모델 받기
ollama pull gemma4:e2b                            # 약 7.2GB

# 3) Python 패키지
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt         # Windows: .venv\Scripts\pip
```

## 실행

```bash
# CLI
.venv/bin/python quiz_generator.py lecture.pdf

# 웹 UI
.venv/bin/streamlit run app.py
# → http://localhost:8501
```

## 모델 / 파라미터 변경

`quiz_generator.py` 상단 상수만 수정합니다.

```python
MODEL = "gemma4:e2b"   # 기본 (빠름, 7.2GB)
MODEL = "gemma4:e4b"   # 멀티모달, 9.6GB
# temperature, num_ctx, num_predict 도 같은 파일 안에 있습니다.
```

## 폴더 구조

```
gemma4-quiz/
├── quiz_generator.py     # CLI 메인 (PDF → Gemma 4 → JSON)
├── app.py                # Streamlit 웹 UI
├── precheck.sh           # 시연 환경 자동 체크
├── requirements.txt
├── SETUP_macos.md
├── SETUP_windows.md
├── gemma4-seminar.pptx   # 발표 슬라이드
└── README.md
```

## 보안 주의

- Ollama 서버를 외부에 노출하지 마십시오. 기본 설정은 `127.0.0.1` 바인딩으로 안전하지만 `OLLAMA_HOST=0.0.0.0`로 변경 시 인증 / 방화벽 / 패치 버전 확인이 필수입니다.
- 강의자료에 외부 학생 식별 정보가 포함된 경우 입력 전 마스킹하십시오.

## 라이선스

학습·연구·발표 용도로 자유롭게 사용 가능합니다. Gemma 4 모델 자체는 [Gemma Terms of Use](https://ai.google.dev/gemma/terms)를 따릅니다.
