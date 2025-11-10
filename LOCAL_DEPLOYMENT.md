# 로컬 PC 백엔드 + Streamlit Cloud 프론트엔드 배포 가이드

## 개요
- **백엔드**: 로컬 PC에서 실행 (ngrok으로 외부 노출)
- **프론트엔드**: Streamlit Community Cloud에 배포

---

## 1단계: ngrok 설치

### Windows

#### 방법 1: 직접 다운로드 (추천)
1. https://ngrok.com/download 접속
2. **Windows (64-bit)** 다운로드
3. 압축 해제 후 원하는 폴더에 저장 (예: `C:\ngrok\`)
4. 환경 변수 PATH에 추가:
   - 시스템 설정 → 고급 시스템 설정 → 환경 변수
   - Path 변수에 `C:\ngrok\` 추가

#### 방법 2: Chocolatey
```powershell
choco install ngrok
```

### 설치 확인
```powershell
ngrok version
```

---

## 2단계: ngrok 계정 설정

### 2-1. 회원가입
1. https://dashboard.ngrok.com/signup 접속
2. Google/GitHub 계정으로 가입 (무료)

### 2-2. Authtoken 설정
1. https://dashboard.ngrok.com/get-started/your-authtoken 접속
2. Authtoken 복사
3. PowerShell에서 실행:
```powershell
ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
```

성공 메시지:
```
Authtoken saved to configuration file: C:\Users\...\AppData\Local\ngrok\ngrok.yml
```

---

## 3단계: 백엔드 실행

### 3-1. 환경 변수 설정
`backend/.env` 파일 생성 (또는 기존 파일 확인):
```env
OPENAI_API_KEY=your-openai-api-key-here
```

### 3-2. 백엔드 서버 실행
**PowerShell 터미널 1:**
```powershell
cd C:\Users\baekhadev\Desktop\구름턴\dyu_RAG_CHAT\backend
python main.py
```

다음 메시지 확인:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
✅ RAG 시스템 초기화 완료!
```

**이 터미널은 계속 열어두세요!**

---

## 4단계: ngrok 터널 생성

### 4-1. ngrok 실행
**PowerShell 터미널 2 (새 터미널):**
```powershell
ngrok http 8000
```

### 4-2. URL 확인
화면에 다음과 같이 표시됩니다:

```
ngrok

Session Status                online
Account                       Your Name (Plan: Free)
Version                       3.x.x
Region                        Asia Pacific (ap)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://xxxx-xxxx-xxxx.ngrok-free.app -> http://localhost:8000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**Forwarding 줄의 HTTPS URL을 복사하세요!**
예: `https://1234-5678-9abc.ngrok-free.app`

**이 터미널도 계속 열어두세요!**

---

## 5단계: GitHub에 푸시

```powershell
# PowerShell 터미널 3 (새 터미널)
cd C:\Users\baekhadev\Desktop\구름턴\dyu_RAG_CHAT

git add .
git commit -m "배포 준비: 환경변수 설정 및 ngrok 대응"
git push origin main
```

---

## 6단계: Streamlit Cloud 배포

### 6-1. Streamlit Cloud 접속
1. https://share.streamlit.io 접속
2. **GitHub 계정으로 로그인**
3. **New app** 클릭

### 6-2. 앱 설정
- **Repository**: `Burgerjoa/dyu_RAG_CHAT`
- **Branch**: `main`
- **Main file path**: `frontend/app.py`

### 6-3. Advanced settings
**Python version**: `3.11`

**Secrets** 클릭 후 추가:
```toml
API_BASE_URL = "https://1234-5678-9abc.ngrok-free.app"
```
**⚠️ 4-2에서 복사한 ngrok URL을 정확히 입력하세요!**

### 6-4. 배포
**Deploy!** 클릭

배포 진행 상황 확인:
- Installing dependencies...
- Running app...
- Your app is live! 🎉

---

## 7단계: 테스트

### 7-1. 백엔드 테스트
브라우저에서 ngrok URL 접속:
```
https://1234-5678-9abc.ngrok-free.app/health
```

응답:
```json
{
  "status": "healthy",
  "rag_system_initialized": true,
  "api_version": "1.0.0"
}
```

**ngrok 무료 버전 경고:**
첫 접속 시 ngrok 경고 페이지가 나올 수 있습니다.
→ "Visit Site" 클릭하면 정상 작동

### 7-2. 프론트엔드 테스트
Streamlit 앱 URL 접속 (예: `https://your-app.streamlit.app`)

테스트 질문:
- "수강신청은 언제야?"
- "장학금 받으려면 어떻게 해야 해?"

답변 및 출처 확인!

---

## 8단계: 운영 방법

### 일상적인 실행 순서
1. **터미널 1**: 백엔드 실행
   ```powershell
   cd backend
   python main.py
   ```

2. **터미널 2**: ngrok 실행
   ```powershell
   ngrok http 8000
   ```

3. **ngrok URL이 바뀌었다면?**
   - Streamlit Cloud → Apps → 앱 선택 → Settings → Secrets
   - `API_BASE_URL` 업데이트
   - Reboot app

### PC를 계속 켜두어야 합니다
- 백엔드가 PC에서 실행되므로 **PC가 꺼지면 서비스 중단**
- 절전 모드 비활성화 권장

### ngrok URL 고정 (유료)
**무료 플랜**: PC 재시작 시 URL 변경
**Pro 플랜 ($8/month)**: 고정 URL 사용 가능

---

## 트러블슈팅

### ngrok: command not found
→ 환경 변수 PATH에 ngrok 경로 추가 필요

### ngrok: authentication failed
→ `ngrok config add-authtoken` 다시 실행

### Streamlit에서 "연결 불가"
1. 백엔드 실행 중인지 확인 (터미널 1)
2. ngrok 실행 중인지 확인 (터미널 2)
3. Streamlit Secrets의 `API_BASE_URL`이 최신 ngrok URL인지 확인
4. ngrok URL에 `/health` 접속해서 백엔드 응답 확인

### ngrok 무료 제한 초과
- 월 40,000 요청 제한
- 초과 시 유료 플랜 고려

---

## ngrok 무료 vs 유료

| 기능 | Free | Pro ($8/mo) |
|------|------|-------------|
| URL | 랜덤 변경 | 고정 가능 |
| 요청 수 | 40,000/월 | 무제한 |
| 동시 터널 | 1개 | 3개 |
| 커스텀 도메인 | ❌ | ✅ |

---

## 비용 예상

- **Streamlit Cloud**: 무료
- **ngrok**: 무료 (또는 $8/월)
- **OpenAI API**: 사용량 기반
  - 임베딩 생성 (첫 실행): ~$1-5 (1회만)
  - 질문 답변: ~$0.001/질문
  - 예상: 월 $5-20

---

## 체크리스트

배포 전 확인:
- [ ] Python 3.11 설치
- [ ] OpenAI API 키 발급
- [ ] ngrok 계정 및 authtoken 설정
- [ ] GitHub에 코드 푸시
- [ ] PC 절전 모드 비활성화

실행 시 확인:
- [ ] 백엔드 서버 실행 중 (터미널 1)
- [ ] ngrok 터널 실행 중 (터미널 2)
- [ ] ngrok URL 확인 및 복사
- [ ] Streamlit Secrets 업데이트
- [ ] 테스트 성공

---

## 백업 플랜: Render로 전환

PC 관리가 부담스러우면 언제든 Render로 전환 가능:
1. `DEPLOYMENT.md` 참고
2. Render에 백엔드 배포
3. Streamlit Secrets의 `API_BASE_URL`만 Render URL로 변경

---

**준비 완료! 이제 단계별로 진행하세요! 🚀**
