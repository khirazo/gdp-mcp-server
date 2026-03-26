# IBM Bob Slash Commands for GDP MCP Server

This directory contains slash command configurations for IBM Bob to provide access to GDP operations and professional report generation.

## Overview

IBM Bob uses **Markdown-based slash commands** (`.md` files) to define custom commands. This directory provides two commands for working with the GDP MCP Server:

1. **`/gdp`** - General GDP operations (routing directive)
2. **`/gdp-report`** - Interactive report generator (8 professional templates)

## Available Commands

### `/gdp` - GDP Operations Router

**File**: `gdp.md`

**Purpose**: Ensures all GDP operations are routed through the gdp-mcp-server.

**Usage**:
```
/gdp <your request or command>
```

**Examples**:
```
/gdp List all monitored datasources
/gdp Search for policy-related APIs
/gdp Show system info
/gdp Check memory usage on cm01
```

**See**: `gdp.md` for full documentation

### `/gdp-report` - Interactive Report Generator

**File**: `gdp-report.md`

**Purpose**: Generate professional GDP reports using interactive menus or direct invocation.

**Usage**:
```
/gdp-report [type] [appliance] [parameters]
```

**Examples**:
```
/gdp-report                          # Interactive menu
/gdp-report 1                        # Security Assessment Report
/gdp-report security cm01 "last 7 days"
/gdp-report compliance cm02 SOX
```

**See**: `gdp-report.md` for full documentation

## Usage

### Basic Usage (Interactive Menu)

```
/gdp-report
```

Bob will present a numbered menu of 8 report types. Select by number or name.

### Direct Invocation (Skip Menu)

```
/gdp-report <type> [appliance] [parameters]
```

**Examples:**

```bash
# Security Assessment Report with defaults
/gdp-report 1

# Security Assessment Report for specific appliance and time period
/gdp-report security cm01 "last 7 days"

# Compliance Report with SOX framework
/gdp-report 2 cm02 SOX

# Datasource Inventory Report
/gdp-report datasource

# System Health Report for specific appliance
/gdp-report 5 cm01
```

## Report Types

| # | Name | Parameters | Description |
|---|------|------------|-------------|
| 1 | `security_assessment` | appliance, time_period | Comprehensive security evaluation |
| 2 | `compliance_summary` | appliance, framework | Policy status and compliance posture |
| 3 | `datasource_inventory` | appliance | List of monitored datasources |
| 4 | `activity_monitoring` | appliance, time_period | Database activity patterns |
| 5 | `system_health` | appliance | System diagnostics |
| 6 | `vulnerability_assessment` | appliance | VA scan results |
| 7 | `stap_status` | appliance | Inspection engine status |
| 8 | `policy_violations` | appliance, time_period | Violation details and trends |

## Parameters

### `appliance` (optional)
Target appliance name. Omit to use the default appliance.

**Examples:** `cm01`, `cm02`, `collector01`

### `time_period` (optional, default: "last 30 days")
Time period for time-based reports (1, 4, 8).

**Examples:**
- `"last 7 days"`
- `"last 30 days"`
- `"last 90 days"`
- `"2024-01-01 to 2024-03-31"`

### `framework` (optional, default: "general")
Compliance framework for compliance report (2).

**Values:** `general`, `SOX`, `GDPR`, `HIPAA`, `PCI-DSS`, `ISO27001`

## Multilingual Support

The command supports both English and Japanese interactions:

### English Example

```
User: /gdp-report

Bob: 📊 GDP Report Generator
     [Shows menu with 8 options]

User: 1

Bob: 🔒 Security Assessment Report
     Parameters:
     - Appliance: [default] or specify name
     - Time Period: [last 30 days] or specify range
     
     Use defaults?

User: Yes

Bob: Generating Security Assessment Report...
```

### Japanese Example

```
User: /gdp-report

Bob: 📊 GDPレポート生成
     [Shows menu in Japanese]

User: セキュリティ評価レポート

Bob: 🔒 セキュリティ評価レポート
     パラメータ:
     - アプライアンス: [デフォルト] または名前を指定
     - 期間: [過去30日] または期間を指定
     
     デフォルト設定で実行しますか？

User: はい

Bob: セキュリティ評価レポートを生成中...
```

## Installation

### For IBM Bob Users

1. **Copy the command files** to your Bob configuration directory:
   ```bash
   cp bob-commands/gdp.md ~/.bob/commands/
   cp bob-commands/gdp-report.md ~/.bob/commands/
   ```

2. **Restart IBM Bob** to load the new commands

3. **Verify installation**:
   - Type `/` in Bob to see the list of available commands
   - `gdp` and `gdp-report` should appear in the list

### For IBM Bob Administrators

If you manage Bob for multiple users, place the command files in the shared commands directory:

```bash
cp bob-commands/gdp.md /opt/ibm-bob/commands/
cp bob-commands/gdp-report.md /opt/ibm-bob/commands/
```

## How It Works

1. **User invokes command**: `/gdp-report`
2. **Bob presents menu**: 8 report types with descriptions
3. **User selects report**: By number (1-8) or name
4. **Bob collects parameters**: Interactively asks for required parameters
5. **Bob generates report**: Uses gdp-mcp-server tools to gather data
6. **Bob displays report**: Formatted markdown with tables and sections

## Technical Details

### MCP Server Integration

The command uses the `gdp-mcp-server` to execute all GDP operations:

- **Tools Used:**
  - `gdp_search_apis` - Search for relevant API endpoints
  - `gdp_execute_api` - Execute GDP REST APIs
  - `gdp_guard_cli` - Execute Guard CLI commands (for system health)

- **Workflow:**
  Each report type follows a specific workflow defined in the command configuration. For example, Security Assessment Report:
  1. Search and list datasources
  2. Search and list policies
  3. Search and list violations
  4. Get system info via CLI
  5. Get memory diagnostics via CLI
  6. Get disk diagnostics via CLI
  7. Format results into professional report

### Report Templates

The command uses the same report templates as MCP Prompts (defined in `src/prompts.py`), ensuring consistency regardless of invocation method.

## Troubleshooting

### Command Not Found

**Problem:** `/gdp-report` returns "Unknown command"

**Solution:**
1. Verify the command file is in the correct directory
2. Restart IBM Bob
3. Check Bob's command loading logs

### MCP Server Not Connected

**Problem:** "Cannot connect to gdp-mcp-server"

**Solution:**
1. Verify gdp-mcp-server is running
2. Check Bob's MCP server configuration
3. Ensure the server name matches: `gdp-mcp-server`

### Report Generation Fails

**Problem:** Report generation fails or returns errors

**Solution:**
1. Check GDP appliance connectivity
2. Verify credentials in `.env` file
3. Check gdp-mcp-server logs for errors
4. Ensure the appliance name is correct (if specified)

### Japanese Menu Not Showing

**Problem:** Menu always displays in English

**Solution:**
1. Ensure Bob's language detection is enabled
2. Try explicitly using Japanese in your request
3. Check Bob's localization settings

## Comparison: Slash Command vs MCP Prompts

| Feature | Slash Command | MCP Prompts |
|---------|--------------|-------------|
| **Availability** | ✅ Now | ⏳ Future (when Bob adds support) |
| **Invocation** | Explicit `/gdp-report` | Natural language |
| **Parameters** | Interactive or direct | Natural language |
| **Discoverability** | `/` command | Prompt picker UI |
| **Flexibility** | Structured | Conversational |
| **Consistency** | ✅ Same templates | ✅ Same templates |

## Future Migration

When IBM Bob adds MCP Prompt support:

1. **Both methods will coexist** - Users can choose their preferred workflow
2. **No changes needed** - Slash command continues to work
3. **Same output** - Both use identical report templates
4. **User preference** - Some prefer explicit commands, others prefer natural language

## Examples Gallery

### Example 1: Quick Security Check

```
/gdp-report 1
```

Generates a Security Assessment Report with default settings (default appliance, last 30 days).

### Example 2: Compliance Audit for SOX

```
/gdp-report compliance cm01 SOX
```

Generates a Compliance Summary Report for appliance `cm01` focused on SOX compliance.

### Example 3: Weekly Activity Review

```
/gdp-report activity cm02 "last 7 days"
```

Generates an Activity Monitoring Report for appliance `cm02` covering the last 7 days.

### Example 4: System Health Check

```
/gdp-report system_health
```

Generates a System Health Report for the default appliance.

## Support

For issues or questions:

1. **GDP MCP Server Issues**: Check `README.md` and `docs/LOCALIZATION.md`
2. **IBM Bob Issues**: Consult IBM Bob documentation

## Related Documentation

- **Localization Guide**: [`docs/LOCALIZATION.md`](../docs/LOCALIZATION.md)
- **MCP Server README**: [`README.md`](../README.md)
- **Report Templates**: [`src/prompts.py`](../src/prompts.py)

## File Structure

```
bob-commands/
├── gdp.md              # /gdp command (routing directive)
├── gdp-report.md       # /gdp-report command (report generator)
└── README.md           # This file
```

---

**Note:** This slash command is a workaround for IBM Bob's current lack of MCP Prompt support. It provides the same functionality and output quality as MCP Prompts, just with a different invocation method.