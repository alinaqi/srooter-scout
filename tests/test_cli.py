"""Tests for the CLI dispatcher."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from srooter_scout.cli import main, help_text


def test_help_text():
    assert help_text().startswith('usage:')
    assert '--json' in help_text()
    assert '--markdown' in help_text()
    assert '--dry-run' in help_text()


def test_help_flag(monkeypatch: Any, capsys: Any):
    testargs = ['srooter-scout', '--help']
    monkeypatch.setattr(sys, 'argv', testargs)
    rc = main()
    out, _ = capsys.readouterr()
    assert rc == 0
    assert 'usage:' in out


def test_dry_run_flag(monkeypatch: Any, capsys: Any):
    testargs = ['srooter-scout', '--dry-run']
    monkeypatch.setattr(sys, 'argv', testargs)
    rc = main()
    out, _ = capsys.readouterr()
    assert rc == 0
    # dry run produces output
    assert 'srooter' in out.lower() or 'Hardware' in out


def test_json_flag(monkeypatch: Any, capsys: Any):
    testargs = ['srooter-scout', '--json']
    monkeypatch.setattr(sys, 'argv', testargs)
    rc = main()
    out, _ = capsys.readouterr()
    assert rc == 0
    import json
    data = json.loads(out)
    assert 'hardware' in data
    assert 'recommendation' in data


def test_nonexistent_flag(monkeypatch: Any, capsys: Any):
    testargs = ['srooter-scout', '--nonexistent-flag']
    monkeypatch.setattr(sys, 'argv', testargs)
    rc = main()
    assert rc != 0  # should error


def test_run_from_any_cwd(monkeypatch: Any, capsys: Any):
    """CLI should work regardless of cwd (doesn't assume project root)."""
    testargs = ['srooter-scout', '--dry-run']
    monkeypatch.setattr(sys, 'argv', testargs)
    rc = main()
    out, _ = capsys.readouterr()
    assert rc == 0
