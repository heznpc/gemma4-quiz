# Gemma 4 강의 복습 퀴즈 생성기

PDF / 텍스트 강의자료를 던지면 복습용 자가 점검 퀴즈를 자동으로 만들어 줍니다.
**외부 API 호출 없이 노트북에서 직접 돌아갑니다.**

> 2026 소프트웨어학부 1학기 세미나 발표 자료입니다.
> 발표 슬라이드는 [`gemma4-seminar.pptx`](./gemma4-seminar.pptx) 참고.

---

## 🖥 OS별 셋업 가이드

| 환경 | 가이드 |
|---|---|
| macOS / Linux | [SETUP_macos.md](./SETUP_macos.md) |
| Windows | [SETUP_windows.md](./SETUP_windows.md) |

---

## 사전 준비 (한 번만)

```bash
# 1) Ollama 설치
brew install --cask ollama-app          # macOS
curl -fsSL https://ollama.com/install.sh | sh   # Linux
# Windows: https://ollama.com/download/windows 에서 .exe 받기

# 2) Gemma 4 모델 받기
ollama pull gemma4:e2b                  # 약 7.2GB · 폰까지 가능한 가장 가벼운 모델

# 3) Python 패키지
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt   # Windows: .venv\Scripts\pip
```

---

## 실행

### CLI

```bash
.venv/bin/python quiz_generator.py lecture.pdf
```

PDF / TXT / MD 파일 모두 입력 가능.

### 웹 UI

```bash
.venv/bin/streamlit run app.py
# → http://localhost:8501
```

- PDF 업로드 / TXT 업로드 / 텍스트 직접 입력 3가지 모드.
- 결과 JSON 다운로드 가능.

---

## 결과 예시

```
============================================================
  📚  주제: 운영체제의 프로세스와 스레드
============================================================

[문제 1] (객관식)
  Q. 프로세스와 스레드의 차이로 가장 적절한 것은?
     1) 프로세스는 자원을 공유하고 스레드는 공유하지 않는다
     2) 스레드는 같은 프로세스 내에서 메모리를 공유한다
     3) 프로세스는 항상 단일 스레드로 동작한다
     4) 스레드는 운영체제가 인식하지 못한다
  ✓ 정답: 스레드는 같은 프로세스 내에서 메모리를 공유한다
  💡 해설: 스레드는 같은 프로세스의 코드·데이터·힙을 공유하며 스택만 별도로 가집니다.
```

---

## 폴더 구조

```
gemma4-quiz/
├── quiz_generator.py        # 메인 코드 (PDF → Gemma 4 → JSON 퀴즈)
├── app.py                   # Streamlit 웹 UI
├── precheck.sh              # 시연 전 환경 자동 체크
├── requirements.txt
├── SETUP_macos.md           # macOS / Linux 셋업
├── SETUP_windows.md         # Windows 셋업
├── gemma4-seminar.pptx      # 발표 슬라이드 (17장)
└── README.md
```

---

## 모델 바꾸기

`quiz_generator.py` 상단의 `MODEL` 상수만 바꾸면 됩니다.

```python
MODEL = "gemma4:e2b"   # 기본 (시연용 — 빠름, 7.2GB)
MODEL = "gemma4:e4b"   # 더 큰 모델 (멀티모달 강함, 9.6GB)
```

`temperature`, `num_ctx`, `num_predict` 도 같은 파일 안에 있습니다.

---

## 핵심 설계

1. **PDF → 텍스트 추출** (`pypdf`) — 텍스트 위주 강의자료엔 충분
2. **시스템 프롬프트로 페르소나 박기** — 결과 품질의 70%를 결정
3. **JSON 스키마로 출력 강제** — `format=` 파라미터에 schema 전달, 파싱 실패 0
4. **Ollama Python 클라이언트로 한 번 호출** — `think=False` 로 thinking 모드 끄기

자세한 시행착오 / 함정은 [발표 슬라이드](./gemma4-seminar.pptx) 12~14번 참고.

---

## 시연·시연자용

### 시연 5분 전 자동 체크

```bash
bash precheck.sh
```

Ollama 서버, 모델, 워밍업, Streamlit, 패키지까지 자동 점검.

### 백업 플랜

- 모델이 이상한 답을 뱉으면 `temperature`를 0.1로 낮추거나 다시 실행
- 응답이 너무 길어 잘리면 `MAX_PAGES`를 더 작게
- 그래도 안 되면 미리 저장해둔 결과를 보여주기

---

## 보안 주의

Ollama 서버를 외부에 노출하지 마세요 (CVE-2026-7482 등 사례).
기본 설정은 `127.0.0.1` 바인딩이라 안전하지만, `OLLAMA_HOST=0.0.0.0` 등으로 바꿔서 외부 노출 시 인증 / 방화벽 / 패치된 버전 확인 필수.

---

## 라이선스

학습·연구·발표 용도로 자유롭게 사용. Gemma 4 모델 자체는 [Gemma Terms of Use](https://ai.google.dev/gemma/terms) 적용.
