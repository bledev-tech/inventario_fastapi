from __future__ import annotations

from typing import Any


def error_detail(code: str, message: str, *, context: dict[str, Any] | None = None) -> dict[str, Any]:
    detail: dict[str, Any] = {"code": code, "message": message}
    if context:
        detail["context"] = context
    return detail


__all__ = ["error_detail"]
