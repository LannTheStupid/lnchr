import re
from queue import Empty, Queue
from subprocess import Popen, PIPE, TimeoutExpired
from threading import Thread
from time import sleep

stringsize = 80
newline = b'\r'
POLL_TIMEOUT = 1
EXIT_TIMEOUT = 60


def my_read_line(in_stream):
    buf = b""
    chunk = b""
    pos = 0
    while True:
        while newline in buf:
            pos = buf.index(newline)
            yield buf[:pos]
            buf = buf[pos + len(newline):]
#            print('pos = ', pos)
        chunk = in_stream.read(stringsize)
#        print('buf = ', buf, 'chunk = ', chunk)
        if not chunk:
            yield buf
            break
        buf += chunk


def cr_reader(pipe, q, sq):
    for line in my_read_line(pipe):
        q.put(line)
        try:
            item = sq.get_nowait()
            print('Got', item, 'from the signal queue in the stdout reader')
            break
        except Empty:
            pass


def reader(pipe, q, sq):
    for line in pipe:
        q.put(line)
        try:
            item = sq.get_nowait()
            print('Got', item, 'from the signal queue in the stderr reader')
            break
        except Empty:
            pass


# noinspection SpellCheckingInspection
class Runner:

    def __init__(self, args):
        self.args = args
        self.poll_timeout = 1   # 1 second between checks
        self.outq = Queue()
        self.errq = Queue()
        self.signal = Queue()

        self.dispatch_table = [
            # (re.compile(r'(\w+) is hosting (\w+)'), self.handle_hosting),
            # (re.compile(r'(\w+) is running (\w+)'), self.redirect),
            # (re.compile(r'[Ee]rror (\d+)'), self.error),
            (re.compile(r'(.*)'), self.gulp),
        ]

    def handle_hosting(self, ptrns):
        print(ptrns[0], 'is hosting', ptrns[1], '. Recording terminated')
        self.proc.terminate()
        return 3

    def echo(self, the_string):
        print(the_string[0])
        return 0

    def gulp(self, the_string):
        pass
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
                    , stderr=PIPE
                    , bufsize=5*stringsize)
        tstdout = Thread(target=reader, args=(self.proc.stdout,self.outq,self.signal,))
        tstdout.start()

        tstderr = Thread(target=cr_reader, args=(self.proc.stderr,self.errq,self.signal,))
        tstderr.start()

        rv = 0
        while self.proc.poll() is None:
            try:
                outstr = self.outq.get_nowait()
                rv = self.dispatch(outstr.decode())
            except Empty:
                pass

            try:
                errstr = self.errq.get_nowait()
                print(errstr)
                # sys.stdout.flush()
            except Empty:
                pass

            sleep(POLL_TIMEOUT)

        try:
            self.signal.put('Done')
            self.signal.put('Done')
            tstderr.join(POLL_TIMEOUT)
            tstdout.join(POLL_TIMEOUT)
            tstderr.join()
            tstdout.join()
            print('Waiting for streamlink to terminate in', EXIT_TIMEOUT, 's')
            self.proc.communicate(timeout=EXIT_TIMEOUT)
            self.proc.wait(timeout=EXIT_TIMEOUT)
        except TimeoutExpired:
            print('streamlink did not terminate in time')

        return rv