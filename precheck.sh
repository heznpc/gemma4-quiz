#!/bin/bash
# 시연 5분 전 자동 체크 — bash precheck.sh

set -e
cd "$(dirname "$0")"

echo "=== 1) Ollama 서버 ==="
VER=$(curl -s http://localhost:11434/api/version 2>/dev/null)
if [ -z "$VER" ]; then
  echo "  ❌ 서버 안 떠있음. 'ollama serve > /tmp/o.log 2>&1 &' 로 띄우세요"
  exit 1
fi
echo "  ✅ $VER"

echo ""
echo "=== 2) 모델 등록 ==="
if ollama list | grep -q "gemma4:e2b"; then
  echo "  ✅ gemma4:e2b 등록됨"
else
  echo "  ❌ gemma4:e2b 없음. 'ollama pull gemma4:e2b' 필요"
  exit 1
fi

echo ""
echo "=== 3) 모델 워밍업 (실제 시연과 동일한 num_ctx로 KV 캐시 미리 할당) ==="
echo "  로딩 중..."
OUT=$(curl -s http://localhost:11434/api/chat -d '{"model":"gemma4:e2b","messages":[{"role":"user","content":"hi"}],"stream":false,"think":false,"options":{"num_ctx":32768,"num_predict":5}}' | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if d.get('message',{}).get('content','') or d.get('eval_count',0)>0 else 'FAIL')" 2>/dev/null)
if [ "$OUT" = "OK" ]; then
  echo "  ✅ 응답 정상"
else
  echo "  ⚠️  응답 이상. 한 번 더 시도하거나 재시작"
fi

echo ""
echo "=== 4) Python 패키지 (.venv import 검증) ==="
PKG=$(.venv/bin/python -c "import ollama, pypdf, streamlit; print('OK')" 2>&1)
if [ "$PKG" = "OK" ]; then
  echo "  ✅ ollama, pypdf, streamlit"
else
  echo "  ❌ 패키지 누락: $PKG"
  echo "     → .venv/bin/pip install -r requirements.txt"
  exit 1
fi

echo ""
echo "=== 5) 작업 폴더 + 파일 ==="
for f in quiz_generator.py app.py sample.pdf sample.quiz.json gemma4-seminar.pptx CUE_SHEET.md; do
  if [ -f "$f" ]; then
    echo "  ✅ $f"
  else
    echo "  ❌ $f 없음"
  fi
done

echo ""
echo "=== 6) Streamlit 웹 UI (Bonus 데모) ==="
ST_HTTP=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501 2>/dev/null)
if [ "$ST_HTTP" = "200" ]; then
  echo "  ✅ Streamlit 떠있음 (localhost:8501)"
else
  echo "  ⚠️  Streamlit 안 떠있음. 자동 시작..."
  pkill -f "streamlit run" 2>/dev/null || true
  sleep 1
  .venv/bin/streamlit run app.py --server.headless=true --server.port=8501 --browser.gatherUsageStats=false > /tmp/streamlit.log 2>&1 &
  for i in 1 2 3 4 5 6 7 8 9 10; do
    sleep 1
    ST_HTTP2=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501 2>/dev/null)
    [ "$ST_HTTP2" = "200" ] && break
  done
  if [ "$ST_HTTP2" = "200" ]; then
    echo "  ✅ Streamlit 시작 완료 (localhost:8501, ${i}초)"
  else
    echo "  ❌ Streamlit 시작 실패. /tmp/streamlit.log 확인"
  fi
fi

echo ""
echo "=== 7) 디스크 여유 ==="
df -h / | tail -1 | awk '{print "  💾 여유: " $4}'

echo ""
echo "===================================="
echo "  ✅ 시연 준비 완료"
echo "===================================="
echo ""
echo "수동 단계:"
echo "  1) Wi-Fi 끄기 (제어센터)"
echo "  2) 터미널 글자 크게 (Cmd + +)"
echo "  3) 브라우저 탭 준비:"
echo "     - sample.pdf (96p 보여줄 때)"
echo "     - http://localhost:8501 (Bonus 데모)"
echo ""
echo "데모 명령:"
echo "  CLI:        .venv/bin/python quiz_generator.py sample.pdf"
echo "  Web (Bonus): 브라우저에서 http://localhost:8501"
