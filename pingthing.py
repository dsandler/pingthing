#!/usr/bin/env python3

import io
import re
import os
import sys
import time
import argparse
try:
    from colors import color
except:
    color = lambda s, **kwargs: s

from subprocess import Popen, PIPE

def ping(host, timeout=1):
    command = ['ping', '-c', '1']
    if os.uname().sysname == 'Darwin':
        command += ['-t', str(timeout)]
    else:
        command += ['-w', str(timeout)]
    command += [host]

    process = Popen(command, stdout=PIPE, stderr=PIPE)
    stdout = io.TextIOWrapper(process.stdout)
    stdout.readline() # skip first line
    # 64 bytes from 8.8.8.8: icmp_seq=1 ttl=118 time=15.8 ms
    result = stdout.readline()
    m = re.match(r'.* bytes from .*: icmp_seq=.* ttl=.* time=(.*) ms', result)
    if m:
        return float(m.group(1))
    else:
        return -1

def makebar(x):
    """https://alexwlchan.net/2018/05/ascii-bar-charts/"""
    bar_chunks, remainder = divmod(int(x * 8), 8)

    # First draw the full width chunks
    bar = '█' * bar_chunks

    # Then add the fractional part.  The Unicode code points for
    # block elements are (8/8), (7/8), (6/8), ... , so we need to
    # work backwards.
    if remainder > 0:
        bar += chr(ord('█') + (8 - remainder))

    # If the bar is empty, add a left one-eighth block
    bar = bar or  '▏'

    return bar

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--timeout', '-t',
        type=int, default=1, required=False, metavar='seconds',
        help='an integer for the accumulator')
    parser.add_argument('--output', '-o',
        default='log.txt', required=False, metavar='file.txt',
        help='file to append all ping times to')
    parser.add_argument('host', nargs=1,
        help='hostname or ip to ping')

    args = parser.parse_args()

    logfile = open(args.output, 'a')
    while True:
        ms = ping(args.host[0])
        bar = "%6.1f %s" % (ms, makebar(ms / 5))

        if ms < 0 or ms > 200:
          bar = color(bar, fg='red')
        elif ms > 100:
          bar = color(bar, fg='yellow')

        print("[%s] %s" % (time.strftime("%Y-%m-%d %X"), bar))
        logfile.write("%s, %f\n" % (
            time.strftime("%Y-%m-%d %X"),
            ms))
        logfile.flush()
        time.sleep(1)

#vim: sw=4 ts=4 et sts=4:
