"""Guard CLI client — execute GDP CLI commands over SSH."""

import asyncio
import logging
import re

import paramiko

from .config import GDPConfig

logger = logging.getLogger("gdp_mcp.cli")

# Commands that modify system state — blocked unless confirm_destructive=True
_DESTRUCTIVE_PATTERNS = re.compile(
    r"\b(restart|reboot|shutdown|delete|remove|drop|restore|"
    r"reset|purge|truncate|kill|stop|disable|decommission|"
    r"uninstall|format|wipe)\b",
    re.IGNORECASE,
)


class GDPCLIClient:
    """SSH client for the Guard CLI (cli@host:2222)."""

    def __init__(self, config: GDPConfig) -> None:
        self._config = config
        self._available: bool | None = None

    @property
    def configured(self) -> bool:
        return bool(self._config.cli_pass)

    async def execute(
        self,
        command: str,
        confirm_destructive: bool = False,
        timeout: int = 30,
    ) -> str:
        """Execute a Guard CLI command over SSH.

        Args:
            command: The CLI command (e.g. "show system info").
            confirm_destructive: Must be True for destructive commands.
            timeout: SSH command timeout in seconds.

        Returns:
            Command output as a string.
        """
        if not self.configured:
            return (
                "Guard CLI is not configured. Set GDP_CLI_PASS in your environment. "
                "Optional: GDP_CLI_HOST (defaults to GDP_HOST), "
                "GDP_CLI_PORT (defaults to 2222), GDP_CLI_USER (defaults to cli)."
            )

        command = command.strip()
        if not command:
            return "No command provided."

        if _DESTRUCTIVE_PATTERNS.search(command) and not confirm_destructive:
            return (
                f"⚠️ BLOCKED: '{command}' appears destructive.\n"
                f"This command may modify system state. "
                f"To proceed, call gdp_guard_cli with confirm_destructive=True.\n"
                f"Ask the user for confirmation first."
            )

        return await asyncio.to_thread(
            self._ssh_exec, command, timeout
        )

    def _ssh_exec(self, command: str, timeout: int) -> str:
        """Run a command over SSH (blocking — called via asyncio.to_thread)."""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        host = self._config.cli_host
        port = self._config.cli_port
        user = self._config.cli_user
        password = self._config.cli_pass

        try:
            logger.info("SSH %s@%s:%d — %s", user, host, port, command)
            client.connect(
                hostname=host,
                port=port,
                username=user,
                password=password,
                timeout=10,
                look_for_keys=False,
                allow_agent=False,
            )

            _, stdout, stderr = client.exec_command(command, timeout=timeout)
            out = stdout.read().decode("utf-8", errors="replace").strip()
            err = stderr.read().decode("utf-8", errors="replace").strip()

            if err and not out:
                return f"CLI error:\n{err}"
            if err:
                return f"{out}\n\n--- stderr ---\n{err}"
            return out or "(no output)"

        except paramiko.AuthenticationException:
            return (
                f"SSH authentication failed for {user}@{host}:{port}. "
                f"Check GDP_CLI_USER and GDP_CLI_PASS."
            )
        except paramiko.SSHException as e:
            return f"SSH error connecting to {host}:{port}: {e}"
        except OSError as e:
            return f"Cannot reach {host}:{port}: {e}"
        finally:
            client.close()
