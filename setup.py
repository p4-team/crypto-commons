from setuptools import setup, find_packages

setup(
    name = "crypto-commons",
    version = "0.0.1",
    author = "p4-team",
    author_email = "team@p4.team",

    url = "https://github.com/p4-team/crypto-commons",
    extras_require={
        ':python_version < "3.0"': [
            'future'
        ]
    },
    packages = find_packages()
)
