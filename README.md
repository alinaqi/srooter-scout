# srooter-scout — Local AI Code Audit & Readiness CLI

`srooter-scout` is a free, standalone open-source CLI tool that analyzes your local AI coding-agent history (Claude Code, srooter-agent, aider) and hardware to show you where you're wasting tokens and what you can optimize.

Developed as a companion tool for the [srooter](https://www.srooter.ai) AI gateway.

---

## What it does

1. **Usage & Inefficiency Audit:** Scan local agent logs (privacy-safe, metadata-only) to detect token usage, redundant reads, overpaying on trivial tasks, and model distribution.
2. **Local Model Recommendation:** Assess your local CPU, RAM, and GPU (Nvidia CUDA, Apple Silicon Metal, AMD ROCm) and recommend the best Ollama-compatible local models to run.
3. **srooter Cost Projection:** Model how much srooter's gateway-based routing (quality x speed x cost) would slash your API bill at equal task quality (SWE-bench verified).

👉 **Ready to slash your token costs?** Get started with [srooter.ai](https://www.srooter.ai) to route your frontier agent tasks to cheap models automatically.

---

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/alinaqi/srooter-scout.git
cd srooter-scout
pip install -e .
```

---

## Usage

Run the scanner in your terminal:

```bash
srooter-scout
```

### Flags

- `--json`: Output results in machine-readable JSON.
- `--markdown`: Save a shareable Markdown report (`report.md`).
- `--dry-run`: Skip local log scan; use sample data to see the report format.
- `--help`: Show usage info.

---

## Examples

### Quick scan (terminal output)

```bash
srooter-scout
```

### Check your real estimated API savings

```bash
srooter-scout
#  Savings: 75.7% ($27,932 → $6,792)
```

### JSON output (for CI pipelines / dashboards)

```bash
srooter-scout --json
```

```json
{
  "hardware": {
    "ram_gb": 128,
    "cpu_cores": 16,
    "cpu_arch": "arm64",
    "gpu_name": "Apple M4 Max",
    "model_size_class": "32b+"
  },
  "usage": {
    "total_tokens": 1888550,
    "total_cost": 27931.6203,
    "model_breakdown": {
      "claude-opus": {"input": 1535998, "output": 55529},
      "glm-5.2": {"input": 0, "output": 137664},
      "gpt-5.5": {"input": 22117, "output": 16097}
    }
  },
  "recommendation": {
    "local_model": "DeepSeek-Coder V2 70B or Qwen 2.5-Coder 32B (Ollama: deepseek-coder-v2:70b)",
    "srooter_cost_est": 6792.34,
    "savings_pct": 75.7
  }
}
```

### Share a markdown report

```bash
srooter-scout --markdown > report.md
```

### Try it without scanning history

```bash
srooter-scout --dry-run
```

### Quick local model check (no history scan needed)

```bash
srooter-scout --json | python -c "import json,sys; d=json.load(sys.stdin); print(f'You can run: {d[\"recommendation\"][\"local_model\"]}')"
```

---

## Example Output

```text
   ╔══════════════════════════════════════╗
   ║         srooter-scout                ║
   ║  Local AI Code Audit & Readiness     ║
   ╚══════════════════════════════════════╝


Hardware:  CPU: 16 cores (arm64) / RAM: 128 GB / GPU: Apple M4 Max

Usage Scan:
  Total tokens:       1,888,550
  Estimated cost:     $27,931.62
  Redundant reads:    0
  Trivial→frontier:   0

  Model breakdown:
    claude-opus         1,535,998 in  55,529 out
    glm-5.2             0 in  137,664 out
    deepseek-pro        0 in  46,203 out

Recommendations:
  Local model:  DeepSeek-Coder V2 70B or Qwen 2.5-Coder 32B (Ollama: deepseek-coder-v2:70b)
  Current cost:     $27,931.62
  With srooter:     ~$6,792.34
  Estimated savings: 75.7%
```

---

## Privacy Policy & Safeguards

- **Offline by Default:** No network calls are made. No telemetry is collected or sent unless explicitly requested.
- **Metadata Only:** The parser strictly extracts metadata (model name, token counts, timestamps, tool names) — **it never reads your actual prompt text or source code content**.
- **Local Scan:** Your history files are parsed locally on your machine and never leave your workstation.

---

## Related

- **[srooter](https://www.srooter.ai)** — The AI model gateway that powers this audit's routing projections. Transparent governance: budgets, policies, routing, council review, audit — invisible to developers.
- **[srooter (GitHub)](https://github.com/alinaqi/srooter)** — Source code for the srooter gateway (closed source, commercial).

## License

MIT License. See [LICENSE](LICENSE) for details.
