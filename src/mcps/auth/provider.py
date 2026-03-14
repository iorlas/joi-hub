"""OAuth 2.1 provider with username/password login for MCP servers.

Subclasses FastMCP's InMemoryOAuthProvider, adding:
- bcrypt password verification
- HTML login page flow (authorize -> login -> redirect with code)
"""

import re
import secrets
from html import escape
from pathlib import Path

import bcrypt
from mcp.server.auth.provider import (
    AuthorizationParams,
)
from mcp.shared.auth import OAuthClientInformationFull
from pydantic import AnyHttpUrl
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.routing import Route

from fastmcp.server.auth.providers.in_memory import InMemoryOAuthProvider

_LOGIN_TEMPLATE = (Path(__file__).parent / "login.html").read_text()


class McpsOAuthProvider(InMemoryOAuthProvider):
    """OAuth provider with bcrypt credential validation and login page."""

    def __init__(
        self,
        *,
        base_url: AnyHttpUrl | str,
        users: dict[str, str],  # {username: bcrypt_hash}
        required_scopes: list[str] | None = None,
    ):
        super().__init__(
            base_url=base_url,
            required_scopes=required_scopes,
        )
        self._users = users
        # Pending auth sessions: session_id -> (client, params)
        self._pending_auth: dict[str, tuple[OAuthClientInformationFull, AuthorizationParams]] = {}

    def verify_credentials(self, username: str, password: str) -> bool:
        """Check username/password against bcrypt hashes."""
        stored_hash = self._users.get(username)
        if stored_hash is None:
            return False
        return bcrypt.checkpw(password.encode(), stored_hash.encode())

    async def authorize(
        self, client: OAuthClientInformationFull, params: AuthorizationParams
    ) -> str:
        """Redirect to login page instead of auto-approving."""
        session_id = secrets.token_urlsafe(32)
        self._pending_auth[session_id] = (client, params)
        return f"/login?session_id={session_id}"

    def _render_login(self, session_id: str, error: str = "") -> str:
        """Render login template with HTML-escaped string replacement."""
        html = _LOGIN_TEMPLATE
        html = html.replace("{{ session_id }}", escape(session_id))
        html = html.replace("{{ error }}", escape(error))
        if error:
            html = html.replace("{% if error %}", "").replace("{% endif %}", "")
        else:
            # Remove the error block
            html = re.sub(r"\{% if error %\}.*?\{% endif %\}", "", html, flags=re.DOTALL)
        return html

    async def _handle_login_get(self, request: Request) -> HTMLResponse:
        """Show login form."""
        session_id = request.query_params.get("session_id", "")
        return HTMLResponse(self._render_login(session_id))

    async def _handle_login_post(self, request: Request) -> RedirectResponse | HTMLResponse:
        """Validate credentials and issue auth code."""
        form = await request.form()
        session_id = str(form.get("session_id", ""))
        username = str(form.get("username", ""))
        password = str(form.get("password", ""))

        if session_id not in self._pending_auth:
            return HTMLResponse(self._render_login(session_id, error="Session expired. Please try again."))

        if not self.verify_credentials(username, password):
            return HTMLResponse(self._render_login(session_id, error="Invalid username or password."))

        # Credentials valid -- issue auth code using parent's logic
        client, params = self._pending_auth.pop(session_id)
        redirect_uri = await super().authorize(client, params)
        return RedirectResponse(url=redirect_uri, status_code=302)

    def get_routes(self, mcp_path: str | None = None) -> list[Route]:
        """Add login routes to the standard OAuth routes."""
        routes = super().get_routes(mcp_path)
        routes.extend([
            Route("/login", endpoint=self._handle_login_get, methods=["GET"]),
            Route("/login", endpoint=self._handle_login_post, methods=["POST"]),
        ])
        return routes
