---
description: "Always use the gdp-mcp-server to execute GDP commands and operations"
---

# GDP MCP Server Command

This slash command ensures that all GDP-related operations are executed through the **gdp-mcp-server**, providing consistent access to IBM Guardium Data Protection APIs and Guard CLI.

## Purpose

When you use `/gdp` followed by any command or request, IBM Bob will:

1. **Route to gdp-mcp-server**: All operations use the configured gdp-mcp-server
2. **Access 579+ APIs**: Full access to GDP REST API endpoints
3. **Execute Guard CLI**: System-level operations via SSH (when configured)
4. **Multi-Appliance Support**: Target specific appliances when multiple are configured

## Usage

### Basic Syntax

```
/gdp <your request or command>
```

### Examples

**List datasources:**
```
/gdp List all monitored datasources
```

**Search APIs:**
```
/gdp Search for policy-related APIs
```

**Execute specific API:**
```
/gdp Execute list_datasource API
```

**Guard CLI commands:**
```
/gdp Show system info
/gdp Check memory usage
/gdp Display network configuration
```

**Multi-appliance operations:**
```
/gdp List datasources on cm01
/gdp Show system health for cm02
```

## What It Does

The `/gdp` command acts as a **routing directive** that tells IBM Bob to:

- Use the `gdp-mcp-server` for all tool calls
- Follow the standard GDP workflow: search → details → execute
- Apply proper authentication (OAuth2 for REST API, SSH for CLI)
- Handle multi-appliance routing when appliance names are specified

## MCP Tools Available

When you use `/gdp`, Bob has access to these tools:

1. **gdp_search_apis** - Search for API endpoints by keyword
2. **gdp_list_categories** - Browse API categories
3. **gdp_get_api_details** - Get parameter details for an API
4. **gdp_execute_api** - Execute a GDP REST API
5. **gdp_guard_cli** - Execute Guard CLI commands over SSH

## Workflow Example

```
User: /gdp List all security policies

Bob internally executes:
  1. gdp_search_apis("policy")
  2. gdp_get_api_details("list_policy")
  3. gdp_execute_api("list_policy")
  4. Formats and presents results
```

## Technical Details

- **MCP Server**: gdp-mcp-server
- **Transport**: stdio (local process communication)
- **Authentication**: OAuth2 (REST API), SSH (Guard CLI)
- **Endpoints**: 579+ REST APIs across 36 categories
- **CLI Access**: Full Guard CLI command set (when configured)

## Notes

- This command is a **routing directive**, not a tool itself
- All actual operations are performed by the gdp-mcp-server
- For structured report generation, use `/gdp-report` instead
- Guard CLI commands require `GDP_CLI_PASS` to be configured

---

**Made with Bob**