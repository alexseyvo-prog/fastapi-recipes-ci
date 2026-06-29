import sys
import unittest


def decrypt(encryption: str) -> str:
    result: list = []
    dots: int = 0
    for symbol in encryption:
        if symbol != '.':
            result.append(symbol)
            dots = 0
            continue

        dots += 1
        if dots == 2 and result:
            result.pop()
            dots = 0

    return ''.join(result)


if __name__ == '__main__':
    data: str = sys.stdin.read()
    decryption: str = decrypt(data)
    print(decryption)


class TestDecrypt(unittest.TestCase):
    def test_one_dot_cases(self):
        cases = {
            'абра-кадабра.': 'абра-кадабра',
            '.': '',
        }
        for encrypted, expected in cases.items():
            with self.subTest(encrypted=encrypted):
                self.assertEqual(decrypt(encrypted), expected)

    def test_two_dot_cases(self):
        cases = {
            'абраа..-кадабра': 'абра-кадабра',
            'абра--..кадабра': 'абра-кадабра',
            'абр......a.': 'a',
            '1..2.3': '23',
        }
        for encrypted, expected in cases.items():
            with self.subTest(encrypted=encrypted):
                self.assertEqual(decrypt(encrypted), expected)

    def test_three_dot_cases(self):
        cases = {
            'абраа..-.кадабра': 'абра-кадабра',
            'абрау...-кадабра': 'абра-кадабра',
        }
        for encrypted, expected in cases.items():
            with self.subTest(encrypted=encrypted):
                self.assertEqual(decrypt(encrypted), expected)

    def test_many_dots_cases(self):
        cases = {
            'абра........': '',
            '1.......................': '',
        }
        for encrypted, expected in cases.items():
            with self.subTest(encrypted=encrypted):
                self.assertEqual(decrypt(encrypted), expected)


if __name__ == '__main__':
    unittest.main()