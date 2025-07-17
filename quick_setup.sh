#!/bin/bash

echo "🚀 전화 연결 시스템 빠른 설정 스크립트"
echo "========================================"

# 가상환경 활성화
echo "📦 가상환경 활성화 중..."
source venv/bin/activate

# 패키지 설치 상태 확인
echo "🔍 패키지 설치 상태 확인 중..."
if ! python -c "import fastapi, twilio, websockets, uvicorn" 2>/dev/null; then
    echo "❌ 패키지가 설치되지 않았습니다. 설치 중..."
    pip install -r requirements.txt
else
    echo "✅ 모든 패키지가 설치되어 있습니다."
fi

# .env 파일 생성 도움
if [ ! -f .env ]; then
    echo "⚠️  .env 파일이 없습니다."
    echo "📝 .env.example을 .env로 복사하시겠습니까? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo "✅ .env 파일이 생성되었습니다."
        echo "🔧 .env 파일을 편집하여 실제 값으로 변경하세요:"
        echo "   - OPENAI_API_KEY: OpenAI API 키"
        echo "   - PUBLIC_DOMAIN: 외부에서 접근 가능한 도메인"
        echo ""
        echo "편집 후 Enter를 눌러 계속하세요..."
        read -r
    fi
fi

# 설정 테스트 실행
echo "🧪 설정 테스트 실행 중..."
python test_setup.py

# 결과에 따른 안내
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 설정 완료! 서버를 실행하시겠습니까? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "🚀 서버 실행 중..."
        echo "서버를 중지하려면 Ctrl+C를 누르세요."
        echo ""
        python main.py
    else
        echo "서버를 실행하려면 다음 명령어를 사용하세요:"
        echo "source venv/bin/activate && python main.py"
    fi
else
    echo ""
    echo "❌ 설정에 문제가 있습니다. 위의 오류를 해결한 후 다시 시도하세요."
    echo ""
    echo "도움말:"
    echo "1. .env 파일 편집: nano .env"
    echo "2. 설정 테스트: python test_setup.py"
    echo "3. 서버 실행: python main.py"
fi