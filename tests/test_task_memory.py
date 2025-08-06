import json
from task_memory import TaskMemory


def test_task_logging_and_analysis(tmp_path):
    path = tmp_path / "tasks.jsonl"
    tm = TaskMemory(path=path, max_entries=2)

    tm.log_task("type1", "prompt1", {}, "out1", True, 1.0)
    tm.log_task("type2", "prompt2", {}, "out2", False, 3.0)

    recent = tm.get_recent()
    assert len(recent) == 2
    assert recent[0]["task_type"] == "type1"
    assert recent[1]["task_type"] == "type2"

    analysis = tm.analyze_performance()
    assert analysis["task_count"] == 2
    assert analysis["success_rate"] == 0.5
    assert analysis["avg_duration"] == 2.0

    tm.log_task("type3", "prompt3", {}, "out3", True, 2.0)
    recent = tm.get_recent()
    assert len(recent) == 2
    assert recent[0]["task_type"] == "type2"
    assert recent[1]["task_type"] == "type3"
