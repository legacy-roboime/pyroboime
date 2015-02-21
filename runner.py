from __future__ import print_function

import sys
from subprocess import Popen, PIPE
from threading import Thread
from time import sleep


profile = False
times = 20


def echo(text, proc='---main---'):
    if not profile:
        print('[%s] %s' % (str(proc), text))


class EchoFile(Thread):
    def __init__(self, file):
        super(EchoFile, self).__init__()
        self.file = file

    def echo(self, text):
        echo(text, self.ident)

    def run(self):
        self.echo('start')
        #for line in self.file:
        while not self.file.closed:
            self.echo('wait for read')
            line = self.file.readline()
            if not line:
                self.echo('read ended (eof)')
                break
            self.echo('read complete')
            self.echo('... <%s>' % line.rstrip())


def magic(proc):
    try:
        echo('open process')
        p = Popen(proc, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        echo('process opened')
    except:
        return


    t1 = EchoFile(p.stdout)
    t2 = EchoFile(p.stderr)

    t1.start()
    t2.start()

    echo('threads started')

    for i in range(times):
        echo('write to stdin (%i)' % i)
        p.stdin.write('foo bar %i\n' % i)
        p.stdin.flush()
        echo('stdin flushed')
        sleep(0.01)

    p.send_signal(2)  # SIGINT
    try:
        echo('wait for process to exit')
        p.wait()
        echo('process exited with %i' % p.returncode)
    except KeyboardInterrupt:
        echo('\rCtrl-C pressed')
        p.terminate()
        #p.stdout.close()
        #p.stderr.close()
        p.wait()
        echo('process force exited with %i' % p.returncode)

    echo('joining threads')
    t1.join()
    t2.join()

    echo('threads joined')


if __name__ == '__main__':
    magic(['python', './ai.py'])
