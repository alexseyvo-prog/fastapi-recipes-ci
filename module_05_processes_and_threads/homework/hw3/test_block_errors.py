import unittest
from block_errors import BlockErrors


class TestBlockErrors(unittest.TestCase):
    def test_error_is_ignored(self):
        """Ошибка из набора типов должна игнорироваться."""
        try:
            with BlockErrors({ZeroDivisionError}):
                _ = 1 / 0
        except ZeroDivisionError:
            self.fail("ZeroDivisionError не должен был быть прокинут")

    def test_error_is_propagated(self):
        """Ошибка не из набора типов должна прокидываться выше."""
        with self.assertRaises(ZeroDivisionError):
            with BlockErrors({TypeError}):
                _ = 1 / 0

    def test_inner_raises_outer_ignores(self):
        """
        Внутренний блок не игнорирует ошибку, она вылетает во внешний блок,
        а внешний блок её подавляет.
        """
        outer_err_types = {TypeError}
        with BlockErrors(outer_err_types):
            inner_err_types = {ZeroDivisionError}
            with BlockErrors(inner_err_types):
                # Здесь возникнет TypeError, inner его не подавит
                _ = 1 / "0"
            # До этой строки мы не дойдём, TypeError поднимется во внешний BlockErrors
        # Если внешний BlockErrors не подавил бы TypeError, тест упал бы

    def test_child_errors_are_ignored(self):
        """Дочерние ошибки тоже игнорируются (через issubclass)."""
        class MyZeroDivisionError(ZeroDivisionError):
            pass

        try:
            with BlockErrors({ZeroDivisionError}):
                raise MyZeroDivisionError("custom")
        except MyZeroDivisionError:
            self.fail("Производный MyZeroDivisionError должен быть подавлен")


if __name__ == '__main__':
    unittest.main()