import struct
import socket
import typing


def bytes2str(b: bytes)->str:
    return b.decode("utf-8")


def str2bytes(s: str)->bytes:
    return s.encode()


def bytes2hex(b: bytes)->str:
    return "0x" + b.hex()


def int2hex(i: int, bytesorder: str) -> str:
    return "0x" + struct.pack(bytesorder, i).hex()


def str2bytesnoencoding(msg: str)->bytes:
    byteset: typing.List[bytes] = [i.to_bytes(1, byteorder="little",
                                              signed=False) for i in range(256)]
    hexset: typing.List[str] = ["0", "1", "2", "3", "4", "5", "6", "7",
                                "8", "9", "a", "b", "c", "d", "e", "f"]
    bytemap: typing.Dict[str, bytes] = {}
    it = 0
    for c1 in hexset:
        for c2 in hexset:
            bytemap[c1 + c2] = byteset[it]
            it += 1
    bdata: bytes = b""
    i = 0
    while i < len(msg):
        if msg[i] == "\\" and (i + 3) < len(msg) and \
                msg[i + 1] == "x" and msg[i + 2].lower() in hexset and \
                msg[i + 3].lower() in hexset:
            bdata += bytemap[(msg[i + 2] + msg[i + 3]).lower()]
            i += 4
        else:
            bdata += msg[i].encode()
            i += 1
    return bdata


def getfreeport()->int:
    skt: socket.socket = socket.socket()
    skt.bind(("", 0))
    port: int = skt.getsockname()[1]
    skt.close()
    return port


def ip2hexbigendianv4(ip: str)->bytes:
    return struct.pack(">L", struct.unpack(">L",
                                           socket.inet_aton(ip))[0])


def port2hexbigendian(port: int)->bytes:
    if 0 >= port or 65535 < port:
        raise ValueError("incorrect port number " + str(port))
    return struct.pack(">H", port)


def uint2hexbigendian(num: int)->bytes:
    # unsigned int (32 bit) to hex code
    return struct.pack(">I", num)
