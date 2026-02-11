from __future__ import annotations

import difflib


def unified_diff(before: str, after: str, *, file_path: str) -> str:
    if before == after:
        raise ValueError("before and after content must differ to produce a unified diff")

    diff_lines = difflib.unified_diff(
        before.splitlines(),
        after.splitlines(),
        fromfile=f"a/{file_path}",
        tofile=f"b/{file_path}",
        lineterm="",
    )
    diff_text = "\n".join(diff_lines)
    if not diff_text:
        raise ValueError("unable to generate unified diff")
    return f"{diff_text}\n"
