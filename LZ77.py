"""
    Usage: in terminal type "python LZ77.py arg(1) arg(2)" where arg(1) is the text file and arg(2) is the noise intesity
"""



import math
import sys
from sys import argv
import os
import random
from typing import AnyStr
import base64
import json
import collections
import re
import numpy as np


def compress(data: AnyStr) -> bytes:
    """
    Applies lz algorithm to compress a text
    :param data: Take input a text
    :return: bits == A string with the compessed file in binary form
            listofbits == A list with all codeword in binary form
    """
    if isinstance(data, str):
        data = data.encode()
    keys: dict = ASCII_TO_INT.copy()
    n_keys: int = 256
    compressed: list = []
    start: int = 0
    n_data: int = len(data)+1
    while True:
        if n_keys >= 512:
            keys = ASCII_TO_INT.copy()
            n_keys = 256
        for i in range(1, n_data-start):
            w: bytes = data[start:start+i]
            if w not in keys:
                compressed.append(keys[w[:-1]])
                keys[w] = n_keys
                start += i-1
                n_keys += 1
                break
        else:
            compressed.append(keys[w])
            break
    bits: str = ' '.join(format(i, 'b') for i in compressed)
    listofbits = (bits.split(" "))
    return bits, listofbits


def hamming_encode(lista, noise):
    """
        Applies the hamming code to encode a list of binary form codewords.
    :param noise:
    :param lista: Takes input a list of compressed codeword in binary form
    :return: A string with all the encoded words in binary form
    """
    encoded_words = []
    index = 0
    noise = noise
    BitErrors = 0
    added_bits = 0
    for i in lista:
        data = list(i)

        data.reverse()
        c, ch, j, r, h = 0, 0, 0, 0, []

        while (len(i)+r+1) > (pow(2, r)):
            r = r+1
            added_bits += 1

        for i in range(0, (r+len(data))):
            p = (2**c)

            if p == (i+1):
                h.append(0)
                c = c+1

            else:
                h.append(int(data[j]))
                j = j+1

        for parity in range(0, (len(h))):
            ph = (2**ch)
            if ph == (parity+1):
                startIndex = ph-1
                i = startIndex
                toXor = []

                while i < len(h):
                    block = h[i:i+ph]
                    toXor.extend(block)
                    i += 2*ph

                for z in range(1, len(toXor)):
                    h[startIndex] = h[startIndex] ^ toXor[z]
                ch += 1

        h.reverse()

        # print('Hamming code for ' + str(index) + " ", end="")
        ham_code = int(''.join(map(str, h)))
        # print(added_bits)
        # print(ham_code)
        arr, count = add_noise(str(ham_code), noise)
        # fix_byte_string(arr, ham_code)
        BitErrors += count
        encoded_words.append(ham_code)
        index += 1

    # for i in encoded_words:
    #     array, count = add_noise(i, noise)
    #     fixedBit += count
    encoded_string: str = ' '.join(str(x) for x in encoded_words)
    # print(BitErrors)
    return encoded_string, BitErrors, added_bits


def add_noise(string, noise):
    """Adds noise to transmissions"""
    arr = str_to_arr(string)
    count = 0
    r = 0
    step = random.randint(0, 5)
    for i in range(len(arr)):
        if r < int(noise):
            arr[i] = (arr[i] + 1) % 2
            count += 1
            r += step
    return arr_to_str(arr), count


# def fix_byte_string(noisy, normal):
#
#     return fixed


def str_to_arr(s):
    """Converts binary string to numpy array"""
    if not re.fullmatch(r'(0|1)*', s):
        raise ValueError('Input must be in binary.')
    return np.array([int(d) for d in s], dtype=np.uint)


def arr_to_str(arr):
    """Converts numpy array to string"""
    return re.sub(r'\[|\]|\s+', '', np.array_str(arr))


def json_response(noise, string, start_s, start_e, end_s, end_e, added, errors):
    code_string = '{{"Algorithm Name": "Lempel-Ziv 77", "Code Style": "Cyclic Code","Noise Intensity": "{0}","Encoded String": "{1}", "Start Size": "{2}", "Start Entropy": "{3}", "End size": "{4}","End Entropy": "{5}","Added Bits": "{6}","Error Bits": "{7}"}}'.format(noise, string, start_s, start_e, end_s, end_e, added, errors)

    # pretty print
    pretty_data = json.loads(code_string)
    print(json.dumps(pretty_data, indent=4))


def find_entropy(data):
    e = 0
    counter = collections.Counter(data)
    le = len(data)
    for count in counter.values():
        # count is always > 0
        p_x = count / le
        e += - p_x * math.log2(p_x)

    return e


if __name__ == '__main__':
    name, InputFile, Noise = argv

    # print("Enter the parth of the ASCII text file"), InputFile
    # print("Enter the noise intesity"), Noise

    # InputFile = input("Enter the path of the ASCII text file")
    file = open(InputFile, "r")
    InputString = file.read()
    # Noise = input("Enter the noise intensity")



    # Pre-Code characteristics
    Start_size = os.path.getsize(InputFile)
    Start_entropy = find_entropy(InputString)

    ASCII_TO_INT: dict = {i.to_bytes(1, 'big'): i for i in range(256)}
    INT_TO_ASCII: dict = {i: b for b, i in ASCII_TO_INT.items()}

    compressed_string, listofbit = compress(InputString)

    # print the compressed string
    # print("compressed string: ", compressed_string)

    ham_enc, ErrorBits, AddedBits = hamming_encode(listofbit, Noise)

    # print the hamming code for each codeword
    # print("Compressed string encoded with hamming cycle code: ", ham_enc)
    base64_encoded = base64.b64encode(ham_enc.encode())
    base64_encoded_string = str(base64_encoded, "utf-8")

    # print the base64 encoded compressed string
    # print(base64_encoded_string)

    f1 = open("encodedfile.txt", "w")
    f1.write(base64_encoded_string)

    # Post-Code characteristics
    End_size = os.path.getsize("encodedfile.txt")
    End_entropy = find_entropy(base64_encoded_string)

    json_response(Noise, base64_encoded_string, Start_size, Start_entropy, End_size, End_entropy, AddedBits, ErrorBits)
