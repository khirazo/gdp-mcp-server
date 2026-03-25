# GDP MCP Server - Locale Files

This directory contains localization files for GDP MCP Server prompts.

## Quick Start

Each `.yml` file in this directory provides translations for MCP prompt templates in a specific language. The server automatically discovers and loads all locale files on startup.

## Bundled Languages

- **`ja.yml`** - Japanese (日本語)
- **`fr.yml`** - French (Français)

## Adding a New Language

1. Create a new file: `<language_code>.yml` (e.g., `de.yml` for German)
2. Follow the schema from existing files
3. Restart the server - your language is automatically loaded!

## File Format

```yaml
# Top-level keys must match prompt names in src/prompts.py
security_assessment_report:
  title: "Your Language Title"
  description: >
    Detailed description of what this prompt does.
    Can span multiple lines.
  trigger_phrases:
    - Natural language example 1
    - Natural language example 2
    - Natural language example 3
```

### Required Fields

- **`title`**: Short display name
- **`description`**: Detailed explanation
- **`trigger_phrases`**: List of natural-language examples (3-5 recommended)

## Available Prompts

All 8 prompts support localization:

1. `security_assessment_report`
2. `compliance_summary_report`
3. `datasource_inventory_report`
4. `activity_monitoring_report`
5. `system_health_report`
6. `vulnerability_assessment_report`
7. `stap_status_report`
8. `policy_violations_report`

## Language Codes

Use ISO 639-1 two-letter codes:

| Language | Code | Example File |
|----------|------|--------------|
| Japanese | ja | `ja.yml` |
| French | fr | `fr.yml` |
| German | de | `de.yml` |
| Spanish | es | `es.yml` |
| Chinese | zh | `zh.yml` |
| Korean | ko | `ko.yml` |
| Portuguese | pt | `pt.yml` |
| Italian | it | `it.yml` |
| Russian | ru | `ru.yml` |
| Arabic | ar | `ar.yml` |

## Documentation

For detailed documentation, see:
- **User Guide**: [`docs/LOCALIZATION.md`](../../docs/LOCALIZATION.md)
