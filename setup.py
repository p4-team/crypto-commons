from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = "crypto-commons",
    version = "0.0.2",
    author = "p4-team",
    author_email = "team@p4.team",
    url = "https://github.com/p4-team/crypto-commons",
    extras_require={
        ':python_version < "3.0"': [
            'future'
        ]
    },
    description="Small python module for common CTF crypto functions.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages = find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
