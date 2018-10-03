def encode_bytes(byte_data, separator=""):
    return separator.join(["{:02X}".format(byte) for byte in byte_data])

