#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
from sudoku import Sudoku
import argparse

def testfiles(options):
    if options.header:
        print('mult','add','vfm','fvm','fvm_skip','vfm_skip','iterations','result','time', sep=',', flush=True)
    sudoku = Sudoku(verbose=False, progress=False, color=False, stats=True, setformula=options.setformula, scheduler=options.scheduler, skip=options.skip, size=options.size)
    for filename in options.files:
        with open(filename, 'r') as f:
            for line in f:
                t0 = time.time()
                res = sudoku.solve(line.strip())
                t1 = time.time()
                stats = res[0]
                outcome = res[1]
                t = t1-t0
                print(stats['mult'],stats['add'],stats['vfm'],stats['fvm'],stats['fvm_skip'],stats['vfm_skip'],stats['iterations'],outcome,t, sep=',', flush=True)

def option_parser(*args, **kwargs):
    parser = argparse.ArgumentParser()
    parser.add_argument('-s','--size', required=True, type=int, help='sub-grid size (3 for a 9x9 sudoku), if not set or set to 0, it is computed from the size of the first grid.')
    parser.add_argument('-S','--scheduler', choices=range(5), default=4, type=int, help='the method to use to solve the sudoku: 0 = naive scheduler, 1-4 = FVM-focused scheduler with FVM choosen by index (1), number of changes (2), sum of changes (3), number of changes and sum of changes (4, default)')
    naive = parser.add_argument_group('Naive Scheduler options', 'These options are only valid with the naive scheduler (0)')
    skip_grp = naive.add_mutually_exclusive_group()
    skip_grp.add_argument('--skip', action='store_true', dest='skip', default=True, help='skip useless computations (default)')
    skip_grp.add_argument('--noskip', action='store_false', dest='skip', default=True, help='do not skip useless computations')
    setformula_grp = naive.add_mutually_exclusive_group()
    setformula_grp.add_argument('--setformula', action='store_true', dest='setformula', default=True, help='use the set formula for faster FVM computations (default)')
    setformula_grp.add_argument('--nosetformula', action='store_false', dest='setformula', default=True, help='do not set formula')
    header_grp = parser.add_mutually_exclusive_group()
    header_grp.add_argument('-H', '--header', action='store_true', dest='header', default=True, help='add header (default)')
    header_grp.add_argument('--noheader', action='store_false', dest='header', default=True, help='do not add header')
    parser.add_argument('files', nargs='+', help='files containing the sudokus')
    options = parser.parse_args(*args, **kwargs)
    return options


if __name__ == '__main__':
    testfiles(option_parser())
