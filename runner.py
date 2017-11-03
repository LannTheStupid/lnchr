import re
from queue import Empty, Queue
from subprocess import Popen, PIPE, TimeoutExpired
from threading import Thread
from time import sleep

stringsize = 80
newline = b'\r'
POLL_TIMEOUT = 1


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


# noinspection SpellCheckingInspection
class Runner:

    def __init__(self, args):
        self.args = args
        self.poll_timeout = 1   # 1 second between checks
        self.outq = Queue()
        self.errq = Queue()

        self.dispatch_table = [
            (re.compile(r'(\w+) is hosting (\w+)'), self.handle_hosting),
            # (re.compile(r'(\w+) is running (\w+)'), self.redirect),
            # (re.compile(r'[Ee]rror (\d+)'), self.error),
            (re.compile(r'(.*)'), self.echo),
        ]

    def handle_hosting(self, ptrns):
        print(ptrns[1], 'is hosting', ptrns[2], 'terminating recording')
        self.proc.terminate()
        return 3

    def echo(self, the_string):
        print(the_string)
        return 0

    def dispatch(self, instr):
        for (regex, func) in self.dispatch_table:
            found = regex.search(instr)
            if found:
                return func(found.groups())
        print('It should have never happened')
        return -255

    def run(self):
        self.proc = Popen(self.args
                    , stdout=PIPE
                    , stderr=PIPE)
        tstdout = Thread(target=reader, args=(self.proc.stdout,self.outq,))
        tstdout.start()

        tstderr = Thread(target=cr_reader, args=(self.proc.stderr,self.errq,))
        tstderr.start()

        rv = 0
        while self.proc.poll() is None:
            try:
                outstr = self.outq.get_nowait()
                rv = self.dispatch(outstr)
            except Empty:
                pass

            try:
                errstr = self.errq.get_nowait()
                print(errstr, end='')
            except Empty:
                pass

            sleep(POLL_TIMEOUT)

        try:
            self.proc.communicate()
            self.proc.wait(timeout=POLL_TIMEOUT)
        except TimeoutExpired:
            print('streamlink did not terminate in time')
        finally:
            tstderr.join()
            tstdout.join()

        return rv