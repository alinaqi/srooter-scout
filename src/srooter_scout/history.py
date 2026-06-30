"""Privacy-safe local agent history parser.

NEVER reads prompt content — only metadata (model, token counts, tool names).
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from srooter_scout.ratings_data import cost_usd


@dataclass
class ScanResult:
    total_tokens: int = 0
    total_cost: float = 0.0
    model_spend: dict[str, dict[str, int]] = field(default_factory=dict)
    redundant_reads: int = 0
    trivial_to_frontier: int = 0
    errors: int = 0
    sources: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.model_spend:
            self._recalc_cost()

    def merge(self, other: ScanResult) -> None:
        self.total_tokens += other.total_tokens
        self.total_cost += other.total_cost
        self.errors += other.errors
        self.redundant_reads += other.redundant_reads
        self.trivial_to_frontier += other.trivial_to_frontier
        self.sources.extend(other.sources)
        for alias, counts in other.model_spend.items():
            if alias not in self.model_spend:
                self.model_spend[alias] = counts
            else:
                self.model_spend[alias]['input'] += counts['input']
                self.model_spend[alias]['output'] += counts['output']
        self._recalc_cost()

    def _recalc_cost(self) -> None:
        self.total_cost = 0.0
        for alias, counts in self.model_spend.items():
            self.total_cost += cost_usd(alias, counts['input'], counts['output'])


_FRONTIER_ALIASES = frozenset({
    'claude-opus', 'claude-sonnet', 'gpt-5.5', 'gemini-3.5-pro',
})

_TRIVIAL_TOOLS = frozenset({
    'Bash', 'ls', 'cat', 'grep', 'glob', 'ListFiles', 'Search',
    'ReadLines', 'Status', 'Glob', 'Grep',
})


def parse_claude_history(path: str) -> ScanResult:
    result = ScanResult(sources=['Claude Code history'])
    try:
        if not os.path.isfile(path):
            return result
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    result.errors += 1
                    continue
                _process_entry(entry, result)
        return result
    except Exception:
        return result


def parse_srooter_sessions(sessions_dir: str) -> ScanResult:
    result = ScanResult(sources=['srooter-agent sessions'])
    try:
        if not os.path.isdir(sessions_dir):
            return result
        for fname in sorted(os.listdir(sessions_dir)):
            if not fname.endswith('.json'):
                continue
            try:
                with open(os.path.join(sessions_dir, fname)) as f:
                    session = json.load(f)
                usage = session.get('usage', {})
                alias = session.get('model', 'unknown')
                tin = usage.get('inputTokens', 0)
                tout = usage.get('outputTokens', 0)
                if tin or tout:
                    if alias not in result.model_spend:
                        result.model_spend[alias] = {'input': 0, 'output': 0}
                    result.model_spend[alias]['input'] += tin
                    result.model_spend[alias]['output'] += tout
                    result.total_tokens += tin + tout
            except Exception:
                result.errors += 1
        result._recalc_cost()
        return result
    except Exception:
        return result


def _process_entry(entry: dict[str, Any], result: ScanResult) -> None:
    alias = entry.get('model', '')
    if not alias:
        return
    tin = entry.get('input_tokens', 0) or 0
    tout = entry.get('output_tokens', 0) or 0
    if alias not in result.model_spend:
        result.model_spend[alias] = {'input': 0, 'output': 0}
    result.model_spend[alias]['input'] += tin
    result.model_spend[alias]['output'] += tout
    result.total_tokens += tin + tout
    # flag redundant reads
    tool = entry.get('tool', '')
    file_size = entry.get('file_size_hint', 0) or 0
    if tool in ('Read', 'cat', 'read_file') and file_size > 10000:
        result.redundant_reads += 1
    # flag frontier usage on trivial ops
    tool_used = tool or entry.get('tool_calls', [{}])[0].get('name', '')
    if alias in _FRONTIER_ALIASES and tool_used in _TRIVIAL_TOOLS:
        result.trivial_to_frontier += 1
