import socket
import fcntl
import struct
import ipaddress
import re
import typing


def getsockinfo(host: str, port: int = None, protocol: int = socket.AF_UNSPEC) \
        -> typing.Tuple[int, int, int, str, typing.Tuple[typing.Any, ...]]:
    try:
        sockinfo = socket.getaddrinfo(host, port, protocol,
                                      socket.SOCK_STREAM, 0, socket.AI_PASSIVE)[0]

        return sockinfo
    except socket.gaierror as err:
        raise exception.CException(str(err))


def getsockaddr(host: str, port: int = None, protocol: int = socket.AF_UNSPEC) \
        -> typing.Tuple[typing.Any, ...]:
    sockaddr = getsockinfo(host, port, protocol)[4]
    return sockaddr


def gethostaddrbyname(hostname: str, protocol: int = socket.AF_UNSPEC) -> str:
    hostaddr = getsockaddr(hostname, None, protocol)[0]
    return hostaddr


def gethwaddr(ifname: str) -> str:
    bifname: bytes = ifname.encode()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,
                       struct.pack('256s', bifname[:15]))
    res = ''.join(['%02x:' % char for char in info[18:24]])[:-1]
    return res


def getipv4addr(ifname: str) -> str:
    bifname: bytes = ifname.encode()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    res = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915,
                                       struct.pack('256s', bifname[:15]))[20:24])
    return res


def ishwaddr(hwaddr: str) -> bool:
    return bool(re.match("[0-9a-f]{2}([:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$",
                         hwaddr.lower()))


def isipv4addr(ipaddr: str) -> bool:
    try:
        if type(ipaddress.ip_address(ipaddr)) == ipaddress.IPv4Address:
            return True
        else:
            return False
    except ValueError:
        return False


def isipv6addr(ipaddr: str) -> bool:
    try:
        ipaddr = ipaddr.split("%")[0]  # in case of ipv6 local-link
        # example fe80::a00:27ff:fe27:6d4%eth0
        if type(ipaddress.ip_address(ipaddr)) == ipaddress.IPv6Address:
            return True
        else:
            return False
    except ValueError:
        return False


def isipv4network(netaddr: str) -> bool:
    try:
        netaddr = netaddr.split("%")[0]  # in case of ipv6 local-link
        # local link CIDR structure : address-block/num_of_bytes%interface
        if isipv4addr(netaddr):
            return False
        elif type(ipaddress.ip_network(netaddr)) == ipaddress.IPv4Network:
            return True
        else:
            return False
    except ValueError:
        return False


def isipv6network(netaddr: str) -> bool:
    try:
        if isipv6addr(netaddr):
            return False
        elif type(ipaddress.ip_network(netaddr)) == ipaddress.IPv6Network:
            return True
        else:
            return False
    except ValueError:
        return False


def isipaddr(ipaddr: str) -> bool:
    if isipv4addr(ipaddr) or isipv6addr(ipaddr):
        return True
    return False


def isipnetwork(netaddr: str) -> bool:
    if isipv4network(netaddr) or isipv6network(netaddr):
        return True
    return False


def host2protocol(host: str) -> int:
    return getsockinfo(host, None)[0]


def gethostsfromnetwork(netaddr: str) -> typing.List[str]:
    return list(str(host) for host in ipaddress.ip_network(netaddr).hosts())
