"""
gmgn_client.py — gmgn-cli subprocess 封装

对应设计文件中所有 GMGN 命令映射。
通过 subprocess 调用 gmgn-cli，返回解析后的 JSON。
"""

from __future__ import annotations

import json
import subprocess
import logging
from typing import Any

logger = logging.getLogger(__name__)

# GMGN CLI 默认超时（秒）
DEFAULT_TIMEOUT = 30
RETRY_COUNT = 1


class GmgnError(Exception):
    """GMGN CLI 调用失败"""
    pass


class GmgnClient:
    """gmgn-cli subprocess 封装"""

    def __init__(self, cli_path: str = "gmgn-cli", timeout: int = DEFAULT_TIMEOUT):
        self.cli_path = cli_path
        self.timeout = timeout

    def _run(self, args: list[str]) -> dict:
        """
        执行 gmgn-cli 命令，返回解析后的 JSON。
        失败时重试 1 次。
        """
        cmd = [self.cli_path] + args
        cmd_str = " ".join(cmd)
        logger.info(f"GMGN: {cmd_str}")

        last_error = None
        for attempt in range(1 + RETRY_COUNT):
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                )
                if result.returncode != 0:
                    last_error = GmgnError(
                        f"gmgn-cli exit {result.returncode}: {result.stderr.strip()}"
                    )
                    logger.warning(f"GMGN attempt {attempt + 1} failed: {last_error}")
                    continue

                data = json.loads(result.stdout)
                return data

            except subprocess.TimeoutExpired:
                last_error = GmgnError(f"gmgn-cli timeout after {self.timeout}s")
                logger.warning(f"GMGN attempt {attempt + 1} timeout")
            except json.JSONDecodeError as e:
                last_error = GmgnError(f"gmgn-cli JSON parse error: {e}")
                logger.warning(f"GMGN attempt {attempt + 1} JSON error: {e}")

        raise last_error  # type: ignore[misc]

    # ──────────────────────────────────────
    # Skill 01: meme-candidate-entry
    # ──────────────────────────────────────

    def token_info(self, address: str, chain: str = "sol") -> dict:
        """gmgn-cli token info"""
        return self._run([
            "token", "info",
            "--chain", chain,
            "--address", address,
            "--raw",
        ])

    def market_trending(
        self, chain: str = "sol", interval: str = "1h",
        order_by: str = "volume", limit: int = 50,
    ) -> dict:
        """gmgn-cli market trending"""
        return self._run([
            "market", "trending",
            "--chain", chain,
            "--interval", interval,
            "--order-by", order_by,
            "--limit", str(limit),
            "--raw",
        ])

    def market_trenches(
        self, chain: str = "sol", type_: str = "completed",
        filter_preset: str = "strict", sort_by: str = "smart_degen_count",
    ) -> dict:
        """gmgn-cli market trenches"""
        return self._run([
            "market", "trenches",
            "--chain", chain,
            "--type", type_,
            "--filter-preset", filter_preset,
            "--sort-by", sort_by,
            "--raw",
        ])

    def market_signal(
        self, chain: str = "sol", signal_type: int = 12,
    ) -> dict:
        """gmgn-cli market signal"""
        return self._run([
            "market", "signal",
            "--chain", chain,
            "--signal-type", str(signal_type),
            "--raw",
        ])

    # ──────────────────────────────────────
    # Skill 02: meme-token-panel
    # ──────────────────────────────────────

    def token_security(self, address: str, chain: str = "sol") -> dict:
        """gmgn-cli token security"""
        return self._run([
            "token", "security",
            "--chain", chain,
            "--address", address,
            "--raw",
        ])

    def token_pool(self, address: str, chain: str = "sol") -> dict:
        """gmgn-cli token pool"""
        return self._run([
            "token", "pool",
            "--chain", chain,
            "--address", address,
            "--raw",
        ])

    def market_kline(
        self, address: str, chain: str = "sol",
        resolution: str = "5m", from_ts: str = "", to_ts: str = "",
    ) -> dict:
        """gmgn-cli market kline"""
        args = [
            "market", "kline",
            "--chain", chain,
            "--address", address,
            "--resolution", resolution,
            "--raw",
        ]
        if from_ts:
            args += ["--from", from_ts]
        if to_ts:
            args += ["--to", to_ts]
        return self._run(args)

    # ──────────────────────────────────────
    # Skill 03: meme-wallet-roles
    # ──────────────────────────────────────

    def token_holders(
        self, address: str, chain: str = "sol",
        limit: int = 50, tag: str | None = None,
        order_by: str = "amount_percentage", direction: str = "desc",
    ) -> dict:
        """gmgn-cli token holders"""
        args = [
            "token", "holders",
            "--chain", chain,
            "--address", address,
            "--limit", str(limit),
            "--order-by", order_by,
            "--direction", direction,
            "--raw",
        ]
        if tag:
            args += ["--tag", tag]
        return self._run(args)

    def token_traders(
        self, address: str, chain: str = "sol",
        limit: int = 50, tag: str | None = None,
        order_by: str = "profit", direction: str = "desc",
    ) -> dict:
        """gmgn-cli token traders"""
        args = [
            "token", "traders",
            "--chain", chain,
            "--address", address,
            "--limit", str(limit),
            "--order-by", order_by,
            "--direction", direction,
            "--raw",
        ]
        if tag:
            args += ["--tag", tag]
        return self._run(args)

    def portfolio_created_tokens(
        self, wallet: str, chain: str = "sol",
        order_by: str = "token_ath_mc", direction: str = "desc",
    ) -> dict:
        """gmgn-cli portfolio created-tokens"""
        return self._run([
            "portfolio", "created-tokens",
            "--chain", chain,
            "--wallet", wallet,
            "--order-by", order_by,
            "--direction", direction,
            "--raw",
        ])

    def portfolio_stats(
        self, wallet: str, chain: str = "sol", period: str = "30d",
    ) -> dict:
        """gmgn-cli portfolio stats"""
        return self._run([
            "portfolio", "stats",
            "--chain", chain,
            "--wallet", wallet,
            "--period", period,
            "--raw",
        ])

    # ──────────────────────────────────────
    # Skill 04: meme-wallet-structure (补充查询)
    # ──────────────────────────────────────

    def portfolio_activity(
        self, wallet: str, chain: str = "sol",
        type_: str = "buy", limit: int = 5,
    ) -> dict:
        """gmgn-cli portfolio activity"""
        return self._run([
            "portfolio", "activity",
            "--chain", chain,
            "--wallet", wallet,
            "--type", type_,
            "--limit", str(limit),
            "--raw",
        ])

    def portfolio_token_balance(
        self, wallet: str, token: str, chain: str = "sol",
    ) -> dict:
        """gmgn-cli portfolio token-balance"""
        return self._run([
            "portfolio", "token-balance",
            "--chain", chain,
            "--wallet", wallet,
            "--token", token,
            "--raw",
        ])
