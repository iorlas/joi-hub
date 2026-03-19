"""Reelm MCP Gateway — OAuth 2.1 + multi-backend federation via FastMCP.

Replaces agentgateway. Handles Auth0 DCR, JWT validation, tool prefixing.
Future: output compression, rate limiting, custom orchestration tools.

Usage:
    uvicorn mcps.gateway:app --host 0.0.0.0 --port 3000
"""

import os

from fastmcp import FastMCP
from fastmcp.server import create_proxy
from fastmcp.server.auth.providers.auth0 import Auth0Provider

# Auth0 config from environment
AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN", "dev-ombhlv0g10x6js0j.us.auth0.com")
AUTH0_CLIENT_ID = os.environ.get("AUTH0_CLIENT_ID", "")
AUTH0_CLIENT_SECRET = os.environ.get("AUTH0_CLIENT_SECRET", "")
AUTH0_AUDIENCE = os.environ.get("AUTH0_AUDIENCE", "https://reelm.shen.iorlas.net")
BASE_URL = os.environ.get("BASE_URL", "https://reelm.shen.iorlas.net")

# Backend MCP server URLs (internal Docker network)
TRANSMISSION_URL = os.environ.get("TRANSMISSION_MCP_URL", "http://reelm-transmission:8000/mcp/")
JACKETT_URL = os.environ.get("JACKETT_MCP_URL", "http://reelm-jackett:8000/mcp/")
STORAGE_URL = os.environ.get("STORAGE_MCP_URL", "http://reelm-storage:8000/mcp/")

# --- Auth ---
auth = Auth0Provider(
    config_url=f"https://{AUTH0_DOMAIN}/.well-known/openid-configuration",
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    audience=AUTH0_AUDIENCE,
    base_url=BASE_URL,
    require_authorization_consent=False,
)

# --- Gateway server ---
gateway = FastMCP(
    "Reelm",
    instructions=(
        "Reelm is your personal media agent. "
        "Use reelm_torrents tools to manage downloads, "
        "reelm_search tools to find content, "
        "reelm_storage tools to manage files on the NAS."
    ),
    auth=auth,
)

# --- Mount backends with tool prefixing ---
gateway.mount(create_proxy(TRANSMISSION_URL), namespace="reelm_torrents")
gateway.mount(create_proxy(JACKETT_URL), namespace="reelm_search")
gateway.mount(create_proxy(STORAGE_URL), namespace="reelm_storage")

# --- ASGI app for uvicorn ---
app = gateway.http_app(path="/mcp")
