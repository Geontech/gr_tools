#!/usr/bin/env python
"""Python module to help debug

This module allows user to connect to an IP:PORT to send
either a datagram or setup a TCP connection to send a
message.
"""
import socket
import numpy as np

def send_udp(message=100, ip="127.0.0.1", port=52001):
    """Send message by UDP

    Parameters
    ----------
    message : int or list of bytes
        If int, specifies number of random bytes to transmit
        If list of bytes, send that as message.

    ip : str
        The internet address to send

    port : int
        The port to send
    """
    # setup a message
    if isinstance(message, int):
        # if message is int, random generate bytes
        message = np.random.randint(0, 256, message).astype(np.byte)

    # send datagram
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message, (ip, port))


def send_tcp(message=1000, ip='127.0.0.1', port=52001):
    """Send message by TCP

    Parameters
    ----------
    message : int or list of bytes
        If int, specifies number of random bytes to transmit
        If list of bytes, send that as message.

    ip : str
        The internet address to send

    port : int
        The port to send
    """
    if isinstance(message, int):
        # if message is int, random generate bytes
        message = np.random.randint(0, 256, message).astype(np.byte)
    else:
        pass # expecting the list of bytes

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #sock.connect(server_address)
    sock = socket.create_connection((ip, port))

    try:
        sock.sendall(message)
    finally:
        sock.close()

if __name__ == "__main__":
    # ----------------------------  setup parser  ---------------------------
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("mode", default="UDP", help="UDP or TCP")
    parser.add_argument("--ip", default="localhost", help="Internet address")
    parser.add_argument("--port", default=52001, type=int,
        help="Port to send towards")
    parser.add_argument("--message", default="", help="message to send")
    parser.add_argument("--num_bytes", default=0, type=int,
        help="Specify number of random bytes")
    args = parser.parse_args()

    # -------------------------  process arguments  -------------------------
    if args.num_bytes > 0:
        # quick means to use random bytes of a given length
        msg = args.num_bytes
    elif args.message != "":
        # convert a string message from command line
        msg = np.array(args.message).astype(np.byte)

    # --------------------------  send the message  -------------------------
    if args.mode == "UDP":
        send_udp(msg, args.ip, args.port)
    elif args.mode == "TCP":
        send_tcp(msg, args.ip, args.port)
