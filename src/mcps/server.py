"""MCP server apps -- one per service, each as a standalone auth-free MCP.

Auth is handled by agentgateway in front. These are internal services only.

Usage:
    uvicorn mcps.server:jackett --host 0.0.0.0 --port 8000
    uvicorn mcps.server:transmission --host 0.0.0.0 --port 8000
    uvicorn mcps.server:tmdb --host 0.0.0.0 --port 8000
    uvicorn mcps.server:storage --host 0.0.0.0 --port 8000
"""

from mcps.servers.jackett import mcp as jackett_mcp
from mcps.servers.storage import mcp as storage_mcp
from mcps.servers.tmdb import mcp as tmdb_mcp
from mcps.servers.transmission import mcp as transmission_mcp

# ASGI apps -- uvicorn targets these directly
jackett = jackett_mcp.http_app(path="/")
transmission = transmission_mcp.http_app(path="/")
tmdb = tmdb_mcp.http_app(path="/")
storage = storage_mcp.http_app(path="/")
