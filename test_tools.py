import unittest

from tools import calculate


class CalculateTests(unittest.TestCase):
    def test_add(self):
        self.assertEqual(
            calculate("add", 2, 3),
            {"ok": True, "result": 5},
        )

    def test_subtract(self):
        self.assertEqual(
            calculate("subtract", 10, 4),
            {"ok": True, "result": 6},
        )

    def test_multiply(self):
        self.assertEqual(
            calculate("multiply", 6, 7),
            {"ok": True, "result": 42},
        )

    def test_divide(self):
        self.assertEqual(
            calculate("divide", 12, 3),
            {"ok": True, "result": 4},
        )

    def test_divide_by_zero(self):
        self.assertFalse(calculate("divide", 1, 0)["ok"])

    def test_invalid_operation(self):
        self.assertFalse(calculate("power", 2, 3)["ok"])

    def test_invalid_number(self):
        self.assertFalse(calculate("add", "2", 3)["ok"])


if __name__ == "__main__":
    unittest.main()

