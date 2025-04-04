import httpx
import mcp.server.stdio
import mcp.types as types
from markitdown import MarkItDown, _markitdown
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from openai import OpenAI
from playwright.async_api import async_playwright

from mcp_server_fetch_python.settings import config

server = Server("mcp-server-fetch-python")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="get-raw-text",
            description="Extracts raw text content directly from URLs without browser rendering. Ideal for structured data formats like JSON, XML, CSV, TSV, or plain text files. Best used when fast, direct access to the source content is needed without processing dynamic elements.",  # noqa: E501
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description":"URL of the target web page (text, JSON, XML, csv, tsv, etc.)."}  # noqa: E501
                },
                "required": ["url"],
            },
        ),
         types.Tool(
            name="get-rendered-html",
            description="Fetches fully rendered HTML content using a headless browser, including JavaScript-generated content. Essential for modern web applications, single-page applications (SPAs), or any content that requires client-side rendering to be complete.",  # noqa: E501
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description":"URL of the target web page (ordinary HTML including JavaScript, etc.)."}  # noqa: E501
                },
                "required": ["url"],
            },
        ),
       types.Tool(
            name="get-markdown",
            description="Converts web page content to well-formatted Markdown, preserving structural elements like tables and definition lists. Recommended as the default tool for web content extraction when a clean, readable text format is needed while maintaining document structure.",  # noqa: E501
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description":"URL of the target web page (ordinary HTML, etc.)."}  # noqa: E501
                },
                "required": ["url"],
            },
        ),
        types.Tool(
            name="get-markdown-from-media",
            description="Performs AI-powered content extraction from media files (images and videos) and converts the results to Markdown format. Specialized tool for visual content analysis that utilizes computer vision and OCR capabilities to generate descriptive text from media sources.",  # noqa: E501
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description":"URL of the target web page (images, videos, etc.)."}  # noqa: E501
                },
                "required": ["url"],
            },
        ), 
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    
    tools can get information from a target web page, given a URL. Key features are as follows:    
    """  # noqa: E501
    
    try:
    
        if name not in ["get-raw-text","get-rendered-html", "get-markdown", "get-markdown-from-media"]:  # noqa: E501
            raise ValueError(f"Unknown tool: {name}")
        
        if not arguments:
            raise ValueError("Missing arguments")

        url = arguments.get("url", None)

        if not url:
            raise ValueError("Missing URL parameter")

        result_string = ""
        try:
            if name == "get-raw-text":
                result_string = await get_raw_text(url)
            elif name == "get-rendered-html":
                parsed_html = await get_parsed_html_string_by_playwright(url)
                result_string = str(parsed_html)
            elif name == "get-markdown":
                parsed_html = await get_parsed_html_string_by_playwright(url)
                result:_markitdown.DocumentConverterResult = _markitdown.HtmlConverter().convert_string(parsed_html)  # noqa: E501
                result_string = str(result.text_content)
            elif name == "get-markdown-from-media":
                if not config.OPENAI_API_KEY:
                    raise ValueError("OPENAI_API_KEY is not set")
                client = OpenAI(api_key=config.OPENAI_API_KEY)
                md = MarkItDown(llm_client=client, llm_model=config.MODEL_NAME)
                result_string = md.convert(url).text_content
            else:
                result_string = "Error: Unknown tool"
        except Exception as e:
            result_string = f"Error processing {name}: {str(e)}"
        
        return [
            types.TextContent(
                type="text",
                text=result_string
            )
        ]
    
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=str(e)
            )
        ]

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-server-fetch-python",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

async def get_raw_text(url:str)->str:
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text

async def get_parsed_html_string_by_playwright(url:str)->str:
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        parsed_html = await page.content()
        await browser.close()
        return parsed_html
    # with sync_playwright() as p:
    #     browser = p.chromium.launch()
    #     page = browser.new_page()
    #     page.goto(request_url)
    #     parsed_html = page.content()
    #     browser.close()
    #     return parsed_html