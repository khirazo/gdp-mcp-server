# This file includes AI-generated code - Review and modify as needed
"""Localization support for GDP MCP Server prompts.

Enables natural-language invocation of MCP Prompts in multiple languages while:
- Keeping English as the canonical, always-present source
- Supporting user-extensible multilingual prompt selection
- Preserving MCP's semantic (intent-based) prompt selection
- Avoiding prompt duplication (1 intent = 1 MCP prompt)

This module targets Prompt selection, not output translation.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger("gdp_mcp")


class LocaleLoader:
    """Loads and manages locale files for prompt localization.
    
    Automatically discovers and loads all .yml files in the locales directory.
    Each locale file provides translations for prompt titles, descriptions,
    and trigger phrases to improve semantic prompt selection across languages.
    
    Example:
        loader = LocaleLoader()
        description = loader.build_multilingual_description(
            base_description="Generate a security report...",
            prompt_name="security_assessment_report"
        )
    """

    def __init__(self, locales_dir: Path | None = None):
        """Initialize the locale loader.
        
        Args:
            locales_dir: Path to locales directory. Defaults to src/locales/
        """
        if locales_dir is None:
            locales_dir = Path(__file__).parent / "locales"
        self.locales_dir = locales_dir
        self.locales: dict[str, dict[str, Any]] = {}
        self._load_all()

    def _load_all(self) -> None:
        """Auto-discover and load all .yml files in locales directory.
        
        Logs warnings for missing directory or failed file loads.
        Successfully loaded locales are stored in self.locales dict.
        """
        if not self.locales_dir.exists():
            logger.warning(f"Locales directory not found: {self.locales_dir}")
            return

        yml_files = list(self.locales_dir.glob("*.yml"))
        if not yml_files:
            logger.info(f"No locale files found in {self.locales_dir}")
            return

        for locale_file in yml_files:
            lang_code = locale_file.stem
            try:
                with open(locale_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data:
                        # Validate basic structure
                        warnings = self._validate_locale_data(lang_code, data)
                        if warnings:
                            for warning in warnings:
                                logger.warning(f"Locale {lang_code}: {warning}")
                        
                        self.locales[lang_code] = data
                        prompt_count = len(data)
                        logger.info(
                            f"Loaded locale: {lang_code} ({prompt_count} prompts)"
                        )
                    else:
                        logger.warning(f"Locale file {lang_code}.yml is empty")
            except yaml.YAMLError as e:
                logger.error(f"YAML parse error in {lang_code}.yml: {e}")
            except Exception as e:
                logger.error(f"Failed to load locale {lang_code}: {e}")

    def _validate_locale_data(
        self, lang_code: str, data: dict[str, Any]
    ) -> list[str]:
        """Validate locale file structure. Returns list of warnings.
        
        Args:
            lang_code: Language code (e.g., 'ja', 'fr')
            data: Parsed YAML data
            
        Returns:
            List of validation warning messages
        """
        warnings = []

        for prompt_name, metadata in data.items():
            if not isinstance(metadata, dict):
                warnings.append(f"{prompt_name}: metadata must be a dict")
                continue

            # Check required fields
            required_fields = ["title", "description", "trigger_phrases"]
            for field in required_fields:
                if field not in metadata:
                    warnings.append(
                        f"{prompt_name}: missing required field '{field}'"
                    )

            # Check trigger_phrases is a list
            if "trigger_phrases" in metadata:
                if not isinstance(metadata["trigger_phrases"], list):
                    warnings.append(
                        f"{prompt_name}: trigger_phrases must be a list"
                    )
                elif not metadata["trigger_phrases"]:
                    warnings.append(
                        f"{prompt_name}: trigger_phrases list is empty"
                    )

        return warnings

    def get_localized_metadata(
        self, prompt_name: str
    ) -> dict[str, dict[str, Any]]:
        """Get all localized metadata for a prompt across all languages.

        Args:
            prompt_name: Name of the MCP prompt (e.g., 'security_assessment_report')

        Returns:
            Dict mapping language codes to their metadata:
            {
                "ja": {
                    "title": "...",
                    "description": "...",
                    "trigger_phrases": [...]
                },
                "fr": {...}
            }
        """
        result = {}
        for lang_code, locale_data in self.locales.items():
            if prompt_name in locale_data:
                result[lang_code] = locale_data[prompt_name]
        return result

    def build_multilingual_description(
        self, base_description: str, prompt_name: str
    ) -> str:
        """Build a description with all available localizations appended.

        This creates a multi-language description that helps LLMs match user
        intent across languages. The format is:

            [English base description]

            [Japanese]
            [Japanese description]

            Example requests:
            - [Japanese trigger phrase 1]
            - [Japanese trigger phrase 2]

            [French]
            [French description]
            ...

        Args:
            base_description: English description (canonical)
            prompt_name: Name of the MCP prompt

        Returns:
            Multi-language description string
        """
        parts = [base_description]

        localized = self.get_localized_metadata(prompt_name)

        if not localized:
            # No localizations available, return base description only
            return base_description

        # Language display names for headers
        lang_names = {
            "ja": "Japanese",
            "fr": "French",
            "de": "German",
            "es": "Spanish",
            "zh": "Chinese",
            "ko": "Korean",
            "pt": "Portuguese",
            "it": "Italian",
            "ru": "Russian",
            "ar": "Arabic",
            "nl": "Dutch",
            "pl": "Polish",
            "tr": "Turkish",
            "vi": "Vietnamese",
            "th": "Thai",
        }

        # Sort by language code for consistent output
        for lang_code in sorted(localized.keys()):
            metadata = localized[lang_code]
            lang_name = lang_names.get(lang_code, lang_code.upper())

            parts.append(f"\n[{lang_name}]")
            parts.append(metadata.get("description", ""))

            # Include trigger phrases as examples (limit to 3 for brevity)
            trigger_phrases = metadata.get("trigger_phrases", [])
            if trigger_phrases:
                parts.append("\nExample requests:")
                for phrase in trigger_phrases[:3]:
                    parts.append(f"- {phrase}")

        return "\n".join(parts)

    def get_available_languages(self) -> list[str]:
        """Get list of available language codes.
        
        Returns:
            Sorted list of language codes (e.g., ['fr', 'ja'])
        """
        return sorted(self.locales.keys())

    def get_prompt_coverage(self) -> dict[str, int]:
        """Get translation coverage statistics.
        
        Returns:
            Dict mapping language codes to number of translated prompts
        """
        return {
            lang_code: len(locale_data)
            for lang_code, locale_data in self.locales.items()
        }


# Global instance (lazy-loaded)
_locale_loader: LocaleLoader | None = None


def get_locale_loader() -> LocaleLoader:
    """Get or create the global LocaleLoader instance.
    
    This function provides a singleton LocaleLoader that is initialized
    on first use. Subsequent calls return the same instance.
    
    Returns:
        Global LocaleLoader instance
    """
    global _locale_loader
    if _locale_loader is None:
        _locale_loader = LocaleLoader()
    return _locale_loader


def reset_locale_loader() -> None:
    """Reset the global LocaleLoader instance.
    
    Useful for testing or when locale files are modified at runtime.
    The next call to get_locale_loader() will create a fresh instance.
    """
    global _locale_loader
    _locale_loader = None

# Made with Bob
