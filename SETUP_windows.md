# Windows 셋업 가이드

> Windows 10 / 11 기준. PowerShell 사용 권장.

## 사전 요구사항

- 디스크 여유 **10 GB 이상**
- RAM **8 GB 권장** (최소 4 GB)
- Python **3.9 이상** (Microsoft Store 또는 https://python.org)
- 인터넷 (모델 다운로드 시에만)
- Git (https://git-scm.com/download/win)

---

## 1. Ollama 설치

https://ollama.com/download/windows 에서 `OllamaSetup.exe` 받아서 설치.

설치하면 시스템 트레이(우측 하단)에 라마 아이콘이 생기고 자동으로 백그라운드 실행됩니다.

PowerShell 열어서 확인:

```powershell
ollama --version
```

버전 번호 나오면 OK. `command not found` 뜨면 PowerShell 다시 열기.

---

## 2. Gemma 4 모델 받기

```powershell
ollama pull gemma4:e2b
```

약 7.2GB, 5~30분.

> 방화벽이 막으면: Windows Defender 방화벽 → "앱 또는 기능 허용" → `ollama` 추가

```powershell
ollama list
```

`gemma4:e2b` 보이면 성공.

---

## 3. 프로젝트 받기 + Python 환경

PowerShell에서:

```powershell
git clone https://github.com/<your-id>/gemma4-quiz.git
cd gemma4-quiz

python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`Activate.ps1` 실행이 막히면 (정책 에러) 한 번만:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

`python` 명령이 안 먹으면 `py`로:

```powershell
py -m venv .venv
```

---

## 4. 한글 깨짐 방지 (cmd 사용 시)

PowerShell은 보통 OK. **cmd**를 쓸 거면 실행 전에 UTF-8 모드로:

```cmd
chcp 65001
```

이게 안 먹히면 PowerShell로 갈아타세요. 훨씬 안정적.

---

## 5. 실행

자기 강의자료 PDF를 폴더에 두고 (예: `lecture.pdf`):

```powershell
python quiz_generator.py lecture.pdf
```

또는 웹 UI:

```powershell
streamlit run app.py
# → 브라우저에서 http://localhost:8501 자동으로 열림
```

첫 호출은 모델 로딩 10~30초 + 추론 1~2분.

---

## 문제 해결

| 증상 | 해결 |
|---|---|
| `'ollama' is not recognized` | PowerShell 새로 열기. 트레이 아이콘 확인 |
| `Could not connect to Ollama` | 트레이 아이콘 → 종료된 상태면 시작 메뉴에서 Ollama 다시 실행 |
| `Activate.ps1 cannot be loaded` | 위 `Set-ExecutionPolicy` 명령 한 번 실행 |
| 한글이 `?` 또는 `□`로 표시 | PowerShell 사용 또는 `chcp 65001` |
| `pip` 명령 안 됨 | `python -m pip ...` 형식으로 |
| `pulling manifest` 에서 멈춤 | 방화벽 확인 + 잠시 대기, 그래도 안 되면 VPN 켜고 재시도 |
| 추론이 너무 느림 | `MAX_PAGES`를 20 이하로 |
