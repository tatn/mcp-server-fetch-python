# mcp-server-fetch-python

An MCP server for fetching and transforming web content into various formats. This server provides comprehensive tools for extracting content from web pages, including support for JavaScript-rendered content and media files.

<a href="https://glama.ai/mcp/servers/8d0zm2o56d"><img width="380" height="200" src="https://glama.ai/mcp/servers/8d0zm2o56d/badge" alt="Server Fetch Python MCP server" /></a>

## Features

### Tools

The server provides four specialized tools:

- **get-raw-text**: Extracts raw text content directly from URLs without browser rendering
  - Arguments:
    - `url`: URL of the target web page (text, JSON, XML, csv, tsv, etc.) (required)
  - Best used for structured data formats or when fast, direct access is needed

- **get-rendered-html**: Fetches fully rendered HTML content using a headless browser
  - Arguments:
    - `url`: URL of the target web page (required)
  - Essential for modern web applications and SPAs that require JavaScript rendering

- **get-markdown**: Converts web page content to well-formatted Markdown
  - Arguments:
    - `url`: URL of the target web page (required)
  - Preserves structural elements while providing clean, readable text output

- **get-markdown-from-media**: Performs AI-powered content extraction from media files
  - Arguments:
    - `url`: URL of the target media file (images, videos) (required)
  - Utilizes computer vision and OCR for visual content analysis
  - Requires a valid OPENAI_API_KEY to be set in environment variables
  - Will return an error message if the API key is not set or if there are issues processing the media file

## Usage

### Claude Desktop

To use with Claude Desktop, add the server configuration:

On MacOS:  `~/Library/Application\ Support/Claude/claude_desktop_config.json`  
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

```json
"mcpServers": {
  "mcp-server-fetch-python": {
    "command": "uvx",
    "args": [
      "mcp-server-fetch-python"
    ]
  }
}
```


## Environment Variables

The following environment variables can be configured:

- **OPENAI_API_KEY**: Required for using the `get-markdown-from-media` tool. This key is needed for AI-powered image analysis and content extraction.
- **PYTHONIOENCODING**: Set to "utf-8" if you encounter character encoding issues in the output.
- **MODEL_NAME**: Specifies the model name to use. Defaults to "gpt-4o".

```json
"mcpServers": {
  "mcp-server-fetch-python": {
    "command": "uvx",
    "args": [
      "mcp-server-fetch-python"
    ],
    "env": {
        "OPENAI_API_KEY": "sk-****",
        "PYTHONIOENCODING": "utf-8",
        "MODEL_NAME": "gpt-4o",        
    }
  }
}
```


### Local Installation

Alternatively, you can install and run the server locally:

```powershell
git clone https://github.com/tatn/mcp-server-fetch-python.git
cd mcp-server-fetch-python
uv sync
uv build
```

Then add the following configuration to Claude Desktop config file:

```json
"mcpServers": {
  "mcp-server-fetch-python": {
    "command": "uv",
    "args": [
      "--directory",
      "path\\to\\mcp-server-fetch-python",  # Replace with actual path to the cloned repository
      "run",
      "mcp-server-fetch-python"
    ]
  }
}
```

## Development

### Debugging

You can start the MCP Inspector using [npx](https://docs.npmjs.com/cli/v11/commands/npx)with the following commands:


```bash
npx @modelcontextprotocol/inspector uvx mcp-server-fetch-python
```

```bash
npx @modelcontextprotocol/inspector uv --directory path\\to\\mcp-server-fetch-python run mcp-server-fetch-python
```
