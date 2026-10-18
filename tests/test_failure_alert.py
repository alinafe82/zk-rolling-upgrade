"""Exercise the actual workflow's Bash JSON parsing expressions."""

import json
import os
import re
import subprocess
from pathlib import Path

import pytest

WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/failure-alert.yml"
EXPRESSIONS = re.findall(
    r"\$\((jq -r \'\.[a-z_]+ // empty\'[^\n]+)\)",
    WORKFLOW.read_text(encoding="utf-8"),
)


@pytest.mark.parametrize("populated", [False, True])
def test_alert_json_expressions(populated):
    assert len(EXPRESSIONS) == 4
    env = {
        **os.environ,
        "latest_run": '{"id":123,"run_attempt":2,"name":"CI"}' if populated else "",
        "issue_record": '{"number":456}' if populated else "",
    }
    expected = ["123", "2", "CI", "456"] if populated else [""] * 4
    for expression, value in zip(EXPRESSIONS, expected, strict=True):
        result = subprocess.run(
            ["bash", "-euo", "pipefail", "-c", expression],
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )
        assert result.stdout.strip() == value


@pytest.mark.parametrize(
    "body",
    [
        None,
        "unrelated",
        "<!-- ci-failure-alert:42:1:1 -->",
        "<!-- ci-failure-alert:42 -->",
    ],
)
def test_alert_issue_matching(body):
    query = re.search(
        r"--arg legacy_marker[^\n]+\n\s+'(.*?)' <<<",
        WORKFLOW.read_text(encoding="utf-8"),
        re.DOTALL,
    )
    assert query is not None
    result = subprocess.run(
        [
            "jq",
            "-c",
            "--arg",
            "marker_prefix",
            "<!-- ci-failure-alert:42:",
            "--arg",
            "legacy_marker",
            "<!-- ci-failure-alert:42 -->",
            query.group(1),
        ],
        input=json.dumps([[{"number": 7, "body": body}]]),
        text=True,
        capture_output=True,
        check=True,
    )
    assert result.stdout.strip() == (
        json.dumps({"number": 7, "body": body}, separators=(",", ":"))
        if body and body.startswith("<!--")
        else ""
    )
