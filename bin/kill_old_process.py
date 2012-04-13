#!/usr/bin/python

import shlex, subprocess
command_line = 'ps -eo pid,start_time,cmd' # | grep py | grep -v grep'
args = shlex.split(command_line)
proc = subprocess.Popen(args,stdout=subprocess.PIPE)

from datetime import datetime, timedelta
def parse_date(date):
    if date.find(':') < 0: # only the date
        return datetime.strptime("%s%s" % (datetime.now().year, date), '%Y%b%d')
    today = datetime.now().strftime("%Y%m%d")
    return datetime.strptime("%s %s" % (today, date), '%Y%m%d %H:%M')

for line in proc.stdout.readlines():
    if line.find('py') < 0:
        continue

    line = line.strip()
    a_line = line.split(' ')
    a_line.reverse()

    pid = a_line.pop()
    date = parse_date(a_line.pop())
    a_line.reverse()
    line = ' '.join(a_line)

    delta = date - datetime.now()

    if delta < timedelta(hours=-2):
        print line

