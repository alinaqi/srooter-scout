"""Tests for privacy-safe history parsing."""
from pathlib import Path
from srooter_scout.history import parse_claude_history, parse_srooter_sessions, ScanResult


def test_parse_claude_history_empty(tmp_path: Path):
    f = tmp_path / 'history.jsonl'
    f.write_text('')
    result = parse_claude_history(str(f))
    assert isinstance(result, ScanResult)
    assert result.model_spend == {}
    assert result.total_tokens == 0
    assert result.total_cost == 0.0
    assert result.redundant_reads == 0
    assert result.trivial_to_frontier == 0


def test_parse_claude_history_one_entry(tmp_path: Path):
    f = tmp_path / 'history.jsonl'
    f.write_text('{"model":"claude-opus","message":1,"input_tokens":100,"output_tokens":50}\n')
    result = parse_claude_history(str(f))
    assert result.total_tokens == 150
    assert 'claude-opus' in result.model_spend
    assert result.model_spend['claude-opus']['input'] == 100
    assert result.model_spend['claude-opus']['output'] == 50


def test_parse_claude_history_skips_bad_line(tmp_path: Path):
    f = tmp_path / 'history.jsonl'
    f.write_text('not-json\n{"model":"claude-opus","message":1,"input_tokens":100,"output_tokens":50}\n')
    result = parse_claude_history(str(f))
    assert result.total_tokens == 150
    assert result.errors == 1


def test_parse_claude_history_missing_file():
    result = parse_claude_history('/nonexistent/history.jsonl')
    assert result.total_tokens == 0


def test_parse_srooter_session(tmp_path: Path):
    import json
    session = {
        'id': 's1', 'model': 'glm-5.2',
        'messages': [],
        'usage': {'inputTokens': 100, 'outputTokens': 50},
    }
    session_file = tmp_path / 's1.json'
    session_file.write_text(json.dumps(session))
    result = parse_srooter_sessions(str(tmp_path))
    assert result.total_tokens == 150
    assert 'glm-5.2' in result.model_spend


def test_parse_srooter_empty_dir(tmp_path: Path):
    result = parse_srooter_sessions(str(tmp_path))
    assert result.total_tokens == 0


def test_redundant_read_flagged(tmp_path: Path):
    f = tmp_path / 'history.jsonl'
    f.write_text(
        '{"model":"claude-opus","message":1,"input_tokens":49000,"output_tokens":10,'
        '"tool":"Read","file_size_hint":48000}\n'
    )
    result = parse_claude_history(str(f))
    assert result.redundant_reads >= 1


def test_trivial_to_frontier_flagged(tmp_path: Path):
    f = tmp_path / 'history.jsonl'
    f.write_text(
        '{"model":"claude-opus","message":1,"input_tokens":50,"output_tokens":10,'
        '"tool":"Glob","cmd":"find *.ts"}\n'
    )
    result = parse_claude_history(str(f))
    assert result.trivial_to_frontier >= 1
