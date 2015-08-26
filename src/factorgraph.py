#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, abc
import numpy as np
from enum import Enum
from functools import reduce
from itertools import permutations, product, tee
from collections import Counter, defaultdict

class DefaultDict(defaultdict):
    def __missing__(self, key):
        if self.default_factory:
            dict.__setitem__(self, key, self.default_factory(key))
            return self[key]
        else:
            defaultdict.__missing__(self, key)

class Side(Enum):
    Variable, Factor = range(2)


def exclude(iterator, element):
    for i in iterator:
        if i != element:
            yield i

class Operations(object):
    __metaclass__ = abc.ABCMeta
    stats = Counter()
    
    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        pass
    @abc.abstractmethod
    def zero(self):
        return 0
    @abc.abstractmethod
    def one(self,i=-1):
        return 1
    @abc.abstractmethod
    def factor_message(self, incoming_values):
        return
    def dist(self, a, b):
        if a == b:
            return 0
        else:
            return 1
    def mult(self, a, b):
        return a*b
    def add(self, a, b):
        return a+b
    def prod(self, values=[], initial=None):
        return reduce(self.mult, values, initial)
    def sum(self, values=[], initial=None):
        return reduce(self.add, values, initial)
    def disp(self, a):
        return str(a)
    def set_stats(self, stats):
        self.stats = stats

class VectorOperations(Operations):
    def __init__(self, size=1, characteristic=lambda x,y: product(x, repeat=y)):
        self.size = size
        self.charac = characteristic
        self.iterators = [
            self.charac(exclude(range(self.size),d), self.size-1)
            for d in range(self.size)
        ]
    def zero(self):
        return [0 for x in range(self.size)]
    def one(self,i=-1):
        if i == -1:
            return [1 for x in range(self.size)]
        return [1 if x==i else 0 for x in range(self.size)]
    def mult(self, a, b):
        return [a[x]&b[x] for x in range(self.size)]
    def add(self, a, b):
        return [a[x]|b[x] for x in range(self.size)]
    def dist(self, a, b):
        d = 0
        for x in range(self.size):
            d += abs(a[x]-b[x])
        return d
    def get_iterator(self, d):
        it1, it2 = tee(self.iterators[d])
        self.iterators[d] = it1
        return it2
    def characteristic(self, values):
        iterators = [
            self.get_iterator(d)
            for d in range(self.size)
        ]
        while True:
            it = [next(itd) for itd in iterators]
            yield [
                    [
                        values[i][it[j][i]]
                        for j in range(self.size)
                    ]
                    for i in range(len(values))
            ]
    def factor_message(self, incoming_values):
        value = self.zero()
        for values in self.characteristic(incoming_values):
            tmp = self.one()
            for v in values:
                tmp = self.mult(tmp,v)
            value = self.add(value,tmp)
        return value
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


class NumpyOperations(VectorOperations):
    def zero(self):
        return np.zeros(self.size, dtype=bool)
    def one(self,i=-1):
        if i == -1:
            return np.ones(self.size, dtype=bool)
        return np.eye(1, self.size, i, dtype=bool)[0]
    def dist(self, a, b):
        return np.count_nonzero(a!=b)
    def characteristic(self, values):
        iterators = [
            self.get_iterator(d)
            for d in range(self.size)
        ]
        while True:
            it = [next(itd) for itd in iterators]
            yield [
                    np.array([
                        values[i][it[j][i]]
                        for j in range(self.size)
                    ])
                    for i in range(len(values))
            ]


class NumpyOperationsStats(NumpyOperations):
    def mult(self, a, b):
        self.stats['mult'] += 1
        return a*b
    def add(self, a, b):
        self.stats['add'] += 1
        return a+b

class FactorGraph:
    def __init__(self, variables, factors, edge_func=None, operations=VectorOperations(), printer=lambda *args: None):
        self.N = variables
        self.M = factors
        self.create_edges(edge_func)
        self.op = operations
        self.printer = printer
        self.stats = Counter()
        self.msgs = DefaultDict(lambda x:self.op.one())
    
    def create_edges(self, edge_func=None):
        if edge_func is None:
            self.Nm = [[] for i in range(self.N)]
            self.Mn = [[] for j in range(self.M)]
        else:
            self.Nm = [
                [
                    j
                    for j in range(self.M)
                    if edge_func(i,j)
                ]
                for i in range(self.N)
            ]
            self.Mn = [
                [
                    i
                    for i in range(self.N)
                    if edge_func(i,j)
                ]
                for j in range(self.M)
            ]
    
    def initial_values(self,values):
        assert len(values) == self.N
        self.initial = values
        self.PseudoPosterior = self.initial
        self.msgs = DefaultDict(self.default_msg_factory)
    
    def default_msg_factory(self, key):
        if key[0] == Side.Factor:
            return self.op.one()
        else:
            return self.initial[key[1][0]]
    
    def compute_message(self, origin, edge):
        if origin == Side.Variable:
            i = edge[0]
            value = self.initial[i]
            for j in self.Nm[i]:
                if not j == edge[1]:
                    msg = self.msgs[Side.Factor, (i,j)]
                    value = self.op.mult(value, msg)
        else:
            j = edge[1]
            value = self.op.one()
            incoming = [
                self.msgs[Side.Variable, (i,j)]
                for i in self.Mn[j]
                if not i == edge[0]
            ]
            value = self.op.factor_message(incoming)
        diff = self.op.dist(value, self.msgs[origin, edge])
        self.msgs[origin,edge] = value
        return diff
    
    def compute_pseudo_posterior(self):
        self.PseudoPosterior = [
            self.op.prod([
                self.msgs[Side.Factor, (i,j)]
                for j in self.Nm[i]
            ], self.initial[i])
            for i in range(self.N)
        ]
    
    def solve_naive(self, doskip=True, doprogress=True, dostats=True):
        diffset = defaultdict(lambda:True)
        changed = True
        while changed:
            changed = False
            for i in range(self.N):
                for j in self.Nm[i]:
                    if doskip and not any([
                        diffset[Side.Factor, (i,j2)]
                        for j2 in self.Nm[i]
                        if not j2 == j
                    ]) and not diffset[Side.Variable, (i,j)]:
                        self.stats['vfm_skip'] += 1
                        continue
                    self.stats['vfm'] += 1
                    diff = self.compute_message(Side.Variable, (i,j))
                    diffset[Side.Variable, (i,j)] = diff > 0
                    changed |= diff > 0
            for j in range(self.M):
                for i in self.Mn[j]:
                    if doskip and not any([
                        diffset[Side.Variable, (i2,j)]
                        for i2 in self.Mn[j]
                        if not i2 == i
                    ]) and not diffset[Side.Factor, (i,j)]:
                        if dostats:
                            self.stats['fvm_skip'] += 1
                        continue
                    if dostats:
                        self.stats['fvm'] += 1
                    diff = self.compute_message(Side.Factor, (i,j))
                    diffset[Side.Factor, (i,j)] = diff > 0
                    changed |= diff > 0
                    if doprogress and diff:
                        self.PseudoPosterior[i] = self.op.mult(self.PseudoPosterior[i], self.msgs[Side.Factor, (i,j)])
                        self.printer(self)
            if dostats:
                self.stats['iterations'] += 1
        self.compute_pseudo_posterior()
        return self.PseudoPosterior
    
    def solve_fvm(self, method=0, doprogress=True, dostats=True):
        fstates = {}
        for i in range(self.N):
            for j in self.Nm[i]:
                fstates[(i,j)] = FactorState()
        for i in range(self.N):
            for j in self.Nm[i]:
                for i2 in self.Mn[j]:
                    if i != i2:
                        diff = self.op.dist(self.op.zero(),self.msgs[Side.Variable, (i2,j)])
                        if diff > 0:
                            fstates[(i2,j)].change(i, diff)
        if method == 2:
            keyfunc = lambda x: fstates.get(x).get_changes()
            keyfilter = lambda x: fstates.get(x).get_changes() != 0
        elif method == 3:
            keyfunc = lambda x: fstates.get(x).get_sum()
            keyfilter = lambda x: fstates.get(x).get_sum() != 0
        elif method == 4:
            keyfunc = lambda x: fstates.get(x).get_mixed()
            keyfilter = lambda x: fstates.get(x).get_mixed() != (0,0)
        else:# method == 1
            keyfunc = lambda x: (fstates.get(x).get_round(),x)
            keyfilter = lambda x: fstates.get(x).get_mixed() != (0,0)
        
        while True:
            try:
                (i,j) = max(filter(keyfilter,fstates),key=keyfunc)
            except ValueError:
                break
            if dostats:
                self.stats['fvm'] += 1
            diff = self.compute_message(Side.Factor, (i,j))
            fstates[(i,j)].reset()
            if diff > 0:
                if doprogress:
                    self.PseudoPosterior[i] = self.op.mult(self.PseudoPosterior[i], self.msgs[Side.Factor, (i,j)])
                    self.printer(self)
                for j2 in self.Nm[i]:
                    if j2 != j:
                        if dostats:
                            self.stats['vfm'] += 1
                        diff = self.compute_message(Side.Variable, (i,j2))
                        if diff > 0:
                            for i2 in self.Mn[j2]:
                                if i2 != i:
                                    fstates[(i2,j2)].change(i, diff)
        self.compute_pseudo_posterior()
        return self.PseudoPosterior
    
    def solve(self, method=4, doskip=True, doprogress=True, dostats=True):
        self.stats = Counter()
        self.op.set_stats(self.stats)
        if method == 0:
            return self.solve_naive(doskip=doskip, doprogress=doprogress, dostats=dostats)
        else:
            return self.solve_fvm(method=method, doprogress=doprogress, dostats=dostats)
    
    def get_stats(self):
        return self.stats

    
class FactorState:
    def __init__(self):
        self.changed = {-1}
        self.sum = 1
        self.round = 0
    def reset(self):
        self.changed = set()
        self.sum = 0
        self.round -= 1 
    def change(self, i, diff):
        self.changed.add(i)
        self.sum += diff
    def get_changes(self):
        return len(self.changed)
    def get_sum(self):
        return self.sum
    def get_mixed(self):
        return (len(self.changed), self.sum)
    def get_round(self):
        return self.round
    def __repr__(self):
        return '{{changes: {}, sum: {}, round: {}}}'.format(len(self.changed), self.sum, self.round)
