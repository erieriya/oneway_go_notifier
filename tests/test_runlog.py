import json

from src.runlog import append_entry


def test_append_entry_creates_file_with_one_line(tmp_path):
    path = tmp_path / "run_log.jsonl"
    append_entry({"a": 1}, path=path)

    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0]) == {"a": 1}


def test_append_entry_accumulates_lines(tmp_path):
    path = tmp_path / "run_log.jsonl"
    append_entry({"n": 1}, path=path)
    append_entry({"n": 2}, path=path)

    lines = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert lines == [{"n": 1}, {"n": 2}]


def test_append_entry_trims_to_max_entries(tmp_path):
    path = tmp_path / "run_log.jsonl"
    for n in range(5):
        append_entry({"n": n}, path=path, max_entries=3)

    lines = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert lines == [{"n": 2}, {"n": 3}, {"n": 4}]
