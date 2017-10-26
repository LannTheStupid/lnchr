from subprocess import Popen, PIPE
from threading import Thread
from queue import Queue
import os

stringsize = 80
newline = b'\r'

def my_read_line(in_stream):
    buf = b""
    while True:
        while newline in buf:
            pos = buf.index(newline)
            yield buf[:pos]
            buf = buf[pos + len(newline):]
            print('pos = ', pos)
        chunk = in_stream.read(stringsize)
#        print('buf = ', buf, 'chunk = ', chunk)
        print()
        if not chunk:
            yield buf
            break
        buf += chunk


def cr_reader(pipe, q):
    for line in my_read_line(pipe):
        q.put(line)


def reader(pipe, q):
    for line in pipe:
        q.put(line)



class Runner:

    def __init__(self, args):
        self.args = args
        self.poll_timeout = 1   # 1 second between checks
        self.outq = Queue()
        self.errq = Queue()


    def run(self):
        proc = Popen(self.args
                    , stdout=PIPE
                    , stderr=PIPE)
        tstdout = Thread(target=reader, args=(proc.stdout,self.outq,))
        tstdout.start()

        tstderr = Thread(target=cr_reader, args=(proc.stderr,self.errq,))
        tstderr.start()

