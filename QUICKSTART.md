# Quick Start - Laptop Deployment with IBM Bob

This guide helps you set up GDP MCP Server on your laptop for use with IBM Bob MCP client via stdio connection.

## 📋 Prerequisites

- **Docker Desktop** (or Docker Engine + Docker Compose)
- **IBM Bob** MCP client installed
- **GDP credentials** (username, password, OAuth client ID/secret)
- **Git** (for cloning the repository)

## 🚀 Setup (3 Steps)

### Step 1: Clone and Configure

```bash
# Clone the repository
git clone https://github.ibm.com/khirazo/gdp-mcp-server.git
cd gdp-mcp-server

# Copy environment template
cp .env.example .env

# Edit .env with your GDP credentials
# Use your preferred text editor (nano, vim, notepad, etc.)
nano .env
```

**Required values in `.env`:**
```bash
GDP_HOST=your-gdp-appliance.example.com
GDP_USERNAME=admin
GDP_PASSWORD=your-password
GDP_CLIENT_ID=your-oauth-client-id
GDP_CLIENT_SECRET=your-oauth-client-secret
```

**Optional: Enable GuardCLI (for system operations):**
```bash
GDP_CLI_PASS=your-cli-password
```

**Optional: Edit `config/config.toml`** for non-sensitive settings (ports, log level, etc.)

### Step 2: Build Container

```bash
# Build the Docker image
docker compose build

# Verify the build
docker images | grep gdp-mcp-server
```

Expected output:
```
gdp-mcp-server:stdio    6b6a8287594b        229MB             0B
```

### Step 3: Configure IBM Bob

Add the GDP MCP server to IBM Bob's configuration file.

**Location of Bob's config file:**

- **Windows**: `%USERPROFILE%\.bob\settings\mcp_settings.json`
- **macOS**: `~/.bob/settings/mcp_settings.json`
- **Linux**: `~/.bob/settings/mcp_settings.json`

**Configuration examples by platform:**

#### Option 1: Docker Desktop (Windows/macOS/Linux)

```json
{
  "mcpServers": {
    "gdp-mcp-server": {
      "command": "docker",
      "args": [
        "compose",
        "run",
        "--rm",
        "gdp-mcp-server"
      ],
      "cwd": "/absolute/path/to/gdp-mcp-server",
      "env": {}
    }
  }
}
```

**Example paths:**
- **Windows**: `C:\\Users\\YourName\\Projects\\gdp-mcp-server`
- **macOS**: `/Users/yourname/projects/gdp-mcp-server`
- **Linux**: `/home/yourname/projects/gdp-mcp-server`

#### Option 2: WSL2 Docker (Windows with WSL2)

If you're using Docker installed in WSL2 (not Docker Desktop), use this configuration:

```json
{
  "mcpServers": {
    "gdp-mcp-server": {
      "command": "wsl",
      "args": [
        "-d",
        "Ubuntu",
        "bash",
        "-c",
        "cd /path/to/gdp-mcp-server && docker compose run --rm gdp-mcp-server"
      ],
      "env": {}
    }
  }
}
```

**Important notes for WSL2:**
- Replace `Ubuntu` with your WSL distribution name (check with `wsl -l -v`)
- Use **Linux-style path** in WSL: `/home/yourname/projects/gdp-mcp-server`
- If repository is on Windows filesystem, use: `/mnt/c/Users/YourName/Projects/gdp-mcp-server`

**To find your WSL distribution name:**
```powershell
# Run in PowerShell or Command Prompt
wsl -l -v
```

Example output:
```
  NAME      STATE           VERSION
* Ubuntu    Running         2
```

**Performance tip:** For better performance with WSL2, clone the repository inside WSL filesystem (`/home/yourname/`) rather than Windows filesystem (`/mnt/c/`).

## ✅ Verification

### Test the Container

```bash
# Test that the container starts correctly
docker compose run --rm gdp-mcp-server

# You should see startup logs like:
=== GDP MCP Server Startup ===
Loading configuration from /config/config.toml...
Configuration loaded from /config/config.toml
  MCP_HOST=0.0.0.0
  MCP_PORT=8003
  LOGGING_LEVEL=INFO
  SECURITY_KEY_STORE_PATH=/data/keys.json
Configuration exported to environment variables
Validating required environment variables...
✓ All required environment variables are set
Configuration:
  GDP Host: 10.18.13.14
  GDP Port: 8443
  GDP CLI Port: 2222
  MCP Transport: stdio
  Log Level: INFO
  Multi-Appliance Mode: Disabled (single appliance)
  GuardCLI: Disabled (GDP_CLI_PASS not set)

Starting GDP MCP Server (stdio mode)...
```

Press `Ctrl+C` to stop the test.

### Test MCP Protocol (Optional)

Test the MCP server's JSON-RPC interface using the provided test scripts:

**Option 1: Automated Test (Recommended)**

```bash
# Run automated tests
bash scripts/test-mcp.sh

# This will test:
# - Initialize connection (MCP 2025-11-25)
# - List tools (5 tools)
# - List prompts (8 report templates)
# - List resources (4 resources)
# - Completions (auto-complete functionality)
```

**Option 2: Manual Test (Interactive)**

Start the container and paste JSON-RPC requests directly into the prompt:

```bash
# Start the MCP server
docker compose run --rm gdp-mcp-server
```

Then paste these requests one by one (press Enter after each):

**1. Initialize the session:**
```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}
```

**2. List available tools:**
```json
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
```

**3. List available prompts:**
```json
{"jsonrpc":"2.0","id":3,"method":"prompts/list","params":{}}
```

**4. List available resources:**
```json
{"jsonrpc":"2.0","id":4,"method":"resources/list","params":{}}
```

**Expected responses:**
- Initialize: Returns server info and capabilities
- Tools list: Returns 5 tools (gdp_search_apis, gdp_list_categories, gdp_get_api_details, gdp_execute_api, gdp_guard_cli)
- Prompts list: Returns 8 report templates
- Resources list: Returns 4 resources (appliances, categories, endpoints, server info)

Press `Ctrl+C` to exit when done.

**Note for Windows users:**
- Use Git Bash or WSL to run the test scripts
- PowerShell may have issues with JSON formatting

### Test with IBM Bob

1. **Restart IBM Bob** (or reload the VS Code window)
2. **Open Bob's chat interface**
3. **Try a GDP command**, for example:
   ```
   List all available GDP API categories
   ```

Bob should now be able to use the GDP MCP tools:
- `gdp_search_apis` - Search the API catalog
- `gdp_list_categories` - List all API categories
- `gdp_get_api_details` - Get parameter schema for an endpoint
- `gdp_execute_api` - Execute any GDP REST API
- `gdp_guard_cli` - Execute Guard CLI commands (if GDP_CLI_PASS is set)

## 🔧 Troubleshooting

### Container won't start

**Check logs:**
```bash
docker compose run --rm gdp-mcp-server
```

**Common issues:**
1. **Missing credentials**: Verify `.env` file has all required values
2. **Invalid credentials**: Check username/password/client ID/secret
3. **Network issues**: Ensure you can reach the GDP appliance from your laptop
4. **OAuth client not registered**: Run `grdapi register_oauth_client` on GDP appliance CLI

### IBM Bob can't connect

**Verify configuration:**
1. Check that `cwd` path in Bob's config is correct (absolute path)
2. Ensure Docker is running
3. Restart VS Code after changing Bob's configuration

**Test Docker Compose manually:**
```bash
cd /path/to/gdp-mcp-server
docker compose run --rm gdp-mcp-server
```

### Permission errors

**On Linux/macOS:**
```bash
# Ensure scripts are executable
chmod +x scripts/*.sh scripts/*.py
```

**Docker permission issues:**
```bash
# Add your user to docker group (Linux)
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect
```

### WSL2-specific issues

**"docker: command not found" in WSL:**
```bash
# Install Docker in WSL2 (if not using Docker Desktop)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER

# Start Docker service
sudo service docker start
```

**Path conversion issues:**
```bash
# If you see "no such file or directory" errors:
# 1. Verify the path exists in WSL
cd /mnt/c/Users/YourName/Projects/gdp-mcp-server  # Windows path
# OR
cd /home/yourname/projects/gdp-mcp-server  # WSL path

# 2. Check if docker compose works
docker compose run --rm gdp-mcp-server
```

**Line ending issues (CRLF vs LF):**
```bash
# If you see "bad interpreter" or syntax errors:
# Convert line endings to Unix format
sudo apt-get install dos2unix
find . -type f -name "*.sh" -exec dos2unix {} \;
find . -type f -name "*.py" -exec dos2unix {} \;
```

### GuardCLI not available

**If you see "GuardCLI: Disabled" in startup logs:**
- Set `GDP_CLI_PASS` in your `.env` file
- Rebuild the container: `docker compose build`
- Restart the container

**SSH connection issues:**
- Verify `GDP_CLI_HOST` and `GDP_CLI_PORT` (default: 2222)
- Test SSH manually: `ssh cli@your-gdp-appliance.example.com -p 2222`

### Multi-appliance setup

**To manage multiple GDP appliances:**

1. Set `GDP_APPLIANCES` in `.env`:
   ```bash
   GDP_APPLIANCES=cm01,cm02,collector01
   ```

2. Configure each appliance with prefixed variables:
   ```bash
   GDP_CM01_HOST=cm01.example.com
   GDP_CM01_CLIENT_ID=cm01_client
   GDP_CM01_CLIENT_SECRET=cm01_secret
   
   GDP_CM02_HOST=cm02.example.com
   GDP_CM02_CLIENT_ID=cm02_client
   GDP_CM02_CLIENT_SECRET=cm02_secret
   ```

3. Shared credentials (optional):
   ```bash
   # These apply to all appliances unless overridden
   GDP_USERNAME=admin
   GDP_PASSWORD=shared_password
   ```

## 📚 Next Steps

- **[README.md](README.md)** - Full documentation and architecture
- **[SETUP_PROCEDURES.md](SETUP_PROCEDURES.md)** - Detailed setup instructions
- **Report Templates** - Use built-in prompts for standardized reports

## 💡 Tips

### Update to Latest Version

```bash
# Pull latest changes
git pull origin main

# Rebuild container
docker compose build

# Restart IBM Bob
```

### View Logs

```bash
# Run with logs visible
docker compose run --rm gdp-mcp-server

# Or check logs from a running container
docker compose logs -f gdp-mcp-server
```

### Change Log Level

Edit `.env` file:
```bash
LOG_LEVEL=DEBUG  # For detailed logs
LOG_LEVEL=INFO   # Default
LOG_LEVEL=ERROR  # Minimal logs
```

Then rebuild:
```bash
docker compose build
```

---

**Ready to use GDP with IBM Bob!** 🎉