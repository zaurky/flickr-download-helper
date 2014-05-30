#!/usr/bin/python

import os
import signal
from datetime import datetime, timedelta


command_line = 'ps -eo pid,lstart,cmd | grep py | grep -v grep' \
               ' | grep -v console | grep -v jabber'
fd = os.popen(command_line)


for line in [line.strip() for line in fd.readlines()]:
    a_line = line.split(' ')
    if '' in a_line:
        a_line.remove('')
    a_line.reverse()

    pid = a_line.pop()

    date = a_line[-5:-1]
    date = dict(zip(('year', 'time', 'day', 'month'), date))
    date = "%(year)s-%(month)s-%(day)s %(time)s" % date
    start = datetime.strptime(date, '%Y-%b-%d %H:%M:%S')
    delta = datetime.now() - start

    if delta.days >= 2:
        print "killing %s" % pid
        os.kill(int(pid), signal.SIGKILL)
        continue

    if 3600*24 * delta.days + delta.seconds > 7200:
        print "%s running for %ss" % (pid, 3600*24 * delta.days + delta.seconds)
