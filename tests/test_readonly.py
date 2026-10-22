"""Tests for the guard's read-only allowance. Run: python3 tests/test_readonly.py

1. Lockstep's read-only scripts call no Plugin API that changes a file.
2. The guard lets an exact read-only render reach a protected file, and blocks everything
   else: other code, an edited render, a forged stamp, a value that smuggles in code, and a
   read-only script run through a different tool.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "plugin" / "scripts"
GUARD = ROOT / "plugin" / "hooks" / "guard.py"
KEY = "TESTPROTECTEDKEY0000000000"
ENV = {**os.environ, "LOCKSTEP_PROTECTED_FILE_KEYS": KEY, "HOME": str(ROOT / "tests" / "no-home"), "CLAUDE_PROJECT_DIR": str(ROOT / "tests" / "no-project")}

sys.path.insert(0, str(SCRIPTS))
os.environ.update({k: ENV[k] for k in ("LOCKSTEP_PROTECTED_FILE_KEYS", "HOME", "CLAUDE_PROJECT_DIR")})
import render  # noqa: E402

# Plugin API calls and node properties that change a document. Reading them is fine;
# calling (or assigning to) them is not.
MUTATING_CALLS = [
    r"figma\.create\w*", r"figma\.variables\.create\w*", r"figma\.(group|ungroup|flatten|union|subtract|intersect|exclude|combineAsVariants)\b",
    r"figma\.import\w*", r"figma\.setCurrentPageAsync", r"figma\.currentPage\s*=", r"figma\.loadAllPagesAsync",
    r"\.(appendChild|insertChild|remove|detachInstance|createInstance|swapComponent|resetOverrides|clone|resize|resizeWithoutConstraints|rescale)\s*\(",
    r"\.(setBoundVariable|setBoundVariableForPaint|setValueForMode|setProperties|setPluginData|setSharedPluginData|setRelaunchData|setExplicitVariableModeForCollection)\s*\(",
    r"\.set\w*(Style|StyleId)\w*Async\s*\(", r"\.setRange\w+\s*\(", r"\.(insertCharacters|deleteCharacters)\s*\(",
    r"figma\.(commitUndo|triggerUndo|closePlugin)", r"\.(addComponentProperty|editComponentProperty|deleteComponentProperty)\s*\(",
]
NODE_PROPS = r"(name|x|y|fills|strokes|effects|characters|visible|opacity|layoutMode|padding\w*|itemSpacing|cornerRadius|\w+Radius|strokeWeight|fontSize|fontName|textStyleId|layoutSizing\w+|clipsContent|locked|constraints|description|scopes|rotation|layoutGrow|layoutAlign|primaryAxis\w+|counterAxis\w+)"
ASSIGN = re.compile(r"\b(n|node|x|inst|root|page|main|set|d|c|comp|v|col|s)\." + NODE_PROPS + r"\s*=(?!=)")

failures = []


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        failures.append(msg)


def guard(tool, tool_input):
    call = {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": tool_input}
    return subprocess.run([sys.executable, str(GUARD)], input=json.dumps(call), capture_output=True, text=True, env=ENV).returncode


for name in render.READONLY:
    source = (SCRIPTS / f"{name}.js").read_text()
    code = "\n".join(l for l in source.splitlines() if not l.strip().startswith("//"))
    hits = [m.group(0) for pat in MUTATING_CALLS for m in re.finditer(pat, code)] + [m.group(0) for m in ASSIGN.finditer(code)]
    check(not hits, f"{name}.js calls no mutating API" + (f": found {hits}" if hits else ""))

USE = "mcp__figma__use_figma"
audit = render.render("audit", {"ROOT_IDS": json.dumps(["0:1"]), "OFFSET": "0"})
inv = render.render("inventory_local", {"PART": json.dumps("variables"), "PAGE_IDS": "[]"})
score = render.render("score", {"ROOT_IDS": json.dumps(["1:2"])})
fix = render.render("fix", {"ROOT_IDS": json.dumps(["1:2"])})

check(guard(USE, {"fileKey": KEY, "code": audit}) == 0, "exact audit render reaches a protected file")
check(guard(USE, {"fileKey": KEY, "code": inv}) == 0, "exact inventory_local render reaches a protected file")
check(guard(USE, {"fileKey": KEY, "code": score}) == 0, "exact score render reaches a protected file")
check(guard(USE, {"fileKey": KEY, "code": fix}) == 2, "fix (writes) is blocked on a protected file")
check(guard(USE, {"fileKey": KEY, "code": "return 1"}) == 2, "hand-written code is blocked on a protected file")
check(guard(USE, {"fileKey": KEY, "code": audit.replace("const EXAMPLES = 4;", "const EXAMPLES = 4; figma.root.children[0].remove();")}) == 2, "an edited render is blocked")
check(guard(USE, {"fileKey": KEY, "code": audit + "\nfigma.createFrame();"}) == 2, "a render with code appended is blocked")
forged = audit.splitlines()[0].replace('"audit"', '"fix"') + "\n" + fix
check(guard(USE, {"fileKey": KEY, "code": forged}) == 2, "a stamp naming a write script is blocked")
smuggle = render.MARKER + json.dumps({"script": "audit", "values": {"ROOT_IDS": '[]; figma.root.remove(); //', "OFFSET": "0"}}) + "\n"
check(guard(USE, {"fileKey": KEY, "code": smuggle + audit.split("\n", 1)[1]}) == 2, "a value that isn't plain JSON is blocked")
check(guard("mcp__figma__generate_figma_design", {"fileKey": KEY, "code": audit}) == 2, "the allowance only applies to use_figma")
check(guard(USE, {"fileKey": "SOMEDRAFTKEY00000000000000", "code": "return 1"}) == 0, "unprotected files are untouched by the guard")

print(f"\n{len(failures)} failed" if failures else "\nall passed")
sys.exit(1 if failures else 0)
