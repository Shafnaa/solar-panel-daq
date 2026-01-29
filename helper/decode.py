import struct


def decode_float(registers):
    if len(registers) < 2:
        return 0.0
    raw = struct.pack(">HH", registers[0], registers[1])
    return struct.unpack(">f", raw)[0]
