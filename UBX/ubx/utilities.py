"""
Utilities for UBX sentences.
"""

from datetime import datetime
import sys
import socket


def mc_sender(mcast_if_ip, mcast_grp, mcast_port, message):
    this_function = 'mc_sender'
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        s.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(mcast_if_ip))
        s.sendto(message, (mcast_grp, mcast_port))
    except socket.error as e:
        print(f'Error {e} in UBX utilities, function {this_function}')
        exit(-1)


def ip_validator(IPv4):
    try:
        socket.inet_aton(IPv4)
    except socket.error:
        print(f'The IP address {IPv4} in the settings does not appear on this computer')
        exit(-1)


def udp_sender(MCAST_GRP, MCAST_PORT, message):

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
    sock.sendto(message, (MCAST_GRP, MCAST_PORT))


def path_name():
    # Operating system dependent stuff
    this_os = sys.platform
    if this_os == 'win32':
        return './logfiles/'
    elif this_os == 'linux':
        return '/home/pi/logfiles/'
    else:
        print(f'Unsupported OS: {this_os}')
        exit(0)


def log_file_name(extension):
    """
    Create a file name in the logfiles directory, based on current data and time
    Requires the computer to have an RTC or synched clock
    """

    now = datetime.now()
    log_file_name = '%0.4d%0.2d%0.2d-%0.2d%0.2d%0.2d' % \
                (now.year, now.month, now.day,
                 now.hour, now.minute, now.second)
    return log_file_name + extension


def ubx_crc(payload_for_crc,ubx_crc_a, ubx_crc_b):
    # Convert CRC bytes to INT
    ubx_crc_a_int = int.from_bytes(ubx_crc_a, "little")
    ubx_crc_b_int = int.from_bytes(ubx_crc_b, "little")

    # Go get the two CRCs
    crc_a = 0
    crc_b = 0

    for byte in payload_for_crc:
        crc_a += byte
        crc_a &= 0xFF
        crc_b += crc_a
        crc_b &= 0xFF

    # Now catch the error if there is one
    if ubx_crc_a_int != crc_a:
        print(f'CRC_A Error, {ubx_crc_a_int} not equal to {crc_a}')
        return False
    if ubx_crc_b_int != crc_b:
        print(f'CRC_B Error, {ubx_crc_b_int} not equal to {crc_b}')
        return False

    return True


def itow(iTOW_in_ms):
    """
    Time/date as an integer week number (TOW)
    and a time of week expressed in seconds.
    """
    # Convert from ms to seconds
    itow_total_seconds = iTOW_in_ms / 1000
    # Calcuate number of seconds in
    day = 24 * 60 * 60
    hour = 60 * 60
    minute = 60
    # The day will be
    itow_day = int(itow_total_seconds / day)
    itow_hour = int((itow_total_seconds - (itow_day * day)) / hour)
    itow_minute = int((itow_total_seconds - (itow_day * day) - (itow_hour * hour)) / minute)
    itow_seconds = int((itow_total_seconds - (itow_day * day) - (itow_hour * hour)) - (itow_minute * minute))
    return itow_day, itow_hour, itow_minute, itow_seconds


