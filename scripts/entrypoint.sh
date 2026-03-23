#!/bin/bash
# GDP MCP Server - Container Entrypoint Script
# This file includes AI-generated code - Review and modify as needed
set -e

# Color output for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== GDP MCP Server Startup ===${NC}"

# Load configuration from TOML file if it exists
if [ -f /config/config.toml ]; then
    echo -e "${GREEN}Loading configuration from /config/config.toml...${NC}"
    python /config-loader.py /config/config.toml
else
    echo -e "${YELLOW}Warning: /config/config.toml not found, using environment variables only${NC}"
fi

# Validate required environment variables
echo -e "${GREEN}Validating required environment variables...${NC}"

MISSING_VARS=()

if [ -z "${GDP_HOST}" ]; then
    MISSING_VARS+=("GDP_HOST")
fi

if [ -z "${GDP_USERNAME}" ]; then
    MISSING_VARS+=("GDP_USERNAME")
fi

if [ -z "${GDP_PASSWORD}" ]; then
    MISSING_VARS+=("GDP_PASSWORD")
fi

if [ -z "${GDP_CLIENT_ID}" ]; then
    MISSING_VARS+=("GDP_CLIENT_ID")
fi

if [ -z "${GDP_CLIENT_SECRET}" ]; then
    MISSING_VARS+=("GDP_CLIENT_SECRET")
fi

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo -e "${RED}ERROR: Missing required environment variables:${NC}"
    for var in "${MISSING_VARS[@]}"; do
        echo -e "${RED}  - ${var}${NC}"
    done
    echo ""
    echo "Set them using:"
    echo "  - Docker: -e GDP_HOST=... -e GDP_USERNAME=... etc."
    echo "  - Docker Compose: environment section or .env file"
    echo "  - Kubernetes: Secret and ConfigMap"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ All required environment variables are set${NC}"

# Display configuration (without sensitive data)
echo -e "${GREEN}Configuration:${NC}"
echo "  GDP Host: ${GDP_HOST}"
echo "  GDP Port: ${GDP_PORT:-8443}"
echo "  GDP CLI Port: ${GDP_CLI_PORT:-2222}"
echo "  MCP Transport: ${MCP_TRANSPORT:-stdio}"
echo "  Log Level: ${LOG_LEVEL:-INFO}"

# Multi-appliance mode check
if [ -n "${GDP_APPLIANCES}" ]; then
    echo "  Multi-Appliance Mode: Enabled"
    echo "  Appliances: ${GDP_APPLIANCES}"
else
    echo "  Multi-Appliance Mode: Disabled (single appliance)"
fi

# GuardCLI check
if [ -n "${GDP_CLI_PASS}" ]; then
    echo "  GuardCLI: Enabled"
else
    echo "  GuardCLI: Disabled (GDP_CLI_PASS not set)"
fi

echo ""

# Start MCP Server based on transport mode
# Default to stdio mode (for laptop deployment with IBM Bob)
TRANSPORT="${1:-${MCP_TRANSPORT:-stdio}}"

# Ensure data directory exists for streamable-http mode (API key storage)
if [ "${TRANSPORT}" = "streamable-http" ]; then
    if [ ! -d /data ]; then
        echo -e "${YELLOW}Creating /data directory for API key storage...${NC}"
        mkdir -p /data
    fi
fi

echo -e "${GREEN}Starting GDP MCP Server (${TRANSPORT} mode)...${NC}"
echo ""

if [ "${TRANSPORT}" = "stdio" ]; then
    exec python -m src
elif [ "${TRANSPORT}" = "streamable-http" ]; then
    exec python -m src --transport streamable-http --host "${MCP_HOST:-0.0.0.0}" --port "${MCP_PORT:-8003}"
else
    # Custom command
    exec "$@"
fi

# Made with Bob
