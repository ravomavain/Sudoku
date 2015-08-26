#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import time
import numpy as np
from factorgraph import FactorGraph, Operations, NumpyOperations, NumpyOperationsStats, Side
from itertools import permutations, combinations
from pprint import pprint
from functools import reduce
import argparse

class SudokuOperations(Operations):
    def __init__(self, size=1):
        self.size = size
    def zero(self):
        return np.zeros(self.size, dtype=bool)
    def one(self,i=-1):
        if i == -1:
            return np.ones(self.size, dtype=bool)
        return np.eye(1, self.size, i, dtype=bool)[0]
    def dist(self, a, b):
        return np.count_nonzero(a!=b)
    def factor_message(self, incoming_values):
        # incoming_values is set of possible value for other variables node
        d = self.sum(incoming_values, self.zero())
        if np.count_nonzero(d) == self.size-1:
            return ~d
        m = self.one()
        for n in range(1,self.size-1):
            for J in combinations(incoming_values,n):  # subsets of n messages.
                A = self.sum(J, self.zero())
                if np.count_nonzero(A) == n:
                    m = m*(~A)
                if np.count_nonzero(m) == 1:
                    return m
        return m
    def disp(self, a):
        res = set()
        for i, v in enumerate(a, start=1):
            if v > 0:
                res.add(i)
        if len(res) == 0:
            return 'ø'
        if len(res) == 1:
            return str(res.pop())
        return str(res)

class SudokuOperationsStats(SudokuOperations):
    def mult(self, a, b):
        self.stats['mult'] += 1
        return a*b
    def add(self, a, b):
        self.stats['add'] += 1
        return a+b

class Sudoku:
    def __init__(self, verbose=False, progress=False, color=False, setformula=True, stats=False, scheduler=4, skip=True, size=3, stdout=sys.stdout, utf8=True):
        self.verbose = verbose
        self.progress = progress
        self.color = color
        self.setformula = setformula
        self.stats = stats
        self.scheduler = scheduler
        self.skip = skip
        self.stdout = stdout
        self.utf8 = utf8
        self.p = size
        self.q = self.p*self.p
        if not self.setformula and self.scheduler == 0:
            if self.stats:
                self.op = NumpyOperationsStats(self.q)
            else:
                self.op = NumpyOperations(self.q)
        else:
            if self.stats:
                self.op = SudokuOperationsStats(self.q)
            else:
                self.op = SudokuOperations(self.q)
        self.counter = 0
        self.graph = FactorGraph(self.q*self.q, 3*self.q, self.edge, self.op, self.print_sudoku if self.verbose and self.progress else lambda *args: None)
    
    def solve(self, s):
        self.graph.initial_values(np.array([self.op.one(int(c,base=36)-1) for c in s], dtype=bool))
        self.firstprint = True
        if self.verbose:
            print("Initial values:", file=self.stdout)
            self.print_sudoku(self.graph, False)
            print("Solving:", file=self.stdout)
        result = self.graph.solve(method=self.scheduler, doskip=self.skip, doprogress=self.progress, dostats=self.stats)
        solvable = True
        if any([np.count_nonzero(r) == 0 for r in result]):
            solvable = False
        elif any([np.count_nonzero(r) > 1 for r in result]):
            solvable = None
        if self.verbose:
            if not self.firstprint:
                print('\033['+str((self.p+1)*self.q+1)+'A',end='', file=self.stdout)
            if solvable == False:
                print("There's no solution:", file=self.stdout)
            elif solvable == None:
                print("We can't find a unique solution:", file=self.stdout)
            else:
                print("We found a solution:", file=self.stdout)
            self.print_sudoku(self.graph, False)
        stats = self.graph.get_stats()
        return (stats, solvable, result)
    
    def edge(self,i,j):
        if j < self.q:      # Row constraints
            return (i//self.q == j)
        elif j < 2*self.q:  # Column constraints
            return (i%self.q == j%self.q)
        else:               # Sub-grid constraints
            return (((i//self.q)//self.p)*self.p + ((i%self.q)//self.p) == j%self.q)
    
    def print_sudoku(self, graph, erase=True):
        digits = "123456789abcdefghijklmnopqrstuvwxyz"
        out = []
        for i1 in range(self.p):
            for i2 in range(self.p):
                for ii in range(self.p):
                    out.append(list(
                        '┃'.join([
                            '│'.join(' '*self.p for col in range(self.p))
                            for col in range(self.p)
                        ])
                    ))
                out.append(list(
                    '╂'.join([
                        '┼'.join('─'*self.p for col in range(self.p))
                        for col in range(self.p)
                    ])
                ))
            out.pop()
            out.append(list(
                '╋'.join([
                    '┿'.join('━'*self.p for col in range(self.p))
                    for col in range(self.p)
                ])
            ))
        out.pop()
        for i in range(self.q):
            for j in range(self.q):
                m = self.graph.PseudoPosterior[i*self.q+j]
                if np.count_nonzero(m) == 1:
                    a = i*(self.p+1)+(self.p//2)
                    b = j*(self.p+1)+(self.p//2)
                    for n in range(self.q):
                        if m[n]:
                            if self.color:
                                out[a][b] = '\033[32m'+digits[n]+'\033[0m'
                            else:
                                out[a][b] = digits[n]
                elif np.count_nonzero(m) > 0:
                    for n in range(self.q):
                        if m[n]:
                            a = i*(self.p+1)+(n//self.p)
                            b = j*(self.p+1)+(n%self.p)
                            out[a][b] = digits[n]
        
        if erase:
            if self.firstprint:
                self.firstprint = False
            else:
                print('\033['+str((self.p+1)*self.q)+'A',end='', file=self.stdout)
        out = '\n'.join([''.join(o) for o in out])
        if not self.utf8:
            out = out.replace('╂','+').replace('┼','+').replace('╋','+').replace('┿','+').replace('┃','|').replace('│','|').replace('─','-').replace('━','-')
        print(out, file=self.stdout)
        print(file=self.stdout)

class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        self.stderr = kwargs.pop('stderr', sys.stderr)
        self.stdout = kwargs.pop('stdout', sys.stdout)
        super(ArgumentParser, self).__init__(*args, **kwargs)
    def print_usage(self, file=None):
        if file is None:
            file = self.stdout
        self._print_message(self.format_usage(), file)
    def print_help(self, file=None):
        if file is None:
            file = self.stdout
        self._print_message(self.format_help(), file)
    def _print_message(self, message, file=None):
        if message:
            if file is None:
                file = self.stderr
            file.write(message)
    def exit(self, status=0, message=None):
        if message:
            self._print_message(message, self.stderr)
        sys.exit(status)
    def error(self, message):
        self.print_usage(self.stderr)
        args = {'prog': self.prog, 'message': message}
        self.exit(2, '%(prog)s: error: %(message)s\n' % args)


def option_parser(*args, **kwargs):
    stderr = kwargs.pop('stderr', sys.stderr)
    stdout = kwargs.pop('stdout', sys.stdout)
    prog = kwargs.pop('prog', sys.argv[0])
    defaults = kwargs.pop('defaults', None)
    parser = ArgumentParser(stdout=stdout, stderr=stderr, prog=prog, formatter_class=argparse.RawDescriptionHelpFormatter, epilog='Example: \n{} 000600710200400000000000300000010062500020000307000000000060800010000000000500000'.format(prog))
    parser.add_argument('-s','--size', default=0, type=int, help='sub-grid size (3 for a 9x9 sudoku), if not set or set to 0, it is computed from the size of the first grid.')
    parser.add_argument('-S','--scheduler', choices=range(5), default=3, type=int, help='the method to use to solve the sudoku: 0 = naive scheduler, 1-4 = FVM-focused scheduler with FVM choosen by index (1), number of changes (2), sum of changes (3), number of changes and sum of changes (4, default)')
    naive = parser.add_argument_group('Naive Scheduler options', 'These options are only valid with the naive scheduler (0)')
    skip_grp = naive.add_mutually_exclusive_group()
    skip_grp.add_argument('--skip', action='store_true', dest='skip', default=True, help='skip useless computations (default)')
    skip_grp.add_argument('--noskip', action='store_false', dest='skip', default=True, help='do not skip useless computations')
    setformula_grp = naive.add_mutually_exclusive_group()
    setformula_grp.add_argument('--setformula', action='store_true', dest='setformula', default=False, help='use the set formula for faster FVM computations (default)')
    setformula_grp.add_argument('--nosetformula', action='store_false', dest='setformula', default=False, help='do not set formula')
    
    progress_grp = parser.add_mutually_exclusive_group()
    progress_grp.add_argument('-p', '--progress', action='store_true', dest='progress', default=False, help='display progression (require an compatible terminal)')
    progress_grp.add_argument('--noprogress', action='store_false', dest='progress', default=False, help='do not display progression')
    color_grp = parser.add_mutually_exclusive_group()
    color_grp.add_argument('-c', '--color', action='store_true', dest='color', default=False, help='use colors (require an compatible terminal')
    color_grp.add_argument('--nocolor', action='store_false', dest='color', default=False, help='do not use colors')
    stats_grp = parser.add_mutually_exclusive_group()
    stats_grp.add_argument('--stats', action='store_true', dest='stats', default=False, help='produce statistics')
    stats_grp.add_argument('--nostats', action='store_false', dest='stats', default=False, help='do not produce statistics (default)')
    verbose_grp = parser.add_mutually_exclusive_group()
    verbose_grp.add_argument('-v', '--verbose', dest='verbose', default=True, action="store_true")
    verbose_grp.add_argument('-q', '--quiet', dest='verbose', default=True, action="store_false")
    utf8_grp = parser.add_mutually_exclusive_group()
    utf8_grp.add_argument('--utf8', action='store_true', dest='utf8', default=True, help='use UTF-8 chars')
    utf8_grp.add_argument('--ascii', action='store_false', dest='utf8', default=True, help='do not use UTF-8 chars')
    parser.add_argument('grid', nargs='+', help='a string reprsenting the numbers in the grid given in row order. A zero means an empty cell. All grid should have the same size which have to be a valid sudoku size.')
    if defaults:
        parser.set_defaults(**defaults)
    options = parser.parse_args(*args, **kwargs)
    if options.size == 0:
        options.size = int(pow(len(options.grid[0]),1/4))
    return options

def main(*args, **kwargs):
    stdout = kwargs.get('stdout', sys.stdout)
    options = option_parser(*args, **kwargs)
    sudoku = Sudoku(verbose=options.verbose, progress=options.progress, color=options.color, setformula=options.setformula, stats=options.stats, scheduler=options.scheduler, skip=options.skip, size=options.size, stdout=stdout, utf8=options.utf8)
    for g in options.grid:
        if options.stats:
            t0 = time.time()
        res = sudoku.solve(g)
        if options.stats:
            t1 = time.time()
        if options.verbose:
            if options.stats:
                print("Stats:",res[0],"Result:",res[1],"Time:",t1-t0,file=stdout)
        else:
            if options.stats:
                print(res[0],res[1],sep=', ',file=stdout)
            else:
                print(res[1])
            print(''.join([sudoku.op.disp(i) for i in res[2]]),file=stdout)
            
            
if __name__ == '__main__':
    main()
