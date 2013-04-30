# -*- coding: utf-8 -*-

# Copyright © 2007–2009 Robert Niederreiter, Jens Klein, Ben Finney
# Copyright © 2003 Clark Evans
# Copyright © 2002 Noah Spurrier
# Copyright © 2001 Jürgen Hermann
#
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the Python Software Foundation License, version 2 or
# later as published by the Python Software Foundation.
# No warranty expressed or implied. See the file LICENSE.PSF-2 for details.

import os
import sys
import time
import logging

from signal import SIGTERM

class Daemon(object):
    """Class Daemon is used to run any routine in the background on unix
    environments as daemon.
    
    There are several things to consider:
    
    * The instance object given to the constructor MUST provide a ``run()``
      function with represents the main routine of the deamon
    
    * The instance object MUST provide global file descriptors for
      (and named as):
        -stdin
        -stdout
        -stderr
    
    * The instance object MUST provide a global (and named as) pidfile.
    """

    UMASK = 0
    WORKDIR = "."
    instance = None
    startmsg = 'started with pid %s'

    def __init__(self, instance, logger_name):
        self.instance = instance
        self.logger_name = logger_name
        self.startstop()
        instance.run()

    def deamonize(self):
        """Fork the process into the background.
        """
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, e:
            msg = "fork #1 failed: (%d) %s\n" % (e.errno, e.strerror)
            log.debug(msg)
            sys.exit(1)

        os.chdir(self.WORKDIR)
        os.umask(self.UMASK)
        os.setsid()

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, e:
            msg = "fork #2 failed: (%d) %s\n" % (e.errno, e.strerror)
            log.debug(msg)
            sys.exit(1)

        pid = str(os.getpid())

        class ErrorWriter(object):
            def write(self, msg):
                log = logging.getLogger(self.logger_name)
                log.error(msg)

        sys.stderr.flush()
        sys.stderr = ErrorWriter()

        if self.instance.pidfile:
            file(self.instance.pidfile, 'w+').write("%s\n" % pid)

    def startstop(self):
        log = logging.getLogger(self.logger_name)
        """Start/stop/restart behaviour.
        """
        if len(sys.argv) > 1:
            action = sys.argv[1]
            try:
                pf = file(self.instance.pidfile, 'r')
                pid = int(pf.read().strip())
                pf.close()
            except IOError:
                pid = None
            if 'stop' == action or 'restart' == action:
                if not pid:
                    mess = "Could not stop, pid file '%s' missing.\n"
                    log.debug(mess % self.instance.pidfile)
                    sys.exit(1)
                try:
                    while 1:
                        os.kill(pid, SIGTERM)
                        time.sleep(1)
                except OSError, err:
                    err = str(err)
                    if err.find("No such process") > 0:
                        os.remove(self.instance.pidfile)
                        if 'stop' == action:
                            sys.exit(0)
                        action = 'start'
                        pid = None
                    else:
                        print str(err)
                        sys.exit(1)
            if 'start' == action:
                if pid:
                    mess = "Start aborded since pid file '%s' exists.\n"
                    log.debug(mess % self.instance.pidfile)
                    print(mess % self.instance.pidfile)
                    sys.exit(1)
                self.deamonize()
                return
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)

