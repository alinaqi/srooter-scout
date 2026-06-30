"""Terminal report generator with ASCII sections."""
from __future__ import annotations

from srooter_scout.hardware import HardwareProfile
from srooter_scout.history import ScanResult
from srooter_scout.recommender import Recommendation


_ASCII_LOGO = r"""
   ╔══════════════════════════════════════╗
   ║         srooter-scout                ║
   ║  Local AI Code Audit & Readiness     ║
   ╚══════════════════════════════════════╝
"""


def generate_report(hw: HardwareProfile, hist: ScanResult, rec: Recommendation, fmt: str = 'markdown') -> str:
    if fmt == 'markdown':
        return _markdown(hw, hist, rec)
    return _terminal(hw, hist, rec)


def _terminal(hw: HardwareProfile, hist: ScanResult, rec: Recommendation) -> str:
    lines = [_ASCII_LOGO, '', f'Hardware:  {hw.summary()}', '']
    lines.append('Usage Scan:')
    lines.append(f'  Total tokens:       {hist.total_tokens:,}')
    lines.append(f'  Estimated cost:     ${hist.total_cost:.4f}')
    lines.append(f'  Redundant reads:    {hist.redundant_reads}')
    lines.append(f'  Trivial→frontier:   {hist.trivial_to_frontier}')
    lines.append('')
    if hist.model_spend:
        lines.append('  Model breakdown:')
        for alias, counts in sorted(hist.model_spend.items()):
            lines.append(f'    {alias:<18}  {counts["input"]:,} in  {counts["output"]:,} out')
    lines.append('')
    lines.append('Recommendations:')
    lines.append(f'  Local model:  {rec.local_model}')
    if hist.total_cost > 0:
        lines.append(f'  Current cost:     ${rec.current_cost_est:.4f}')
        lines.append(f'  With srooter:     ~${rec.srooter_cost_est:.4f}')
        lines.append(f'  Estimated savings: {rec.savings_pct:.1f}%')
    else:
        lines.append('  (no history data — run with a coding agent first)')
    lines.append('')
    return '\n'.join(lines)


def _markdown(hw: HardwareProfile, hist: ScanResult, rec: Recommendation) -> str:
    lines = [
        '# srooter-scout Report',
        '',
        f'**Hardware:** {hw.summary()}',
        '',
        '## Usage Summary',
        '',
        f'| Metric | Value |',
        '|--------|-------|',
        f'| Total tokens | {hist.total_tokens:,} |',
        f'| Estimated cost | ${hist.total_cost:.4f} |',
        f'| Inefficient reads | {hist.redundant_reads} |',
        f'| Trivial tasks → frontier model | {hist.trivial_to_frontier} |',
        '',
    ]
    if hist.model_spend:
        lines.append('### Model Breakdown')
        lines.append('')
        lines.append('| Model | Input tokens | Output tokens |')
        lines.append('|-------|-------------|--------------|')
        for alias, counts in sorted(hist.model_spend.items()):
            lines.append(f'| {alias} | {counts["input"]:,} | {counts["output"]:,} |')
        lines.append('')
    lines.extend([
        '## Recommendations',
        '',
        f'- **Best local model:** {rec.local_model}',
        f'- **srooter projected cost:** ~${rec.srooter_cost_est:.4f}',
    ])
    if hist.total_cost > 0:
        lines.append(f'- **Estimated savings vs current:** {rec.savings_pct:.1f}%')
    else:
        lines.append('- *(Run with a coding agent first to generate cost projections.)*')
    return '\n'.join(lines)
