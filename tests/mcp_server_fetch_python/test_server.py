from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_server_fetch_python.server import (
    get_parsed_html_string_by_playwright,
    get_raw_text,
    handle_call_tool,
    handle_list_tools,
)


@pytest.mark.asyncio
async def test_handle_list_tools():
    """利用可能なツールのリスト取得テスト"""
    tools = await handle_list_tools()
    
    assert len(tools) == 4
    tool_names = [tool.name for tool in tools]
    assert "get-raw-text" in tool_names
    assert "get-rendered-html" in tool_names
    assert "get-markdown" in tool_names
    assert "get-markdown-from-media" in tool_names

@pytest.mark.asyncio
async def test_get_raw_text():
    """get_raw_textの正常系テスト"""
    test_url = "https://example.com"
    test_content = "Test content"
    
    mock_response = AsyncMock()
    mock_response.text = test_content
    
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value.get.return_value = mock_response
    
    with patch('httpx.AsyncClient', return_value=mock_client):
        result = await get_raw_text(test_url)
        assert result == test_content

@pytest.mark.asyncio
async def test_get_parsed_html_string_by_playwright():
    """get_parsed_html_string_by_playwrightの正常系テスト"""
    test_url = "https://example.com"
    test_html = "<title>Example Domain</title>"
    
    mock_browser = AsyncMock()
    mock_page = AsyncMock()
    mock_page.content.return_value = test_html
    mock_browser.new_page.return_value = mock_page
    
    mock_playwright = AsyncMock()
    mock_playwright.__aenter__.return_value.chromium.launch.return_value = mock_browser
    
    with patch('playwright.async_api.async_playwright', return_value=mock_playwright):
        result = await get_parsed_html_string_by_playwright(test_url)
        assert test_html in result

@pytest.mark.asyncio
async def test_handle_call_tool_get_raw_text():
    """get-raw-textツールの正常系テスト"""
    test_url = "https://example.com"
    test_content = "Test content"
    
    with patch('mcp_server_fetch_python.server.get_raw_text', 
              new_callable=AsyncMock) as mock_get_raw_text:
        mock_get_raw_text.return_value = test_content
        
        result = await handle_call_tool("get-raw-text", {"url": test_url})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert result[0].text == test_content
        mock_get_raw_text.assert_called_once_with(test_url)

@pytest.mark.asyncio
async def test_handle_call_tool_get_rendered_html():
    """get-rendered-htmlツールの正常系テスト"""
    test_url = "https://example.com"
    test_html = "<html><body>Test content</body></html>"
    
    with patch('mcp_server_fetch_python.server.get_parsed_html_string_by_playwright', 
              new_callable=AsyncMock) as mock_get_html:
        mock_get_html.return_value = test_html
        
        result = await handle_call_tool("get-rendered-html", {"url": test_url})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert result[0].text == test_html
        mock_get_html.assert_called_once_with(test_url)

@pytest.mark.asyncio
async def test_handle_call_tool_invalid_tool():
    """無効なツール名のテスト"""
    result = await handle_call_tool("invalid-tool", {"url": "https://example.com"})
    assert len(result) == 1
    assert "Unknown tool" in result[0].text

@pytest.mark.asyncio
async def test_handle_call_tool_missing_arguments():
    """引数なしのテスト"""
    result = await handle_call_tool("get-raw-text", None)
    assert len(result) == 1
    assert "Missing arguments" in result[0].text

@pytest.mark.asyncio
async def test_handle_call_tool_missing_url():
    """URL引数なしのテスト"""
    result = await handle_call_tool("get-raw-text", {})
    assert len(result) == 1
    assert "Missing arguments" in result[0].text

@pytest.mark.asyncio
async def test_handle_call_tool_get_markdown():
    """get-markdownツールの正常系テスト"""
    test_url = "https://example.com"
    test_html = "<html><body><h1>Test</h1></body></html>"
    expected_markdown = "# Test"
    
    with patch('mcp_server_fetch_python.server.get_parsed_html_string_by_playwright', 
              new_callable=AsyncMock) as mock_get_html:
        mock_get_html.return_value = test_html
        
        # HtmlConverterのモック
        mock_converter_result = MagicMock()
        mock_converter_result.text_content = expected_markdown
        mock_converter = MagicMock()
        mock_converter._convert.return_value = mock_converter_result
        
        with patch('markitdown._markitdown.HtmlConverter', return_value=mock_converter):
            result = await handle_call_tool("get-markdown", {"url": test_url})
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert result[0].text == expected_markdown

