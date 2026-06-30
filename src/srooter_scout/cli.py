"""srooter-scout CLI — local AI audit & readiness tool."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from srooter_scout.hardware import detect_hardware
from srooter_scout.history import parse_claude_history, parse_srooter_sessions
from srooter_scout.recommender import recommend_models
from srooter_scout.report import generate_report


def help_text() -> str:
    return (
        'usage: srooter-scout [--json] [--markdown] [--dry-run] [--help]\n\n'
        'Local AI code audit tool.\n\n'
        'Analyze your coding agent history and hardware to find:\n'
        '  1) Token inefficiencies and overspending\n'
        '  2) Best local models for your system\n'
        '  3) How srooter can reduce your API costs\n\n'
        'Flags:\n'
        '  --json       Output machine-readable JSON\n'
        '  --markdown   Output as markdown file\n'
        '  --dry-run    Skip network checks; use sample data\n'
        '  --help       Show this help\n'
    )


def _default_history_path() -> str:
    home = os.path.expanduser('~')
    return os.path.join(home, '.claude', 'history.jsonl')


def _default_srooter_sessions() -> str:
    return os.path.join(os.path.expanduser('~'), '.srooter', 'agent', 'sessions')


def main() -> int:
    args = [a for a in sys.argv[1:] if a.startswith('--')]
    flags = {f.lstrip('-') for f in args}
    bare = [a for a in sys.argv[1:] if a not in args]

    valid_flags = {'help', 'json', 'markdown', 'dry-run'}
    unknown = flags - valid_flags
    if unknown:
        sys.stderr.write(f'error: unknown flag(s): {", ".join(unknown)}\n')
        sys.stderr.write(help_text())
        return 2

    if 'help' in flags or bare == ['help']:
        sys.stdout.write(help_text())
        return 0

    if 'json' in flags:
        fmt = 'json'
    elif 'markdown' in flags:
        fmt = 'markdown'
    else:
        fmt = 'terminal'

    hw = detect_hardware()
    if 'dry-run' in flags:
        # Example scan for users with no history
        from srooter_scout.history import ScanResult
        from srooter_scout.recommender import Recommendation
        sample = ScanResult(
            total_tokens=118000,
            model_spend={'claude-opus': {'input': 80000, 'output': 38000}},
        )
        rec = Recommendation(
            local_model='Qwen 2.5-Coder 7B (Ollama: qwen-coder:7b)',
            srooter_cost_est=10.75,
            savings_pct=82.0,
            current_cost_est=sample.total_cost,
        )
    else:
        # Real scan
        history = parse_claude_history(_default_history_path())
        srooter_history = parse_srooter_sessions(_default_srooter_sessions())
        history.merge(srooter_history)
        rec = recommend_models(hw, history)
        sample = history

    if fmt == 'json':
        data = {
            'hardware': {
                'ram_gb': hw.ram_gb,
                'cpu_cores': hw.cpu_cores,
                'cpu_arch': hw.cpu_arch,
                'gpu_name': hw.gpu_name,
                'gpu_vram_gb': hw.gpu_vram_gb,
                'model_size_class': hw.model_size_class(),
            },
            'usage': {
                'total_tokens': sample.total_tokens,
                'total_cost': sample.total_cost,
                'redundant_reads': sample.redundant_reads,
                'trivial_to_frontier': sample.trivial_to_frontier,
                'model_breakdown': sample.model_spend,
            },
            'recommendation': {
                'local_model': rec.local_model,
                'srooter_cost_est': rec.srooter_cost_est,
                'savings_pct': rec.savings_pct,
            },
        }
        sys.stdout.write(json.dumps(data, indent=2) + '\n')
    else:
        sys.stdout.write(generate_report(hw, sample, rec, fmt) + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
