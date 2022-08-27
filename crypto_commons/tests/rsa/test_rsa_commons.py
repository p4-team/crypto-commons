import unittest
from crypto_commons.generic import factor
from crypto_commons.rsa.rsa_commons import get_fi


class TestRsaCommons(unittest.TestCase):
    def test_phi(self):
        # Hardcoded test cases
        # Borrowed from https://primefan.tripod.com/Phi500.html
        test_cases = {
            1: 1,
            2: 1,
            3: 2,
            4: 2,
            5: 4,
            6: 2,
            7: 6,
            8: 4,
            9: 6,
            10: 4,
            11: 10,
            12: 4,
            13: 12,
            14: 6,
            15: 8,
            16: 8,
            17: 16,
            18: 6,
            19: 18,
            20: 8,
            21: 12,
            22: 10,
            23: 22,
            24: 8,
            25: 20,
            26: 12,
            27: 18,
            28: 12,
            29: 28,
            30: 8,
            31: 30,
            32: 16,
            33: 20,
            34: 16,
            35: 24,
            36: 12,
            37: 36,
            38: 18,
            39: 24,
            40: 16,
        }
        for n, phi_n in test_cases.items():
            self.assertEqual(get_fi(factor(n)[0]), phi_n)
