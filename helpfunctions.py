# Primality Testing with the Rabin-Miller Algorithm
# http://inventwithpython.com/hacking (BSD Licensed)

import random
import hashlib
import secrets
import math
import sys
from dotenv import dotenv_values

sys.set_int_max_str_digits(10000000)

config = dotenv_values(".env")

HASH_TO_PRIME_LENGTH = int(config["HASH_TO_PRIME_LENGTH"])


def rabin_miller(num):
    # Returns True if num is a prime number.

    s = num - 1
    t = 0
    while s % 2 == 0:
        # keep halving s while it is even (and use t
        # to count how many times we halve s)
        s = s // 2
        t += 1

    for trials in range(5): # try to falsify num's primality 5 times
        a = random.randrange(2, num - 1)
        v = pow(a, s, num)
        if v != 1: # this test does not apply if v is 1.
            i = 0
            while v != (num - 1):
                if i == t - 1:
                    return False
                else:
                    i = i + 1
                    v = (v ** 2) % num
    return True


def is_prime(num):
    # Return True if num is a prime number. This function does a quicker
    # prime number check before calling rabin_miller().

    if (num < 2):
        return False # 0, 1, and negative numbers are not prime

    # About 1/3 of the time we can quickly determine if num is not prime
    # by dividing by the first few dozen prime numbers. This is quicker
    # than rabin_miller(), but unlike rabin_miller() is not guaranteed to
    # prove that a number is prime.
    lowPrimes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]

    if num in lowPrimes:
        return True

    # See if any of the low prime numbers can divide num
    for prime in lowPrimes:
        if (num % prime == 0):
            return False

    # If all else fails, call rabin_miller() to determine if num is a prime.
    return rabin_miller(num)


def generate_large_prime(num_of_bits):
    while True:
        num = secrets.randbelow(pow(2, num_of_bits))
        if is_prime(num):
            return num


def generate_two_large_distinct_primes(num_of_bits):
    p = generate_large_prime(num_of_bits)
    while True:
        q = generate_large_prime(num_of_bits)
        while q != p:
            return p, q


def hash_to_prime(x, num_of_bits=HASH_TO_PRIME_LENGTH, nonce=0):
    while True:
        num = hash_to_length(x + nonce, num_of_bits)
        if is_prime(num):
            return num, nonce
        nonce = nonce + 1


def hash_to_length(x, num_of_bits):
    pseudo_random_hex_string = ""
    num_of_blocks = math.ceil(num_of_bits / 256)
    for i in range(0, num_of_blocks):
        pseudo_random_hex_string += hashlib.sha256(str(x + i).encode()).hexdigest()

    if num_of_bits % 256 > 0:
        pseudo_random_hex_string = pseudo_random_hex_string[int((num_of_bits % 256)/4):]  # we do assume divisible by 4
    return int(pseudo_random_hex_string, 16)


def xgcd(b, a):
    x0, x1, y0, y1 = 1, 0, 0, 1
    while a != 0:
        q, b, a = b // a, a, b % a
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return b, x0, y0


def mul_inv(b, n):
    g, x, _ = xgcd(b, n)
    if g == 1:
        return x % n


def concat(*arg):
    res = ""
    for i in range(len(arg)):
        res += str(arg[i])
    return int(res)


def bezoute_coefficients(a, b):
    o = xgcd(a, b)
    return o[1], o[2]


def shamir_trick(pi1, pi2, x1, x2, n):
    # we omit the validity check of (x1^pi1 == x2^pi2) for performance reasons, assume caller validates

    # find a,b s.t. a*x + b*y = 1 (mod n)
    a, b = bezoute_coefficients(x1, x2)
    negative_is_a = a < 0
    if negative_is_a:
        positive_a = -a
        inverse_pi2 = mul_inv(pi2, n)
        power1 = pow(pi1, b, n)
        power2 = pow(inverse_pi2, positive_a, n)
    elif b < 0:
        positive_b = -b
        inverse_pi1 = mul_inv(pi1, n)
        power1 = pow(inverse_pi1, positive_b, n)
        power2 = pow(pi2, a, n)
    else:
        power1 = pow(pi1, b, n)
        power2 = pow(pi2, a, n)
    pi = power1 * power2
    return pi


# This is the fastest method available
def calculate_product(lst):
    r = 1
    for x in lst:
        r *= x
    return r

# ----------------------- The following are new help functions -----------------------

def write_list_to_file(elements, filename):
    """
    Writes a list of strings or integers to a text file, with each element separated by a newline.

    Args:
        elements (list): List of strings or integers to write.
        filename (str): Name of the output text file.

    Returns:
        None
    """
    with open(filename, 'w') as file:
        file.write('\n'.join(map(str, elements)))  # Join elements with newline separato

def write_two_d_array_to_file(two_d_array, filename):
    try:
        with open(filename, 'w') as file:
            for i, row in enumerate(two_d_array):
                # Join the elements in the row with commas
                row_str = ','.join(str(elem) for elem in row)
                file.write(row_str)
                if i < len(two_d_array) - 1:
                    file.write('\n')  # Add a newline after each row except the last one
    except Exception as e:
        print(f"Error writing to {filename}: {e}")

def extract_merkle_proof(proof_list):
    """
    Extracts the side (0 for left, 1 for right) and hash strings from a list of dictionaries representing a Merkle proof.

    Args:
        proof_list (list[dict]): List of dictionaries with 'left' or 'right' keys and SHA256 hash values.

    Returns:
        tuple: Two ordered lists (sides, hashes).
            - sides (list[int]): List of 0s and 1s indicating sibling position (0 = left, 1 = right).
            - hashes (list[str]): List of SHA256 hash strings.
    """
    sides = []
    hashes = []

    for proof in proof_list:
        if 'left' in proof:
            sides.append(0)
            hashes.append('0x' + proof['left'])
        elif 'right' in proof:
            sides.append(1)
            hashes.append('0x' + proof['right'])

    return sides, hashes

def hash_strings(strings):
    hashed_list = []
    for s in strings:
        # Calculate the SHA-256 hash of each string
        hashed_value = hashlib.sha256(s.encode()).hexdigest()
        hashed_list.append(hashed_value)
    return hashed_list


def create_random_list(size, bit_length):
    result = []
    for index in range(0, size):
        random_element = random.randint(1, pow(2, bit_length)-1)
        result.append(random_element)
    return result

def hash_integers(integers):
    """
    Hashes a list of decimal integers using SHA-256.

    Args:
        integers (list of int): List of decimal integers.

    Returns:
        list of str: List of SHA-256 hashes (in hexadecimal format).
    """
    hashed_list = []
    for num in integers:
        # Convert the integer to bytes (using variable-length bytes)
        num_bytes = num.to_bytes((num.bit_length() + 7) // 8, byteorder='big')

        # Create a SHA-256 hash object
        hash_obj = hashlib.sha256()
        hash_obj.update(num_bytes)

        # Get the hexadecimal digest
        hash_hex = hash_obj.hexdigest()
        hashed_list.append(hash_hex)

    return hashed_list

def make_even_size(hex_num):
    if len(hex_num) % 2 != 0:
        return '0x0' + hex_num[2:]
    else:
        return hex_num

def to_padded_num_str(num, length_in_bytes):
    length_in_hex_str = length_in_bytes * 2 + 2
    num_str = format(num, '#0' + str(length_in_hex_str) + 'x')
    return num_str
