import json
from pathlib import Path

import pytest

from mcps.servers.jackett import mcp as jackett_mcp
from mcps.servers.tmdb import mcp as tmdb_mcp
from mcps.servers.transmission import mcp as transmission_mcp

SNAPSHOTS_DIR = Path(__file__).parent / "snapshots"

MCP_SERVERS = [
    ("tmdb", tmdb_mcp),
    ("transmission", transmission_mcp),
    ("jackett", jackett_mcp),
]


async def _get_tool_schemas(mcp_server):
    """Get tool schemas as dicts directly from FastMCP."""
    tools = await mcp_server.list_tools()
    return [{"name": t.name, "description": t.description, "inputSchema": t.parameters} for t in tools]


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("server_name,mcp_server", MCP_SERVERS, ids=[s[0] for s in MCP_SERVERS])
async def test_mcp_schema_snapshot(server_name, mcp_server, update_snapshots):
    tools = await _get_tool_schemas(mcp_server)
    snapshot_path = SNAPSHOTS_DIR / f"{server_name}.json"

    if update_snapshots:
        SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        snapshot_path.write_text(json.dumps(tools, indent=2) + "\n")
        pytest.skip(f"Updated {snapshot_path.name}")

    assert snapshot_path.exists(), f"No snapshot for {server_name}. Run: uv run pytest tests/test_tool_schemas.py --update-snapshots"

    expected = json.loads(snapshot_path.read_text())
    assert tools == expected, f"{server_name} schema changed! Run: uv run pytest tests/test_tool_schemas.py --update-snapshots"
