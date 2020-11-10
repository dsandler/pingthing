#!/usr/bin/env python3

import io
import re
import os
import sys
import time
try:
    from colors import color
except:
    color = lambda s, **kwargs: s

from subprocess import Popen, PIPE

def ping(host):

    command = ['ping', '-c', '1']
    if os.uname().sysname == 'Darwin':
        command += ['-t', '1']
    else:
        command += ['-w', '1']
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
    args = sys.argv[1:]
    if len(args) == 0 or args[0] in ('-h', '--help'):
        print("usage: %s <host>" % sys.argv[0])
        sys.exit(1)
    host = args[0]
    logfile = open('log.txt', 'a')
    while True:
        ms = ping(host)
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
            
        
