# 🤖 GPT-4o-mini 전화 음성 어시스턴트

Twilio와 OpenAI GPT-4o-mini를 사용한 실시간 전화 음성 어시스턴트 애플리케이션입니다.

## 🚨 전화 연결 문제 해결

**"도대체 왜 전화가 안가냐고"** 문제의 주요 원인과 해결책:

### 주요 문제점들
1. ❌ 환경 변수 미설정 (OPENAI_API_KEY, PUBLIC_DOMAIN)
2. ❌ 서버 미실행 상태
3. ❌ 의존성 패키지 미설치 (해결됨)
4. ❌ 외부 접근 불가능한 네트워크 설정

## 🛠️ 빠른 해결 방법

### 1단계: 자동 설정 스크립트 실행
```bash
./quick_setup.sh
```

### 2단계: 수동 설정 (필요시)
```bash
# 1. 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 실제 값 입력

# 2. 가상환경 활성화
source venv/bin/activate

# 3. 설정 테스트
python test_setup.py

# 4. 서버 실행
python main.py
```

## 📋 필수 설정 항목

### 환경 변수 (.env 파일)
```env
OPENAI_API_KEY=sk-your-actual-openai-api-key
PUBLIC_DOMAIN=https://your-domain.com
PORT=5050
```

### Twilio 설정
1. [Twilio Console](https://console.twilio.com/)에서 전화번호 구매
2. Webhook URL 설정: `https://your-domain.com/incoming-call`

## 🔧 사용 가능한 도구들

### 설정 테스트 스크립트
```bash
python test_setup.py
```
- 패키지 설치 상태 확인
- 환경 변수 설정 확인
- 파일 존재 여부 확인

### 빠른 설정 스크립트
```bash
./quick_setup.sh
```
- 전체 설정 과정 자동화
- 대화형 설정 도움
- 자동 서버 실행 옵션

## 🌐 네트워크 설정

### 로컬 테스트 (ngrok 사용)
```bash
# 터미널 1: ngrok 실행
ngrok http 5050

# 터미널 2: 환경 변수 설정 후 서버 실행
export PUBLIC_DOMAIN="https://your-ngrok-url.ngrok.io"
source venv/bin/activate
python main.py
```

### 프로덕션 환경 (AWS EC2)
```bash
# 보안 그룹에서 포트 5050 개방
# 공개 IP 또는 도메인 사용
export PUBLIC_DOMAIN="http://your-ec2-public-ip:5050"
```

## 🚀 서버 실행 및 테스트

### 서버 실행
```bash
source venv/bin/activate
python main.py
```

### 상태 확인
```bash
curl http://localhost:5050/health
```

### 엔드포인트
- `GET /`: 서버 상태 확인
- `GET /health`: 헬스 체크
- `POST /incoming-call`: Twilio webhook (전화 수신)
- `WebSocket /media-stream`: 음성 스트리밍

## 📞 Twilio 설정 단계

1. **전화번호 구매**: Twilio Console에서 전화번호 구매
2. **Webhook 설정**: 
   - Voice URL: `https://your-domain.com/incoming-call`
   - HTTP Method: POST
3. **테스트**: 구매한 번호로 전화 걸기

## 🐛 문제 해결

### 일반적인 오류들

#### "OPENAI_API_KEY not set"
```bash
# .env 파일에 API 키 설정
OPENAI_API_KEY=sk-your-actual-key
```

#### "PUBLIC_DOMAIN not set"
```bash
# .env 파일에 공개 도메인 설정
PUBLIC_DOMAIN=https://your-domain.com
```

#### "Connection refused"
```bash
# 방화벽 설정 확인
sudo ufw allow 5050
# 또는 보안 그룹에서 포트 개방
```

#### "Module not found"
```bash
# 가상환경 활성화 확인
source venv/bin/activate
pip install -r requirements.txt
```

## 📚 추가 리소스

- [OpenAI API 문서](https://platform.openai.com/docs)
- [Twilio Voice API 문서](https://www.twilio.com/docs/voice)
- [FastAPI 문서](https://fastapi.tiangolo.com/)

## 🔍 로그 및 디버깅

### 서버 로그 확인
서버 실행 시 콘솔에 다음과 같은 로그가 출력됩니다:
```
Incoming call - Headers: ...
WebSocket URL: wss://your-domain.com/media-stream
Connected to OpenAI WebSocket
```

### 문제 진단 체크리스트
- [ ] 환경 변수 설정 완료
- [ ] 서버 실행 중
- [ ] 외부 접근 가능한 도메인 설정
- [ ] Twilio webhook 설정 완료
- [ ] 방화벽/보안 그룹 설정 완료

## 💡 팁

1. **개발 환경**: ngrok 사용 추천
2. **프로덕션 환경**: HTTPS 사용 필수
3. **디버깅**: 서버 로그와 Twilio 로그 함께 확인
4. **성능**: 안정적인 인터넷 연결 필요

---

**이제 전화가 제대로 연결될 것입니다!** 🎉

문제가 지속되면 `python test_setup.py`를 실행하여 설정을 다시 확인하세요.