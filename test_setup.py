#!/usr/bin/env python3
"""
전화 연결 시스템 설정 테스트 스크립트
"""

import os
import sys

def test_imports():
    """필수 패키지 import 테스트"""
    print("📦 패키지 import 테스트...")
    
    try:
        import fastapi
        print("✅ FastAPI 설치됨")
    except ImportError:
        print("❌ FastAPI 설치 필요")
        return False
    
    try:
        import twilio
        print("✅ Twilio 설치됨")
    except ImportError:
        print("❌ Twilio 설치 필요")
        return False
    
    try:
        import websockets
        print("✅ WebSockets 설치됨")
    except ImportError:
        print("❌ WebSockets 설치 필요")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn 설치됨")
    except ImportError:
        print("❌ Uvicorn 설치 필요")
        return False
    
    return True

def test_env_vars():
    """환경 변수 테스트"""
    print("\n🔧 환경 변수 확인...")
    
    # .env 파일 확인
    if os.path.exists('.env'):
        print("✅ .env 파일 존재")
        from dotenv import load_dotenv
        load_dotenv()
    else:
        print("⚠️  .env 파일 없음 - .env.example을 참조하여 생성하세요")
    
    # 필수 환경 변수 확인
    openai_key = os.getenv('OPENAI_API_KEY')
    public_domain = os.getenv('PUBLIC_DOMAIN')
    port = os.getenv('PORT', '5050')
    
    if openai_key and openai_key != 'sk-your-openai-api-key-here':
        print("✅ OPENAI_API_KEY 설정됨")
    else:
        print("❌ OPENAI_API_KEY 설정 필요")
    
    if public_domain and public_domain != 'https://your-domain.com':
        print(f"✅ PUBLIC_DOMAIN 설정됨: {public_domain}")
    else:
        print("❌ PUBLIC_DOMAIN 설정 필요")
    
    print(f"ℹ️  PORT: {port}")
    
    return bool(openai_key and public_domain)

def test_main_file():
    """main.py 파일 확인"""
    print("\n📄 main.py 파일 확인...")
    
    if os.path.exists('main.py'):
        print("✅ main.py 파일 존재")
        return True
    else:
        print("❌ main.py 파일 없음")
        return False

def main():
    """메인 테스트 함수"""
    print("🔍 전화 연결 시스템 설정 테스트 시작\n")
    
    tests = [
        ("패키지 설치", test_imports),
        ("환경 변수", test_env_vars),
        ("메인 파일", test_main_file)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name} 테스트 실패: {e}")
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 모든 테스트 통과! 서버를 실행할 준비가 되었습니다.")
        print("\n다음 명령어로 서버를 실행하세요:")
        print("source venv/bin/activate && python main.py")
    else:
        print("⚠️  일부 테스트 실패. 위의 오류를 해결한 후 다시 시도하세요.")
        print("\n해결 방법:")
        print("1. .env.example을 .env로 복사하고 실제 값으로 수정")
        print("2. 필요한 패키지 설치: pip install -r requirements.txt")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)