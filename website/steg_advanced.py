import cv2
import numpy as np
import os

def to_bin(data):
    """Convert `data` to binary format as string"""
    if isinstance(data, str):
        return ''.join([ format(ord(i), "08b") for i in data ])
    elif isinstance(data, bytes):
        return ''.join([ format(i, "08b") for i in data ])
    elif isinstance(data, np.ndarray):
        return [ format(i, "08b") for i in data ]
    elif isinstance(data, int) or isinstance(data, np.uint8):
        return format(data, "08b")
    else:
        raise TypeError("Type not supported.")
    
def encode_img(image_name, secret_data, lth_bit=8, s_bit=1):
    # read the image
    image = cv2.imread(image_name)
    # maximum bytes to encode
    n_bytes = image.shape[0] * image.shape[1] * 3 // 8
    print("[*] Maximum bytes to encode:", n_bytes)
    print("[*] Data size:", len(secret_data))
    if len(secret_data) > n_bytes:
        raise ValueError(f"[!] Insufficient bytes ({len(secret_data)}), need bigger image or less data.")
    print("[*] Encoding data...")
    # add stopping criteria
    if isinstance(secret_data, str):
        secret_data += "====="
    elif isinstance(secret_data, bytes):
        secret_data += b"====="
    data_index = 0
    # convert data to binary
    binary_secret_data = to_bin(secret_data)
    # size of data to hide
    data_len = len(binary_secret_data)
    # for bit in range(1, n_bits+1):
    index = s_bit + lth_bit - 1
    for row in image:
        for pixel in row:
            # convert RGB values to binary format
            r, g, b = to_bin(pixel)
            # modify the least significant bit only if there is still data to store
            if data_index < data_len:
                    pixel[0] = int(r[:index] + binary_secret_data[data_index] + r[index + 1:], 2)
                    data_index += 1
            if data_index < data_len:
                pixel[1] = int(g[:index] + binary_secret_data[data_index] + g[index + 1:], 2)
                data_index += 1
            if data_index < data_len:
                pixel[2] = int(b[:index] + binary_secret_data[data_index] + b[index + 1:], 2)
                data_index += 1
            # if data is encoded, just break out of the loop
            if data_index >= data_len:
                break
    return image

def decode_file(image_name, in_bytes=False, lth_bit=7, s_bit=1):
    print("[+] Decoding...")
    # read the image
    image = cv2.imread(image_name)
    binary_data = ""

    index = s_bit + lth_bit - 1
    # for bit in range(1, n_bits+1):
    for row in image:
        for pixel in row:
            r, g, b = to_bin(pixel)
            binary_data += r[index]
            binary_data += g[index]
            binary_data += b[index]
    # split by 8-bits
    all_bytes = [ binary_data[i: i+8] for i in range(0, len(binary_data), 8) ]
    # convert from bits to characters
    if in_bytes:
        # if the data we'll decode is binary data, 
        # we initialize bytearray instead of string
        decoded_data = bytearray()
        for byte in all_bytes:
            # append the data after converting from binary
            decoded_data.append(int(byte, 2))
            if decoded_data[-5:] == b"=====":
                # exit out of the loop if we find the stopping criteria
                break
    else:
        decoded_data = ""
        for byte in all_bytes:
            decoded_data += chr(int(byte, 2))
            if decoded_data[-5:] == "=====":
                break
    return decoded_data[:-5]

