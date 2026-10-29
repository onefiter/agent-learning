import math


def calculate(operation: str, a: float, b: float) -> dict:
    allowed_operations = {
        "add",
        "subtract",
        "multiply",
        "divide",
    }

    if operation not in allowed_operations:
        return {
            "ok": False,
            "error": "不支持的计算操作",
        }

    for value in (a, b):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return {
                "ok": False,
                "error": "a 和 b 必须是数字",
            }

        try:
            finite = math.isfinite(value)
        except (OverflowError, TypeError):
            finite = False

        if not finite:
            return {
                "ok": False,
                "error": "数字超出支持范围",
            }

    try:
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        else:
            if b == 0:
                return {
                    "ok": False,
                    "error": "除数不能为零",
                }
            result = a / b

        if not math.isfinite(result):
            return {
                "ok": False,
                "error": "计算结果超出支持范围",
            }

    except (OverflowError, ValueError):
        return {
            "ok": False,
            "error": "计算结果超出支持范围",
        }

    return {
        "ok": True,
        "result": result,
    }
