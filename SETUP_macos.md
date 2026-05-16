# macOS / Linux 셋업 가이드

> Apple Silicon / Intel Mac, Ubuntu 22.04+ 기준

## 사전 요구사항

- 디스크 여유 **10 GB 이상** (모델 7.2GB + 환경 1GB + 여유분)
- RAM **8 GB 권장** (최소 4 GB)
- Python **3.9 이상**
- 인터넷 (모델 다운로드 시에만)

---

## 1. Ollama 설치

**macOS — 한 줄로:**

```bash
brew install --cask ollama-app
```

Homebrew 없으면 → https://ollama.com/download 에서 `.dmg` 받아서 설치.

**Linux:**

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

설치 확인:

```bash
ollama --version
```

버전 번호 (예: `ollama version is 0.20.6`) 나오면 OK.

---

## 2. Gemma 4 모델 받기

```bash
ollama pull gemma4:e2b
```

약 7.2GB, 인터넷 속도에 따라 5~30분.

```bash
ollama list
```

목록에 `gemma4:e2b` 보이면 성공.

---

## 3. 프로젝트 받기 + Python 환경

```bash
git clone https://github.com/<your-id>/gemma4-quiz.git
cd gemma4-quiz

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 4. 실행

자기 강의자료 PDF를 폴더에 두고 (예: `lecture.pdf`):

```bash
python quiz_generator.py lecture.pdf
```

또는 웹 UI:

```bash
streamlit run app.py
# → http://localhost:8501 자동으로 열림
```

첫 호출은 모델 로딩 10~30초 + 추론 1~2분. 이후는 빠름.

---

## 문제 해결

| 증상 | 해결 |
|---|---|
| `ollama: command not found` | 터미널 새로 열기 또는 `source ~/.zshrc` |
| 응답이 비어있음 | `think=False` 옵션 확인 (코드에 이미 들어있음) |
| `Could not connect to Ollama` | `ollama serve` 한 번 실행 (또는 메뉴바 아이콘 확인) |
| 추론이 너무 느림 | `MAX_PAGES`를 20 이하로, 또는 e2b 모델 사용 확인 |
