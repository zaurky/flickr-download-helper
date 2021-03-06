#!/usr/bin/python

from jabberbot import JabberBot, botcmd
import datetime
import threading
import time
import sys, time
import re
import os
import signal
import yaml

from flickr_download_helper.config import OptConfigReader, OPT

class LogJabberBot(JabberBot):
    thread_killed = False
    line = {}
    last_log = None
    log_level = 1
    possible_levels = ('0','1','2','3','4')
    display_date = False
    internal = {}
    _pause = False
    _start_at = None

    def __init__(self, jid, password, to_user, res = None):
        super(LogJabberBot, self).__init__(jid, password, res)

        self.config = OptConfigReader()
        self.config.setup()

        self._to_user = to_user
        self.downloads_file = OPT.downloads_file
        self.last_log_file = OPT.jabber_last

        self.day = datetime.datetime.now().strftime('%Y%m%d')

        if self.last_log_file is None:
            self._log('you must specify jabber_last in the conf file')
            sys.exit(2)

        self._file = open(self.downloads_file, 'rb')
        if os.path.exists(self.last_log_file):
            self._log('getting last log date from %s'%self.last_log_file)
            f = open(self.last_log_file, 'rb')
            l = f.readlines()
            f.close()
            if len(l) > 0:
                self._log('#%s#'%l[-1].strip())
                self._start_at = datetime.datetime.strptime(l[-1].strip(), '%Y-%m-%d %H:%M:%S')

    def idle_proc( self):
        if not len(self.line):
            return

        if self._pause:
            self._log('I am in pause')
            return False

        # copy the message queue, then empty it
        messages = self.line
        self.line = {}

        sorted = messages.keys()
        sorted.sort()
        for timestamp in sorted:
            message, level = messages[timestamp]
            self.last_log = timestamp
            if level > self.log_level:
                if self.display_date:
                    message = "%s %s"%(
                        timestamp.strftime('%m%d %H:%M'),
                        message
                    )
                self._log('sending "%s".' % (message))
                self.send(self._to_user, message)
                time.sleep(1)
            else:
                self._log('not sending "%s" (ll %s)'%(message, level))

    def can_send(self, m):
        if m is not None:
            if self._start_at != None:
                if self._start_at > datetime.datetime.strptime(m.group(1), '%Y-%m-%d %H:%M:%S'):
                    return False
            return True
        return False

    def thread_proc( self):
        if datetime.datetime.now().strftime('%Y%m%d') != self.day:
            # change day : reinits
            self.internal = {}
            self._file.close()
            self._file = open(self.downloads_file, 'rb')

        try:
            while not self.thread_killed:
                lines = self._file.readlines()
                if lines:
                    for line in lines:
                        timestamp = datetime.datetime.now()
                        # get downloads
                        m = re.search('(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\.\d+ (\d+) (.+)', line)
                        if self.can_send(m):
                            if m.group(3) not in self.internal:
                                self.internal[m.group(3)] = 0
                            self.internal[m.group(3)] += int(m.group(2))
                            self.line[timestamp] = ("%s %s"%(m.group(2), m.group(3)), 2)

                        # get video
                        m = re.search('(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\.\d+ video (.+)', line)
                        if self.can_send(m):
                            self.line[timestamp] = ("video : %s"%(m.group(2)), 3)

                time.sleep(1)
            self.finish()
        except Exception, e:
            self._log(e)
            return

    def finish(self):
        self._log("thread killed")
        if self.last_log is not None:
            self._log("writing last date in %s"%self.last_log_file)
            # put self.last_log somewhere I can read it at next start!
            f = open(self.last_log_file, 'w')
            f.write(self.last_log.strftime('%Y-%m-%d %H:%M:%S'))
            f.close()
        self._log("closing log file")
        self._file.close()
        sys.exit()

    def _log(self, s):
        print self.__class__.__name__, datetime.datetime.now().strftime('%H:%M'), ':', s

    @botcmd
    def level(self, mess, args = ''):
        level = str(args)
        if args == '':
            self._log('log level = %s'%(level))
            return
        if level not in self.possible_levels:
            self._log('log level %s invalid'%(level))
            self.send(self._to_user, 'log level %s invalid'%(level))
            self.send(self._to_user, 'should be one of %s'%', '.join(self.possible_levels))
            return
        self._log('setting log level to %s'%(level))
        self.log_level = level

    @botcmd
    def l(self, mess, args):
        return self.level(mess, args)

    @botcmd
    def reload(self, mess='', args=''):
        self._log('reload was asked')
        self._file.close()
        self._file = open(self.downloads_file, 'rb')

    @botcmd
    def r(self, mess, args):
        return self.reload(mess, args)

    @botcmd
    def quit(self, mess, args):
        self.send(self._to_user, 'quit asked')
        self.finish()

    @botcmd
    def q(self, mess, args):
        self.finish()

    @botcmd
    def pause(self, mess, args):
        self.send(self._to_user, 'pausing')
        self._log('pausing')
        self._pause = True

    @botcmd
    def wake(self, mess, args):
        self.send(self._to_user, 'waking up')
        self._log('waking up')
        self.reload()
        self._pause = False

    @botcmd
    def date(self, mess, args):
        self.send(self._to_user, 'adding date')
        self.display_date = True
    @botcmd
    def nodate(self, mess, args):
        self.send(self._to_user, 'removing date')
        self.display_date = False

    @botcmd
    def howmuch(self, mess, args = ''):
        contact = args
        if contact == '':
            self.send(self._to_user, 'you must give me a contact name')
            return
        if contact not in self.internal:
            self.send(self._to_user, 'contact "%s" is not in internals'%contact)
            return
        self.send(self._to_user, 'there is %d files for %s today'%(self.internal[contact], contact))

    @botcmd
    def status(self, mess, args):
        self.send(self._to_user, 'display date %s'%self.display_date)
        self.send(self._to_user, 'pause %s'%self._pause)
        self.send(self._to_user, 'log level %s'%self.log_level)

    @botcmd
    def kill(self, mess, args):
        self._log('will kill %s' % args)
        os.kill(args, signal.SIGKILL)

    @botcmd
    def pgrep(self, mess, args):
        command_line = 'ps -eo pid,lstart,cmd | grep py | grep -v grep | grep -v jabber'
        for line in os.popen(command_line).readlines():
            self.send(self._to_user, line.strip())
            self.send(self._to_user, '')


f = open('/etc/fdh/jabber.yaml')
conf = yaml.load(f)

write_to = conf['write_to']
username = conf['write_from']['email']
password = conf['write_from']['password']

def serve(username, password, write_to):
    bot = LogJabberBot(username, password, write_to)
    th = threading.Thread(target = bot.thread_proc)
    try:
        bot.serve_forever(connect_callback = lambda: th.start())
        bot.thread_killed = True
        return False
    except IOError, e:
        bot.thread_killed = True
        bot.finish()
        return True

while serve(username, password, write_to): pass
