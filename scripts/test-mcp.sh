#!/bin/bash
# MCP Server Test Script for GDP MCP Server
# Tests stdio mode by sending JSON-RPC requests in sequence to a single container instance

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== GDP MCP Server Test Script ===${NC}"
echo ""
echo -e "${YELLOW}Testing MCP protocol with sequential requests in a single session${NC}"
echo ""

# Create a temporary file for requests
REQUESTS_FILE=$(mktemp)

# Write all requests to the file (one per line)
# Updated to MCP 2025-11-25 protocol version
cat > "$REQUESTS_FILE" << 'EOF'
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"test-client","version":"1.0.0"}}}
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
{"jsonrpc":"2.0","id":3,"method":"prompts/list","params":{}}
{"jsonrpc":"2.0","id":4,"method":"resources/list","params":{}}
{"jsonrpc":"2.0","id":5,"method":"completion/complete","params":{"ref":{"type":"ref/prompt","name":"security_assessment_report"},"argument":{"name":"appliance","value":""}}}
EOF

echo -e "${GREEN}Sending requests:${NC}"
echo -e "${BLUE}1. initialize (MCP 2025-11-25)${NC}"
echo -e "${BLUE}2. tools/list${NC}"
echo -e "${BLUE}3. prompts/list${NC}"
echo -e "${BLUE}4. resources/list${NC}"
echo -e "${BLUE}5. completion/complete (test completions)${NC}"
echo ""

echo -e "${YELLOW}Starting GDP MCP server and sending requests...${NC}"
echo ""

# Send all requests to the server and capture output
OUTPUT=$(cat "$REQUESTS_FILE" | docker compose run --rm -T gdp-mcp-server 2>&1)

# Clean up temp file
rm "$REQUESTS_FILE"

# Extract JSON responses (lines starting with {)
RESPONSES=$(echo "$OUTPUT" | grep -E '^\{')

# Parse and display each response
echo -e "${GREEN}=== Test Results ===${NC}"
echo ""

# Response 1: Initialize
echo -e "${BLUE}Test 1: Initialize${NC}"
INIT_RESPONSE=$(echo "$RESPONSES" | sed -n '1p')
if echo "$INIT_RESPONSE" | jq -e '.result' > /dev/null 2>&1; then
    echo "$INIT_RESPONSE" | jq '{protocolVersion: .result.protocolVersion, serverInfo: .result.serverInfo, capabilities: .result.capabilities}'
else
    echo "$INIT_RESPONSE" | jq '.'
fi
echo ""

# Response 2: Tools List
echo -e "${BLUE}Test 2: List Tools${NC}"
TOOLS_RESPONSE=$(echo "$RESPONSES" | sed -n '2p')
if echo "$TOOLS_RESPONSE" | jq -e '.result.tools' > /dev/null 2>&1; then
    echo "$TOOLS_RESPONSE" | jq '.result.tools[] | {name: .name, description: .description}'
else
    echo "$TOOLS_RESPONSE" | jq '.'
fi
echo ""

# Response 3: Prompts List
echo -e "${BLUE}Test 3: List Prompts${NC}"
PROMPTS_RESPONSE=$(echo "$RESPONSES" | sed -n '3p')
if echo "$PROMPTS_RESPONSE" | jq -e '.result.prompts' > /dev/null 2>&1; then
    echo "$PROMPTS_RESPONSE" | jq '.result.prompts[] | {name: .name, description: .description}'
else
    echo "$PROMPTS_RESPONSE" | jq '.'
fi
echo ""

# Response 4: Resources List
echo -e "${BLUE}Test 4: List Resources${NC}"
RESOURCES_RESPONSE=$(echo "$RESPONSES" | sed -n '4p')
if echo "$RESOURCES_RESPONSE" | jq -e '.result.resources' > /dev/null 2>&1; then
    echo "$RESOURCES_RESPONSE" | jq '.result.resources[] | {uri: .uri, name: .name, description: .description}'
else
    echo "$RESOURCES_RESPONSE" | jq '.'
fi
echo ""

# Response 5: Completions
echo -e "${BLUE}Test 5: Completions${NC}"
COMPLETIONS_RESPONSE=$(echo "$RESPONSES" | sed -n '5p')
if echo "$COMPLETIONS_RESPONSE" | jq -e '.result' > /dev/null 2>&1; then
    echo "$COMPLETIONS_RESPONSE" | jq '.'
else
    echo "$COMPLETIONS_RESPONSE" | jq '.'
fi
echo ""

echo -e "${GREEN}=== All tests completed ===${NC}"
echo ""
echo -e "${BLUE}Summary:${NC}"
echo "- Initialize: $(echo "$RESPONSES" | sed -n '1p' | jq -r 'if .result then "✓ Success" else "✗ Failed" end')"
echo "- Tools List: $(echo "$RESPONSES" | sed -n '2p' | jq -r 'if .result.tools then "✓ Success (" + (.result.tools | length | tostring) + " tools)" else "✗ Failed" end')"
echo "- Prompts List: $(echo "$RESPONSES" | sed -n '3p' | jq -r 'if .result.prompts then "✓ Success (" + (.result.prompts | length | tostring) + " prompts)" else "✗ Failed" end')"
echo "- Resources List: $(echo "$RESPONSES" | sed -n '4p' | jq -r 'if .result.resources then "✓ Success (" + (.result.resources | length | tostring) + " resources)" else "✗ Failed" end')"
echo "- Completions: $(echo "$RESPONSES" | sed -n '5p' | jq -r 'if .result then "✓ Success" else "✗ Failed" end')"
echo ""
echo -e "${YELLOW}Note: GDP MCP Server uses MCP protocol 2025-11-25 with FastMCP${NC}"

# Made with Bob
