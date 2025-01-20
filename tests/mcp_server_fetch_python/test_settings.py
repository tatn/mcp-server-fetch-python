import os

from mcp_server_fetch_python.settings import Settings


def test_settings_default_values():
    """デフォルト値のテスト"""
    settings = Settings()
    assert settings.OPENAI_API_KEY == ""
    assert settings.MODEL_NAME == "gpt-4o"

def test_settings_from_env():
    """環境変数からの設定値読み込みテスト"""
    test_api_key = "test-api-key"
    test_model = "gpt-3.5-turbo"
    
    os.environ["OPENAI_API_KEY"] = test_api_key
    os.environ["MODEL_NAME"] = test_model
    
    settings = Settings()
    assert settings.OPENAI_API_KEY == test_api_key
    assert settings.MODEL_NAME == test_model