#!/usr/bin/python
import gevent, gevent.server, gevent.socket
import os,sys
from telnetsrvlib.green import TelnetHandler, command
import logging
import argparse
from sudoku import main as Sudoku
from multiprocessing import Process

logging.getLogger('').setLevel(logging.DEBUG)

class WriteFile():
    def __init__(self, write):
        self.write = write

class SudokuTelnetHandler(TelnetHandler):
    # -- Override items to customize the server --
    WELCOME = 'Welcome on sudoku.cat sudoku solver. Type \'solve -h\' for help.'
    PROMPT = "> "
    
    # -- Custom Commands --
    @command('solve')
    def command_solve(self, params):
        '''
        Solve sudokus
        Solve sudokus. Type 'solve -h' for more informations.
        '''
        out = WriteFile(self.write)
        params.append('--nosetformula')
        params.append('--ascii')
        defaults = {'color': True, 'progress': True, 'verbose': True, 'stats': True, 'scheduler': 3}
        p = Process(target=Sudoku, args=(params,), kwargs={'stdout': out, 'stderr': out, 'prog': "solve", 'defaults': defaults})
        try:
            p.start()
            while p.is_alive():
                c = self.getc(block=False)
                while c != '':
                    if  c == chr(3):
                        self.write('\n^C ABORT\n')
                        p.terminate()
                    c = self.getc(block=False)
                gevent.sleep(1)
        except:
            pass
        finally:
            p.terminate()
            p.join()


if __name__ == '__main__':
    if os.environ.get('LISTEN_PID', None) == str(os.getpid()):
        sfd = gevent.socket.fromfd(3, gevent.socket.AF_INET6, gevent.socket.SOCK_STREAM)
        server = gevent.server.StreamServer(sfd, SudokuTelnetHandler.streamserver_handle)
    else:
        parser = argparse.ArgumentParser( description='Run a telnet server.')
        parser.add_argument( '--bind', '-b', metavar="ADDR", type=str, default='', help="The address on which to listen on." )
        parser.add_argument( 'port', metavar="PORT", type=int, help="The port on which to listen on." )
        console_args = parser.parse_args()
        server = gevent.server.StreamServer((console_args.bind, console_args.port), SudokuTelnetHandler.streamserver_handle)
        logging.info("Starting server at port %d.  (Ctrl-C to stop)" % (console_args.port) )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("Server shut down.")
