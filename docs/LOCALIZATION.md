# GDP MCP Server - Localization Guide

## Overview

GDP MCP Server supports **multi-language prompt selection** to enable natural-language invocation in any language. Users can ask for reports in Japanese, French, or any other language, and the AI will correctly match their intent to the appropriate prompt.

**Key Features:**
- ✅ English as canonical source (always present)
- ✅ User-extensible - add languages without code changes
- ✅ Semantic prompt selection across all languages
- ✅ No prompt duplication (1 intent = 1 MCP prompt)
- ✅ Automatic discovery of locale files

## Quick Start

### Using Existing Languages

The server comes with Japanese (`ja.yml`) and French (`fr.yml`) translations. Simply start the server:

```bash
gdp-mcp-server
```

You'll see in the logs:
```
INFO gdp_mcp — Prompt localization enabled for: fr, ja
INFO gdp_mcp — Registered 8 report template prompts
```

Now you can ask in any supported language:

**English:**
> "Generate a security assessment report for the GDP appliance"

**Japanese:**
> "GDPアプライアンスのセキュリティ評価レポートを生成してください"

**French:**
> "Générer un rapport d'évaluation de sécurité pour GDP"

All three requests will trigger the same `security_assessment_report` prompt.

### Adding a New Language

1. **Create a locale file** in `src/locales/` with the ISO 639-1 language code:
   ```bash
   touch src/locales/de.yml  # German
   ```

2. **Follow the schema** (see below for details):
   ```yaml
   security_assessment_report:
     title: "Sicherheitsbewertungsbericht"
     description: >
       Erstellen Sie einen umfassenden Sicherheitsbewertungsbericht für eine GDP-Appliance.
     trigger_phrases:
       - Erstellen Sie einen Sicherheitsbewertungsbericht
       - GDP-Sicherheitslage bewerten
   ```

3. **Restart the server** - the new language is automatically loaded:
   ```
   INFO gdp_mcp — Prompt localization enabled for: de, fr, ja
   ```

That's it! No code changes required.

## Locale File Format

### File Naming Convention

- **Format:** `<ISO_639-1_code>.yml`
- **Location:** `src/locales/`
- **Examples:** `ja.yml`, `fr.yml`, `de.yml`, `zh.yml`, `es.yml`

### Schema

Each locale file is a YAML document where:
- **Top-level keys** must match MCP prompt names in `src/prompts.py`
- Each prompt has three required fields: `title`, `description`, `trigger_phrases`

```yaml
# Example: src/locales/ja.yml
security_assessment_report:
  title: "セキュリティ評価レポート"
  description: >
    GDPアプライアンスのセキュリティ状況を包括的に評価するレポートを生成します。
    データソース、ポリシー、違反、システム健全性、推奨事項を含みます。
  trigger_phrases:
    - GDPアプライアンスのセキュリティ評価レポートを生成してください
    - GDPのセキュリティ状況を評価したい
    - Guardiumのセキュリティ評価を実施してください

compliance_summary_report:
  title: "コンプライアンスサマリーレポート"
  description: >
    ポリシーステータス、違反トレンド、GDP環境全体のコンプライアンス状況を示すレポートを生成します。
  trigger_phrases:
    - コンプライアンスサマリーレポートを作成してください
    - ポリシー違反の状況を確認したい
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Short, user-facing name for the prompt (used in UI) |
| `description` | string | Yes | Detailed explanation of what the prompt does (helps LLM match intent) |
| `trigger_phrases` | list[string] | Yes | Natural-language examples that should trigger this prompt (3-5 recommended) |

### Validation

The server performs basic validation on startup:
- Checks for required fields (`title`, `description`, `trigger_phrases`)
- Warns if `trigger_phrases` is not a list or is empty
- Logs warnings for malformed entries (but continues loading valid ones)

Example warning:
```
WARNING gdp_mcp — Locale ja: security_assessment_report: missing required field 'title'
```

## Available Prompts

All 8 GDP report templates support localization:

| Prompt Name | English Title | Purpose |
|-------------|---------------|---------|
| `security_assessment_report` | Security Assessment Report | Comprehensive security evaluation |
| `compliance_summary_report` | Compliance Summary Report | Policy status and compliance posture |
| `datasource_inventory_report` | Datasource Inventory Report | List of monitored datasources |
| `activity_monitoring_report` | Activity Monitoring Report | Database activity patterns and anomalies |
| `system_health_report` | System Health Report | System diagnostics (CPU, memory, disk) |
| `vulnerability_assessment_report` | Vulnerability Assessment Report | VA scan results and remediation |
| `stap_status_report` | S-TAP Status Report | Inspection engine status |
| `policy_violations_report` | Policy Violations Report | Violation details and trends |

## How It Works

### Architecture

```
src/
 ├─ prompts.py           # Canonical English prompts
 ├─ localization.py      # Locale loader + helpers
 └─ locales/
      ├─ ja.yml          # Japanese (bundled)
      ├─ fr.yml          # French (bundled)
      └─ *.yml           # User-added languages
```

### Prompt Registration Flow

1. **Startup:** `localization.py` scans `src/locales/` directory
2. **Discovery:** All `*.yml` files are loaded into memory
3. **Validation:** Basic schema checks with warnings for issues
4. **Registration:** Each prompt calls `build_multilingual_description()`
5. **Augmentation:** English + all translations are combined
6. **MCP Registration:** The augmented description is registered with FastMCP

### Prompt Selection Flow

1. **User Request:** User asks in any language
2. **LLM Processing:** AI reads all prompt descriptions (English + Japanese + French + ...)
3. **Semantic Matching:** AI matches user intent to the most relevant prompt
4. **Execution:** The single canonical prompt is executed

### Multi-Language Description Format

When a prompt has translations, the description becomes:

```
Generate a comprehensive Security Assessment Report for a GDP appliance.
Covers datasources, policies, violations, system health, and recommendations.

[Japanese]
GDPアプライアンスのセキュリティ状況を包括的に評価するレポートを生成します。
データソース、ポリシー、違反、システム健全性、推奨事項を含みます。

Example requests:
- GDPアプライアンスのセキュリティ評価レポートを生成してください
- GDPのセキュリティ状況を評価したい
- Guardiumのセキュリティ評価を実施してください

[French]
Générer un rapport d'évaluation de sécurité complet pour une appliance GDP.
Couvre les sources de données, les politiques, les violations, la santé du système et les recommandations.

Example requests:
- Générer un rapport d'évaluation de sécurité pour GDP
- Évaluer la posture de sécurité de Guardium
```

This format:
- Preserves English as the canonical source
- Provides semantic hints for all languages
- Includes example trigger phrases to improve matching
- Requires no language-specific routing logic

## Best Practices

### Writing Good Translations

1. **Be Natural:** Use phrases people would actually say
   - ✅ "GDPのセキュリティ状況を評価したい"
   - ❌ "セキュリティアセスメントレポートジェネレーション"

2. **Include Variations:** Add synonyms and paraphrases
   ```yaml
   trigger_phrases:
     - セキュリティ評価レポートを生成してください  # Formal
     - セキュリティレポートが必要です              # Casual
     - Guardiumのセキュリティ評価を実施して       # Alternative phrasing
   ```

3. **Keep Descriptions Concise:** Focus on what the prompt does, not how
   - ✅ "GDPアプライアンスのセキュリティ状況を包括的に評価するレポート"
   - ❌ "このプロンプトはGDPツールを呼び出してデータを収集し..."

4. **Match the English Intent:** Don't add or remove functionality
   - Translate the purpose, not the implementation details

### Trigger Phrases Guidelines

- **Quantity:** 3-5 phrases per prompt (more is better for coverage)
- **Diversity:** Include formal, casual, and technical variations
- **Specificity:** Be specific enough to avoid ambiguity
- **Context:** Include domain terms (GDP, Guardium, datasource, etc.)

### Testing Your Translations

1. **Start the server** and check logs for warnings
2. **Ask in your language** via Claude Desktop or VS Code
3. **Verify prompt selection** - check which prompt was triggered
4. **Iterate** - add more trigger phrases if matching is weak

## Troubleshooting

### Locale File Not Loading

**Symptom:** No log message about your language

**Causes:**
- File not in `src/locales/` directory
- File extension is not `.yml`
- YAML syntax error

**Solution:**
```bash
# Check file location
ls src/locales/

# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('src/locales/de.yml'))"
```

### Prompt Not Matching

**Symptom:** AI doesn't select the right prompt for your language

**Causes:**
- Trigger phrases too generic or too specific
- Missing key domain terms
- Not enough variation in phrases

**Solution:**
- Add more trigger phrases with different phrasings
- Include domain-specific terms (GDP, Guardium, datasource, etc.)
- Test with different user requests

### Validation Warnings

**Symptom:** Warnings in logs like "missing required field 'title'"

**Causes:**
- Typo in field name
- Missing required field
- Incorrect YAML structure

**Solution:**
- Check field names: `title`, `description`, `trigger_phrases`
- Ensure all three fields are present for each prompt
- Validate YAML indentation (use 2 spaces)

## Advanced Usage

### Programmatic Access

```python
from src.localization import get_locale_loader

loader = get_locale_loader()

# Get available languages
languages = loader.get_available_languages()
print(languages)  # ['fr', 'ja']

# Get translation coverage
coverage = loader.get_prompt_coverage()
print(coverage)  # {'fr': 8, 'ja': 8}

# Get localized metadata for a prompt
metadata = loader.get_localized_metadata("security_assessment_report")
print(metadata['ja']['title'])  # "セキュリティ評価レポート"
```

### Resetting the Loader

Useful for testing or hot-reloading locale files:

```python
from src.localization import reset_locale_loader, get_locale_loader

# Reset and reload
reset_locale_loader()
loader = get_locale_loader()  # Fresh instance with reloaded files
```

## Language Support Matrix

| Language | Code | Status | Prompts Translated |
|----------|------|--------|-------------------|
| English | en | ✅ Built-in | 8/8 (canonical) |
| Japanese | ja | ✅ Bundled | 8/8 |
| French | fr | ✅ Bundled | 8/8 |
| German | de | ⚪ User-added | - |
| Spanish | es | ⚪ User-added | - |
| Chinese | zh | ⚪ User-added | - |
| Korean | ko | ⚪ User-added | - |

**Legend:**
- ✅ Built-in: Always available
- ✅ Bundled: Included in distribution
- ⚪ User-added: Can be added by users

## Future Enhancements

Potential extensions (not yet implemented):

- **Output Language Switching:** Request reports in specific languages
- **Locale-Aware UI Labels:** Show localized titles in Claude's prompt picker
- **Validation CLI:** `gdp-mcp-server validate-locales` command
- **Coverage Report:** Show which prompts have translations per language
- **Environment Variable Override:** `GDP_LOCALE=ja` to prefer specific language

## References

- **Design Brief:** [`work/MCP_Prompt_Localization_Design_Brief_COPILOT.md`](../work/MCP_Prompt_Localization_Design_Brief_COPILOT.md)
- **Implementation:** [`src/localization.py`](../src/localization.py)
- **Prompts:** [`src/prompts.py`](../src/prompts.py)
- **Example Locales:** [`src/locales/ja.yml`](../src/locales/ja.yml), [`src/locales/fr.yml`](../src/locales/fr.yml)

## Contributing Translations

We welcome translations for additional languages! To contribute:

1. Fork the repository
2. Create a new locale file in `src/locales/`
3. Translate all 8 prompts following the schema
4. Test with the server
5. Submit a pull request

**Translation Checklist:**
- [ ] File named correctly (`<lang_code>.yml`)
- [ ] All 8 prompts translated
- [ ] Each prompt has `title`, `description`, `trigger_phrases`
- [ ] At least 3 trigger phrases per prompt
- [ ] Tested with the server
- [ ] No YAML syntax errors
- [ ] Natural, idiomatic language

Thank you for helping make GDP MCP Server accessible to more users worldwide! 🌍