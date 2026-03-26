---
description: "Interactive GDP report generator with 8 professional report templates. Always uses gdp-mcp-server."
---

# GDP Report Generator

Interactive menu-driven interface to generate 8 types of professional GDP reports using the gdp-mcp-server.

## Quick Start

```
/gdp-report
```

Bob will present a numbered menu of 8 report types. Select by number or name, provide parameters interactively, and receive a professionally formatted report.

## Report Types

### 1. 🔒 Security Assessment Report
**Comprehensive security evaluation**

- **Parameters**: `appliance` (optional), `time_period` (optional, default: "last 30 days")
- **Includes**: Datasources, policies, violations, system health, recommendations
- **Use when**: You need a complete security overview

### 2. 📋 Compliance Summary Report
**Policy status and compliance posture**

- **Parameters**: `appliance` (optional), `framework` (optional, default: "general")
- **Frameworks**: general, SOX, GDPR, HIPAA, PCI-DSS, ISO27001
- **Includes**: Compliance score, policy coverage, monitoring coverage, gaps, remediation
- **Use when**: Preparing for audits or compliance reviews

### 3. 🗄️ Datasource Inventory Report
**List of all monitored datasources**

- **Parameters**: `appliance` (optional)
- **Includes**: Datasource details table, grouping by type, connectivity issues
- **Use when**: You need a complete inventory of monitored databases

### 4. 📊 Activity Monitoring Report
**Database activity patterns and anomalies**

- **Parameters**: `appliance` (optional), `time_period` (optional, default: "last 7 days")
- **Includes**: Activity volume, top users, activity by datasource, anomalies
- **Use when**: Investigating unusual activity or usage patterns

### 5. 🏥 System Health Report
**System diagnostics and resource utilization**

- **Parameters**: `appliance` (optional)
- **Includes**: System overview, CPU/memory/disk metrics, network config, processes, S-TAPs
- **Use when**: Checking appliance health or troubleshooting performance

### 6. 🛡️ Vulnerability Assessment Report
**VA scan results and remediation guidance**

- **Parameters**: `appliance` (optional)
- **Includes**: Findings by severity, findings by datasource, remediation priority, VA coverage
- **Use when**: Reviewing security vulnerabilities in monitored databases

### 7. 📡 S-TAP Status Report
**Inspection engine status and connectivity**

- **Parameters**: `appliance` (optional)
- **Includes**: S-TAP inventory, connectivity status, version compliance
- **Use when**: Verifying inspection engine health and coverage

### 8. ⚠️ Policy Violations Report
**Violation details, trends, and affected users**

- **Parameters**: `appliance` (optional), `time_period` (optional, default: "last 30 days")
- **Includes**: Violations by policy/severity/user/datasource, recent violations, remediation
- **Use when**: Investigating policy violations or security incidents

## Usage Examples

### Interactive Menu (Recommended)

```
/gdp-report
```

Bob presents the menu, you select a report, provide parameters interactively.

### Direct Invocation

**By number:**
```
/gdp-report 1
/gdp-report 5 cm01
```

**By name:**
```
/gdp-report security
/gdp-report compliance cm02 SOX
/gdp-report datasource
```

**With all parameters:**
```
/gdp-report security cm01 "last 7 days"
/gdp-report activity cm02 "last 30 days"
/gdp-report compliance cm01 GDPR
```

## Parameters

### `appliance` (optional)
Target appliance name. Omit to use the default appliance.

**Examples**: `cm01`, `cm02`, `collector01`

### `time_period` (optional)
Time period for time-based reports (1, 4, 8).

**Default**: `"last 30 days"`

**Examples**:
- `"last 7 days"`
- `"last 30 days"`
- `"last 90 days"`
- `"2024-01-01 to 2024-03-31"`

### `framework` (optional)
Compliance framework for compliance report (2).

**Default**: `"general"`

**Values**: `general`, `SOX`, `GDPR`, `HIPAA`, `PCI-DSS`, `ISO27001`

## Multilingual Support

The command supports both English and Japanese interactions. Bob will detect your language and respond accordingly.

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
     [Displays formatted report]
```

### Japanese Example

```
User: /gdp-report

Bob: 📊 GDPレポート生成
     [日本語でメニュー表示]

User: セキュリティ評価レポート

Bob: 🔒 セキュリティ評価レポート
     パラメータ:
     - アプライアンス: [デフォルト] または名前を指定
     - 期間: [過去30日] または期間を指定
     
     デフォルト設定で実行しますか？

User: はい

Bob: セキュリティ評価レポートを生成中...
     [フォーマットされたレポートを表示]
```

## How It Works

1. **User invokes**: `/gdp-report` or `/gdp-report <type> [params]`
2. **Menu presentation**: Bob shows 8 report types (if no type specified)
3. **Parameter collection**: Bob asks for required parameters interactively
4. **Data gathering**: Bob uses gdp-mcp-server tools to collect data:
   - `gdp_search_apis` - Find relevant API endpoints
   - `gdp_execute_api` - Execute GDP REST APIs
   - `gdp_guard_cli` - Execute Guard CLI commands (for system health)
5. **Report generation**: Bob follows the specific workflow for each report type
6. **Formatted output**: Professional markdown with tables and sections

## Report Workflows

Each report type follows a specific workflow to ensure consistency and completeness:

### Security Assessment Report Workflow
1. Call `gdp_search_apis("datasource")` → `gdp_execute_api("list_datasource")`
2. Call `gdp_search_apis("policy")` → list all policies
3. Call `gdp_search_apis("violation")` → list violations
4. Call `gdp_guard_cli("show system info")`
5. Call `gdp_guard_cli("diag system memory")`
6. Call `gdp_guard_cli("diag system disk")`
7. Format as: Executive Summary, Datasources table, Policies table, Violations by severity, System Health metrics, Recommendations

### Compliance Summary Report Workflow
1. Call `gdp_search_apis("policy")` → list all policies
2. Call `gdp_execute_api("list_datasource")`
3. Call `gdp_search_apis("violation")` → list violations
4. Format as: Compliance Score, Policy Coverage table, Monitoring Coverage, Violations by Category, Compliance Gaps, Remediation Recommendations

### System Health Report Workflow
1. Call `gdp_guard_cli("show system info")`
2. Call `gdp_guard_cli("diag system memory")`
3. Call `gdp_guard_cli("diag system disk")`
4. Call `gdp_guard_cli("show network interface all")`
5. Call `gdp_guard_cli("show system processes")`
6. Call `gdp_search_apis("stap")` → list S-TAPs
7. Format as: System Overview, Resource Utilization (Memory/Disk tables), Network Configuration, Running Processes, S-TAPs, Health Summary, Recommendations

*(Other report workflows follow similar patterns - see full documentation for details)*

## Report Quality Standards

All reports follow these standards:

- ✅ **Real Data Only**: Never fabricate values - use actual GDP data
- ✅ **Professional Format**: Markdown with tables, sections, and proper structure
- ✅ **Consistent Layout**: Same format every time for the same report type
- ✅ **Complete Sections**: All sections specified in the template
- ✅ **Visual Indicators**: Emojis for severity (🔴 Critical, 🟠 High, 🟡 Medium, 🟢 Low)
- ✅ **Resource Warnings**: Flag utilization above 80% with ⚠️
- ✅ **Error Handling**: State "Data unavailable — [reason]" if tool calls fail
- ✅ **Report Footer**: "This report was generated automatically by the GDP MCP Server"

## Comparison with /gdp Command

| Feature | `/gdp` | `/gdp-report` |
|---------|--------|---------------|
| **Purpose** | General GDP operations | Structured report generation |
| **Output** | Varies by request | Professional formatted reports |
| **Structure** | Flexible | Fixed templates (8 types) |
| **Use Case** | Ad-hoc queries | Regular reporting, audits |
| **Consistency** | Varies | Guaranteed consistent format |

**When to use `/gdp`**: Ad-hoc queries, exploration, one-off operations

**When to use `/gdp-report`**: Regular reporting, audits, documentation, consistent output

## Troubleshooting

### Command Not Recognized

**Problem**: `/gdp-report` returns "Unknown command"

**Solution**:
1. Verify the command file exists in `~/.bob/commands/gdp-report.md`
2. Restart IBM Bob
3. Check Bob's command loading logs

### Report Generation Fails

**Problem**: Report generation fails or returns errors

**Solution**:
1. Check GDP appliance connectivity
2. Verify credentials in `.env` file
3. Check gdp-mcp-server logs for errors
4. Ensure the appliance name is correct (if specified)
5. For system health reports, verify `GDP_CLI_PASS` is configured

### Incomplete Data

**Problem**: Report shows "Data unavailable" for some sections

**Solution**:
1. Check GDP appliance permissions for the authenticated user
2. Verify the specific API or CLI command is supported on your GDP version
3. Check gdp-mcp-server logs for specific error messages
4. Some features may require specific GDP licenses or configurations

### Japanese Menu Not Showing

**Problem**: Menu always displays in English

**Solution**:
1. Ensure Bob's language detection is enabled
2. Try explicitly using Japanese in your request
3. Check Bob's localization settings

## Related Commands

- `/gdp` - General GDP operations and ad-hoc queries

## Technical Details

- **MCP Server**: gdp-mcp-server
- **Transport**: stdio (local process communication)
- **Authentication**: OAuth2 (REST API), SSH (Guard CLI)
- **API Coverage**: 579+ REST API endpoints across 36 categories

## Future: MCP Prompts

When IBM Bob adds MCP Prompt support:

- Both `/gdp-report` and natural language prompts will coexist
- Same report templates ensure identical output
- Users can choose their preferred invocation method
- No changes needed to existing `/gdp-report` command

## Examples Gallery

### Example 1: Quick Security Check
```
/gdp-report 1
```
Generates Security Assessment Report with defaults (default appliance, last 30 days).

### Example 2: SOX Compliance Audit
```
/gdp-report compliance cm01 SOX
```
Generates Compliance Summary Report for appliance `cm01` focused on SOX compliance.

### Example 3: Weekly Activity Review
```
/gdp-report activity cm02 "last 7 days"
```
Generates Activity Monitoring Report for appliance `cm02` covering the last 7 days.

### Example 4: System Health Check
```
/gdp-report system_health
```
Generates System Health Report for the default appliance.

### Example 5: Vulnerability Scan Results
```
/gdp-report vulnerability cm01
```
Generates Vulnerability Assessment Report for appliance `cm01`.

## Support

For issues or questions, consult IBM Bob documentation or the GDP MCP Server documentation.

---

**Made with Bob**