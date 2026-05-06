# Weclapp MCP Server

Weclapp is a cloud-based ERP and CRM platform designed for small and medium-sized enterprises.
This Model Context Protocol (MCP) server provides an AI-powered connector for Weclapp with the following capabilities.

## MCP Capabilities

- Manage parties: companies and individuals

## Setup the Server

### Prerequisites

Before you begin, make sure you have:
- Python 3.10+ installed
- Weclapp tenant name
  - when logged in, you can find it in the URL: `https://<tenant>.weclapp.com`
- Weclapp API token
  - Log in and click your profile in the top-right corner
  - Go to **My Settings**
  - Scroll to the **API Token** section 
  - Enter your password to unlock it 
  - Click **Add new API token** to generate one.

### Launch the Server

Replace `WECLAPP_TENANT` and `WECLAPP_TOKEN` with your actual values:

```shell
pip install -r requirements.txt
WECLAPP_TENANT=phuryoqpaxjvihl WECLAPP_TOKEN=4a6c6090-ed4b-4be4-bd09-1446600fd6ee python3 server.py
```

## Add MCP Capabilities

Any MCP-compatible AI client that supports HTTPS transport and MCP protocol can connect.
Refer to the client's documentation for instructions on adding an MCP server.

**Stdio mode:**
```
"webclapp": {
  "command": "python",
  "args": ["/absolute/path/to/server.py"],
  "env": {
    "WECLAPP_TENANT": "phuryoqpaxjvihl",
    "WECLAPP_TOKEN": "4a6c6090-ed4b-4be4-bd09-1446600fd6ee",
    "TRANSPORT": "stdio"
  }
}
```

**HTTP mode:**
```
"webclapp": {
  "url": "http://localhost:8000/mcp"
}
```

## Need support?

This Weclapp MCP Server is community-maintained. Fixes and improvements are driven by contributors - so you're encouraged to explore, debug, and extend it yourself. If you run into issues, feel free to open an issue or contribute a fix.

If you need dedicated support, you tell us what's broken, slow or embarrassing on [https://codelev.com](https://codelev.com) directly. In just 3 steps our AI agent will help you create a briefing for the contact - no preparation, no discovery phase and no calls needed.

## License

This project is licensed under the Server Side Public License (SSPL) v1.0 - see the [LICENSE](LICENSE) file for details.
