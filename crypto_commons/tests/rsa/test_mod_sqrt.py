import random
import unittest

from crypto_commons.generic import get_primes, multiply
from crypto_commons.rsa.rsa_commons import modular_sqrt, modular_sqrt_composite, modular_sqrt_composite_powers


class TestModSqrt(unittest.TestCase):
    def test_roots_over_prime(self):
        primes = get_primes(10000)
        for i in range(0, 10):
            prime = random.choice(primes)
            root = random.randint(prime // 2, prime - 1)
            residue = pow(root, 2, prime)
            with self.subTest(prime=prime, root=root, residue=residue):
                computed_root = modular_sqrt(residue, prime)
                self.assertTrue(root in [computed_root, prime - computed_root])

    def test_roots_over_simple_composites(self):
        primes = get_primes(10000)
        for i in range(0, 10):
            factors = random.sample(primes, k=random.randint(2, 10))
            modulus = multiply(factors)
            root = random.randint(modulus // 2, modulus - 1)
            residue = pow(root, 2, modulus)
            with self.subTest(root=root, residue=residue, factors=factors):
                self.assertTrue(root in modular_sqrt_composite(residue, factors))

    def test_roots_over_composites_with_prime_powers(self):
        primes = get_primes(10000)
        for i in range(0, 10):
            simple_factors = random.sample(primes, k=random.randint(2, 10))
            factors = sum([[prime] * random.randint(2, 10) for prime in simple_factors], [])
            modulus = multiply(factors)
            root = random.randint(modulus // 2, modulus - 1)
            residue = pow(root, 2, modulus)
            with self.subTest(root=root, residue=residue, factors=factors):
                self.assertTrue(root in modular_sqrt_composite_powers(residue, factors))
