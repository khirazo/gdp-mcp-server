"""GDP MCP Server — exposes IBM Guardium Data Protection APIs as MCP tools.

Targets MCP spec 2025-11-25:
  - Streamable HTTP transport (POST /mcp) — replaces SSE
  - stdio transport for local/IDE integration
  - API key authentication via admin-managed key store
  - Lifespan API — no global state; tools access deps via ctx
  - Multi-appliance support — manage multiple GDP appliances from one server
"""

import argparse
import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field

from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from . import keystore
from .auth import GDPAuth
from .cli import GDPCLIClient
from .client import GDPClient
from .config import GDPConfig, load_appliance_names
from .discovery import GDPDiscovery
from .prompts import register_prompts
from .completions import register_completions
from .resources import register_resources
from .tools import register_tools

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
)
logger = logging.getLogger("gdp_mcp")


# ── Per-appliance context ───────────────────────────────────────

@dataclass
class ApplianceContext:
    """Runtime deps for a single GDP appliance."""
    name: str
    config: GDPConfig
    auth: GDPAuth
    client: GDPClient
    discovery: GDPDiscovery
    cli_client: GDPCLIClient | None


@dataclass
class AppContext:
    """Top-level lifespan context holding all appliances."""
    appliances: dict[str, ApplianceContext] = field(default_factory=dict)
    default_name: str = "default"

    def get(self, name: str | None = None) -> ApplianceContext:
        """Resolve an appliance by name. Returns default when name is None."""
        key = (name or self.default_name).lower()
        if key not in self.appliances:
            available = ", ".join(sorted(self.appliances))
            raise KeyError(
                f"Appliance '{key}' not found. Available: {available}"
            )
        return self.appliances[key]

    @property
    def names(self) -> list[str]:
        return sorted(self.appliances)

    @property
    def is_multi(self) -> bool:
        return len(self.appliances) > 1


def _build_appliance(name: str, config: GDPConfig) -> ApplianceContext:
    """Create an ApplianceContext from a config."""
    auth = GDPAuth(config)
    client = GDPClient(config, auth)
    discovery = GDPDiscovery(client)
    cli_client = GDPCLIClient(config) if config.cli_pass else None
    return ApplianceContext(
        name=name,
        config=config,
        auth=auth,
        client=client,
        discovery=discovery,
        cli_client=cli_client,
    )


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Initialize GDP appliance(s) at startup, tear down on shutdown."""
    app = AppContext()
    appliance_names = load_appliance_names()

    if appliance_names:
        # Multi-appliance mode
        app.default_name = appliance_names[0]
        for name in appliance_names:
            prefix = f"GDP_{name.upper()}"
            config = GDPConfig.from_prefix(prefix)
            ctx = _build_appliance(name, config)
            app.appliances[name] = ctx
            logger.info(
                "Appliance '%s': %s:%s (CLI: %s)",
                name, config.host, config.port,
                "enabled" if ctx.cli_client else "disabled",
            )
        logger.info(
            "GDP MCP Server v2.0.0 — %d appliances, default: %s",
            len(app.appliances), app.default_name,
        )
    else:
        # Single-appliance mode (backward compatible)
        config = GDPConfig()
        ctx = _build_appliance("default", config)
        app.appliances["default"] = ctx
        app.default_name = "default"
        logger.info(
            "GDP MCP Server v2.0.0 — target: %s:%s (CLI: %s)",
            config.host, config.port,
            "enabled" if ctx.cli_client else "disabled",
        )

    yield app
    logger.info("GDP MCP Server shutting down")


# ── FastMCP instance ───────────────────────────────────────────

mcp = FastMCP(
    "GDP MCP Server",
    instructions=(
        "AI interface to IBM Guardium Data Protection. "
        "Provides access to all GDP REST API endpoints for querying, "
        "configuring, and managing GDP appliances. "
        "Workflow: gdp_search_apis → gdp_get_api_details → gdp_execute_api. "
        "For system-level operations, use gdp_guard_cli (Guard CLI over SSH). "
        "When multiple appliances are configured, pass the 'appliance' parameter "
        "to target a specific one (omit to use the default)."
    ),
    stateless_http=True,
    streamable_http_path="/mcp",
    lifespan=app_lifespan,
)

# Register tool definitions (no runtime objects needed — tools pull deps from ctx)
register_tools(mcp)

# Register report template prompts for standardized output
register_prompts(mcp)

# Register completion handler for auto-complete suggestions
register_completions(mcp)

# Register GDP resources for client resource panels
register_resources(mcp)


# ── API Key Middleware ──────────────────────────────────────────


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Validates API key from the key store in Authorization header.

    Every request must include: Authorization: Bearer <key>
    The /health, /admin/*, and /mcp endpoints are handled separately.
    """

    async def dispatch(self, request, call_next):
        # Always allow health checks without auth
        if request.url.path == "/health":
            return await call_next(request)

        # Admin endpoints use localhost check, not API key
        if request.url.path.startswith("/admin"):
            return await call_next(request)

        # Validate API key against key store
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.removeprefix("Bearer ").strip()

        key_info = keystore.validate_key(token)
        if key_info is None:
            logger.warning(
                "Unauthorized request from %s to %s",
                request.client.host if request.client else "unknown",
                request.url.path,
            )
            return JSONResponse(
                {"error": "Unauthorized", "message": "Invalid or missing API key"},
                status_code=401,
            )

        return await call_next(request)


# ── Streamable HTTP App with Auth + Admin ───────────────────────


def _create_http_app(host: str = "0.0.0.0", port: int = 8003) -> Starlette:
    """Create a Starlette app wrapping FastMCP's Streamable HTTP transport.

    FastMCP.streamable_http_app() produces a Starlette app that registers
    the MCP endpoint at /mcp internally. We mount it at "/" so the final
    path stays /mcp, and add health + admin routes alongside it.
    """
    # FastMCP builds its own Streamable HTTP ASGI app with /mcp route inside
    mcp_http_app = mcp.streamable_http_app()

    async def health(request):
        names = load_appliance_names()
        if names:
            targets = {
                n: f"{GDPConfig.from_prefix(f'GDP_{n.upper()}').host}:"
                   f"{GDPConfig.from_prefix(f'GDP_{n.upper()}').port}"
                for n in names
            }
        else:
            cfg = GDPConfig()
            targets = {"default": f"{cfg.host}:{cfg.port}"}
        return JSONResponse({
            "status": "ok",
            "server": "GDP MCP Server",
            "version": "2.0.0",
            "protocol": "2025-11-25",
            "transport": "streamable-http",
            "endpoint": "/mcp",
            "auth_required": True,
            "active_keys": len(keystore.list_keys()),
            "appliances": targets,
        })

    # ── Admin endpoints (localhost only) ────────────────────────

    _ADMIN_ALLOWED_IPS = {"127.0.0.1", "::1", "localhost", "172.17.0.1"}

    def _is_localhost(request) -> bool:
        client_host = request.client.host if request.client else None
        return client_host in _ADMIN_ALLOWED_IPS

    async def admin_create_key(request):
        if not _is_localhost(request):
            return JSONResponse(
                {"error": "Forbidden", "message": "Admin endpoints are localhost only"},
                status_code=403,
            )
        try:
            body = await request.json()
            user = body.get("user", "").strip()
        except Exception:
            user = ""
        if not user:
            return JSONResponse(
                {"error": "Bad Request", "message": "'user' field is required"},
                status_code=400,
            )
        result = keystore.generate_key(user)
        return JSONResponse(result, status_code=201)

    async def admin_list_keys(request):
        if not _is_localhost(request):
            return JSONResponse(
                {"error": "Forbidden", "message": "Admin endpoints are localhost only"},
                status_code=403,
            )
        return JSONResponse(keystore.list_keys())

    async def admin_revoke_key(request):
        if not _is_localhost(request):
            return JSONResponse(
                {"error": "Forbidden", "message": "Admin endpoints are localhost only"},
                status_code=403,
            )
        key_prefix = request.path_params["key_prefix"]
        result = keystore.revoke_key(key_prefix)
        if result is None:
            return JSONResponse(
                {"error": "Not Found", "message": f"No key with prefix '{key_prefix}'"},
                status_code=404,
            )
        return JSONResponse(result)

    # ── Wire it all together ────────────────────────────────────

    middleware = [Middleware(APIKeyMiddleware)]
    logger.info("API key authentication enforced for Streamable HTTP connections")
    logger.info("Key store: %s", keystore.KEY_STORE_PATH)
    logger.info("Active keys: %d", len(keystore.list_keys()))

    return Starlette(
        debug=False,
        routes=[
            Route("/health", health),
            Route("/admin/keys", admin_create_key, methods=["POST"]),
            Route("/admin/keys", admin_list_keys, methods=["GET"]),
            Route("/admin/keys/{key_prefix}", admin_revoke_key, methods=["DELETE"]),
            # Mount the FastMCP streamable HTTP app at root — it owns /mcp (must be last)
            Mount("/", app=mcp_http_app),
        ],
        middleware=middleware,
    )


# ── Entry point ─────────────────────────────────────────────────


def main() -> None:
    """Start the GDP MCP Server (stdio or streamable-http transport)."""
    parser = argparse.ArgumentParser(description="GDP MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default=os.getenv("MCP_TRANSPORT", "stdio").lower(),
        help="Transport mode: stdio (default) or streamable-http",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("MCP_HOST", "0.0.0.0"),
        help="Host to bind HTTP server (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("MCP_PORT", "8003")),
        help="Port for HTTP server (default: 8003)",
    )
    args = parser.parse_args()

    cfg = GDPConfig()
    logger.info(
        "GDP MCP Server v2.0.0 starting — target: %s:%s (transport: %s)",
        cfg.host,
        cfg.port,
        args.transport,
    )

    if args.transport == "streamable-http":
        import uvicorn

        logger.info("Streamable HTTP on %s:%d", args.host, args.port)
        logger.info("MCP endpoint: http://%s:%d/mcp", args.host, args.port)
        starlette_app = _create_http_app(args.host, args.port)
        uvicorn.run(starlette_app, host=args.host, port=args.port)
    else:
        logger.info("stdio mode — no API key auth (direct process communication)")
        mcp.run(transport="stdio")
