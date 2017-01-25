# crypto-commons

Small python module for common CTF crypto functions.
Feel free to contribute if you think there is something missing, or if you have some interesting code to share.

In general we want to keep this as much dependency-free as possible, so most likely pull requests with a lot of external dependencies will not get merged.

For the record: this is not a generic-purpose crypto library, nor production-level cryptography implementation!
You should not use any of this code in real-life applications.

The problems we want to solve here:

- The need to constantly look for implementations for some less common algorithms (like Damgard-Jurik) or less common scenarios (like RSA with prime powers).
- The need to install many different libraries in order to use some simple function.
- Issues with installing dependencies on different environments. 
Especially with Python 2/3 incompatibility and compiled C-modules.
- Repeating the same code over and over again, and wasting time on debugging typos and small mistakes.

General guidelines we hope to follow:
- Split implementation into small steps. CTF tasks often require changes in some of the algorithms, 
so it would be nice to be able to assemble an algorithm from smaller blocks. 
- Expose clear interfaces.
Object-oriented code might be nice for production-level software, 
but makes it more complicated when you're trying to translate primitives you have into objects the library requires.
Especially when you're missing some parameters, which are not necessary for the function you need.
- Don't make asserts and checks other than the necessary ones for current function.
Some libraries are not usable in CTF environment because they will automatically fail detecting some "invalid" parameters, 
while in reality we know the parameters are wrong and we need a few more steps to solve the task.

## Installation

``` bash
sudo python setup.py install
```
## Usage example

``` python
from crypto_commons import generic

#xor a hex array with a string and print the result
a = [0x61, 0x53, 0x40, 0x47, 0x42, 0x59, 0x45, 0x5c, 0x08]
b = "123456789"

b = list(map(ord, b))

xored = list(map(chr, generic.xor(a, b)))

print(''.join(xored))

```