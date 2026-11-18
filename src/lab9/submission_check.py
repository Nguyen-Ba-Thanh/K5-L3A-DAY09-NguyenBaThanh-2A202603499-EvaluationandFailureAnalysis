"""Audit local Lab9 deliverables without rerunning evaluations or changing reports.

This command writes its own audit JSON. It cannot certify hosted Actions,
hidden grading, or the user's review of AI-assisted documentation.
"""

import ast
import hashlib
import json
import subprocess
from pathlib import Path

import yaml

from lab8.console import utf8_stdio
from lab9 import evalset, gate
from lab9.eval import load_spec


def main():
    utf8_stdio()
    root = Path.cwd().parent
    checks = []

    def check(name, passed, detail=""):
        checks.append({"name": name, "passed": bool(passed), "detail": detail})
        print(f"{'PASS' if passed else 'FAIL'} {name}" + (f": {detail}" if detail else ""))

    required = [
        "src/lab9/stats.py", "src/lab9/graders.py", "src/lab9/evalset.py", "src/lab9/gate.py",
        "src/config/metric_spec.yaml", "src/config/metric_spec_v2.yaml", "src/config/fm_map.yaml",
        "docs/failure_taxonomy.md", "docs/trace_case.md", "docs/judge_audit.md",
        "docs/eval_card.md", "docs/PRD_v1.1.md", "docs/pr_evidence.md",
        "src/data/eval/eval_set_v1.jsonl", "src/data/eval/labels_v1.json",
        "src/data/eval/eval_set_v2.jsonl", "src/data/eval/labels_v2.json",
        "src/reports/baseline_v1.json", "src/reports/eval_fixed.json",
        "src/reports/eval_seeded_regression.json", "src/reports/baseline_v2.json",
        "src/reports/verification.json", ".github/workflows/eval-gate.yml",
        "LAB9_SUBMISSION.md", ".github/PULL_REQUEST_TEMPLATE.md",
    ]
    missing = [p for p in required if not (root / p).is_file()]
    check("Required files", not missing, ", ".join(missing))
    if missing:
        return 1
    for file in ("stats.py", "graders.py", "evalset.py", "gate.py"):
        tree = ast.parse((Path("lab9") / file).read_text(encoding="utf-8"))
        pending = [node for node in ast.walk(tree) if isinstance(node, ast.Name) and node.id == "NotImplementedError"]
        check(f"Implemented {file}", not pending)
    for version in (1, 2):
        items = Path(f"data/eval/eval_set_v{version}.jsonl")
        labels = Path(f"data/eval/labels_v{version}.json")
        problems = evalset.check(items, labels)
        check(f"Eval set v{version}", not problems, "; ".join(problems))
        check(f"Canonical LF v{version}", b"\r\n" not in items.read_bytes())
        spec = load_spec(Path("config/metric_spec.yaml" if version == 1 else "config/metric_spec_v2.yaml"))
        base = json.loads(Path(f"reports/baseline_v{version}.json").read_text(encoding="utf-8"))
        check(f"Baseline v{version} SHA", base["manifest"]["eval_set_sha"] == evalset.sha12(items))
        blocked, lines = gate.check(base, base, spec, spec)
        check(f"Baseline v{version} self-gate", not blocked, "; ".join(blocked))
        check(f"Baseline v{version} swarm", base.get("shape") == "swarm")
        check(f"Baseline v{version} complete", not base.get("evaluator_failures")
              and len(base["rows"]) == base["manifest"]["items"] * len(spec["seeds"]))
    harness = yaml.safe_load(Path("harness_map.yaml").read_text(encoding="utf-8"))
    check("Harness eval section", bool(harness.get("sections", {}).get("eval")))
    workflow = (root / ".github/workflows/eval-gate.yml").read_text(encoding="utf-8")
    check("Core and v2 workflow jobs", "eval-gate:" in workflow and "eval-gate-v2:" in workflow)
    taxonomy = (root / "docs/failure_taxonomy.md").read_text(encoding="utf-8")
    modes = {line.split("|")[1].strip() for line in taxonomy.splitlines() if line.startswith("| FM-")}
    check("Taxonomy >=5 FM", len(modes) >= 5)
    mapping = yaml.safe_load(Path("config/fm_map.yaml").read_text(encoding="utf-8"))
    check("Attack mapping uses taxonomy ids", all(v in modes for v in mapping.values()))
    verification = json.loads(Path("reports/verification.json").read_text(encoding="utf-8"))
    check("Core fixed accepted", verification["core"]["fixed"]["exit_code"] == 0)
    check("Core regression blocked on pass_rate", "pass_rate" in verification["core"]["seeded_regression"]["blocked"])
    check("Mutation score 3/3, 0 false alarms", verification["mutation_score"] == "3/3"
          and verification["false_alarms"] == 0)
    check("All recorded traps blocked", all(r["exit_code"] == 1 for r in verification["traps"].values()))
    check("A/A zero", all(value == 0 for value in verification["aa"]["deltas"].values()))
    # Inspect source and Git metadata without staging, committing or modifying global config.
    git = ["git", "-c", f"safe.directory={root.as_posix()}", "-C", str(root)]

    def git_output(*args):
        return subprocess.check_output([*git, *args], text=True, encoding="utf-8").strip()

    check("Lab8 unchanged from inherited HEAD", not git_output("diff", "HEAD", "--name-only", "--", "src/lab8"))
    starter = root.parent / "lab9-starter/src"
    if starter.is_dir():
        for rel in ("lab9/variants.py", "lab9/variant_agent.py", "lab9/traps.py",
                    "tests/test_lab9_stats.py", "tests/test_lab9_graders.py", "tests/test_lab9_advanced.py"):
            # Text comparison ignores checkout line endings; content must be the supplied one.
            check(f"Provided fixture unchanged: {rel}", Path(rel).read_text(encoding="utf-8")
                  == (starter / rel).read_text(encoding="utf-8"))
    code_hash = hashlib.sha256()
    for path in sorted(Path("lab9").glob("*.py")):
        code_hash.update(path.name.encode())
        code_hash.update(path.read_text(encoding="utf-8").replace("\r\n", "\n").encode())
    manual = [
        "Read and confirm the personal information, AI-use disclosure and audit conclusions.",
        "Stage the final changes, create a real commit, and record its hash in the PR description.",
        "Push starter/d09 and open a PR into main of the same personal fork.",
        "Check hosted eval-gate and eval-gate-v2 are green; paste docs/pr_evidence.md into the PR.",
        "Submit the PR/repository link via the channel requested by the course before its deadline.",
    ]
    result = {"command": "python -m lab9.submission_check", "checks": checks,
              "local_ready": all(c["passed"] for c in checks),
              "git": {"head": git_output("rev-parse", "HEAD"), "branch": git_output("branch", "--show-current"),
                      "origin": git_output("remote", "get-url", "origin"),
                      "uncommitted_changes": bool(git_output("status", "--porcelain"))},
              "lab9_source_sha256": code_hash.hexdigest(), "manual_steps": manual,
              "hosted_ci": "not_verified", "hidden_grade": "not_available"}
    Path("reports/submission_audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{'LOCAL READY' if result['local_ready'] else 'LOCAL INCOMPLETE'} — hosted CI and submission remain separate")
    return 0 if result["local_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
