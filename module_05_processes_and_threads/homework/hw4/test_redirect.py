import io
import sys
import traceback
import unittest

from redirect import Redirect


class TestRedirect(unittest.TestCase):
    def test_redirect_stdout(self):
        """Проверяем, что stdout перенаправляется в заданный поток."""
        buffer = io.StringIO()
        original_stdout = sys.stdout

        with Redirect(stdout=buffer):
            print("Hello stdout.txt")

        # stdout должен быть восстановлен
        self.assertIs(sys.stdout, original_stdout)
        # В буфере должно быть то, что мы печатали
        self.assertEqual(buffer.getvalue().strip(), "Hello stdout.txt")

    def test_redirect_stderr(self):
        """Проверяем, что stderr перенаправляется в заданный поток."""
        buffer = io.StringIO()
        original_stderr = sys.stderr

        with Redirect(stderr=buffer):
            try:
                raise Exception("Hello stderr.txt")
            except Exception:
                # Явно выводим трейсбек в текущий sys.stderr (буфер)
                traceback.print_exc()

        # stderr должен быть восстановлен
        self.assertIs(sys.stderr, original_stderr)
        # В буфере должен быть текст исключения
        text = buffer.getvalue()
        self.assertIn("Hello stderr.txt", text)
        self.assertIn("Traceback", text)

    def test_redirect_both_streams(self):
        """Проверяем одновременное перенаправление stdout и stderr."""
        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()

        with Redirect(stdout=stdout_buf, stderr=stderr_buf):
            print("to stdout")
            # Пишем в stderr напрямую
            print("to stderr", file=sys.stderr)

        self.assertIn("to stdout", stdout_buf.getvalue())
        self.assertIn("to stderr", stderr_buf.getvalue())

    def test_nested_redirects(self):
        """Проверяем корректную работу вложенных Redirect-блоков."""
        outer_buf = io.StringIO()
        inner_buf = io.StringIO()

        original_stdout = sys.stdout

        with Redirect(stdout=outer_buf):
            print("outer-1")
            with Redirect(stdout=inner_buf):
                print("inner")
            print("outer-2")

        # stdout восстановлен
        self.assertIs(sys.stdout, original_stdout)

        # Внешний буфер получил outer-строки, но не inner
        outer_text = outer_buf.getvalue().splitlines()
        self.assertEqual(outer_text, ["outer-1", "outer-2"])

        # Внутренний буфер получил только inner
        inner_text = inner_buf.getvalue().splitlines()
        self.assertEqual(inner_text, ["inner"])


if __name__ == '__main__':
    unittest.main()