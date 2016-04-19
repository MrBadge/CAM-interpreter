# coding=utf-8
import operator
from copy import deepcopy

import re
from texttable import Texttable
from utils import get_term_in_brackets, DictHack, UnicodeHack


class CAM:
    _transitions = {
        '<': lambda self: self._push(),
        ',': lambda self: self._swap(),
        '>': lambda self: self._cons(),
        '\'': lambda self: self._quote(),
        'Fst': lambda self: self._car(),
        'Snd': lambda self: self._cdr(),

        u'ε': lambda self: self._app(),
        'Eps': lambda self: self._app(),

        u'Λ': lambda self: self._cur(),
        '\\': lambda self: self._cur(),

        'branch': lambda self: self._branch(),
        'Y': lambda self: self._rec(),

        '+': lambda self: self._math_op(operator.add),
        '-': lambda self: self._math_op(operator.sub),
        '*': lambda self: self._math_op(operator.mul),
        '=': lambda self: self._math_op(operator.eq)
    }

    def __init__(self, code, only_result=False):
        self.code = UnicodeHack(code.replace(' ', ''))
        self.term = ()
        self.stack = []

        self.recursion_stack = {}

        self.history = []
        self.iteration = 0
        self.evaluated = False
        self.errors = False

        self.show_steps = not only_result
        if self.show_steps:
            self.history.append([0, (), self.code, []])

    def _rec(self):
        arg, code = get_term_in_brackets(self.code)
        rec_stack_depth = len(self.recursion_stack)
        self.recursion_stack['rec' + str(rec_stack_depth)] = DictHack({arg: (self.term, 'rec' + str(rec_stack_depth))})
        self.term = self.recursion_stack['rec' + str(rec_stack_depth)]
        self.code = code

    def _branch(self):
        args, code = get_term_in_brackets(self.code)
        if not isinstance(self.term, bool):
            raise Exception('Term is neither true not false')
        elif self.term:
            self.code = args.split(',')[0] + code
        else:
            self.code = ','.join(args.split(',')[1:]) + code
        self.term = self.stack.pop()

    def _push(self):
        self.stack.append(self.term)

    def _car(self):
        self.term = self.term[0]

    def _cdr(self):
        self.term = self.term[1]

    def _cons(self):
        self.term = (self.stack.pop(), self.term)

    def _cur(self):
        parse_arg = get_term_in_brackets(self.code)
        self.code = parse_arg[1]
        self.term = DictHack({parse_arg[0]: self.term})

    def _quote(self):
        self.term = UnicodeHack(re.findall(r'\d+', self.code)[0])
        self.code = self.code[len(str(self.term)):]

    def _swap(self):
        tmp = self.stack.pop()
        self.stack.append(self.term)
        self.term = tmp

    def _app(self):
        self.term = (
            self.recursion_stack[self.term[0]] if self.term[0] in self.recursion_stack.keys() else self.term[0],
            self.term[1])
        self.code = self.term[0].keys()[0] + self.code
        self.term = (self.term[0].values()[0], self.term[1])

    def _math_op(self, f):
        self.term = f(int(self.term[0]), int(self.term[1]))

    def _get_next_token(self):
        for item in self._transitions.keys():
            if self.code.startswith(item):
                self.code = self.code[len(item):]
                return item
        return self.code

    def next_step(self):
        try:
            self._transitions[self._get_next_token()](self)
            self.iteration += 1
        except KeyError, e:
            self.evaluated = True
            self.errors = True
            print 'Unknown operation: %s' % str(e)
        except Exception, e:
            self.evaluated = True
            self.errors = True
            print 'Code could be invalid. Got exception: ' + str(e)

    def evaluate(self):
        while self.code and not self.evaluated:
            self.next_step()
            if self.show_steps:
                self.history.append([self.iteration, self.term, UnicodeHack(self.code), deepcopy(self.stack)])
        self.evaluated = True

    def print_steps(self):
        def max_len_of_list_of_str(s):
            return max(len(line) for line in str(s).split('\n'))

        def autodetect_width(d):
            widths = [0] * len(d[0])
            for line in d:
                for _i in range(len(line)):
                    widths[_i] = max(widths[_i], max_len_of_list_of_str(line[_i]))
            return widths

        if self.show_steps:
            if self.errors:
                self.history = self.history[:-1]
            t = Texttable()
            data = [['№', 'Term', 'Code', 'Stack']] + [
                [repr(i).decode("unicode_escape").encode('utf-8') for i in item] for item in self.history]
            t.add_rows(data)
            t.set_cols_align(['l', 'r', 'r', 'r'])
            t.set_cols_valign(['m', 'm', 'm', 'm'])
            t.set_cols_width(autodetect_width(data))
            print t.draw()
        else:
            if not self.errors:
                print '%s steps' % self.iteration
                # print 'Result: %s' % self.term


if __name__ == "__main__":
    import time

    # import cam_compiler

    # import sys

    # sys.setrecursionlimit(100000000)
    # factorial = lambda x: x and factorial(x - 1) * x or 1
    # print factorial(10000)

    # dz1 = '(\\f.\\x.f x)(\\x.+[1,x])3'
    # dz2 = '((\\x.\\f.+[x,f x])5)(\\x.*[4,x])'
    # examples = [cam_compiler.compile_expr(dz1)]

    # examples = [u"<Λ( Snd +),     <'1,'2>>ε", u"<Λ(Snd+),<'1,<Λ(Snd*),<'3,'4>>ε>>ε"]
    # examples = [u"<Λ(<Snd, <'4, '3>>ε),Λ(Snd+)>ε"]
    # examples = [u"<<Λ(Λ(<Λ(SndP),<Fst Snd,Snd>>)),'1>ε,'0>ε"]
    # examples = [u"<Λ(<Λ(<Snd, <Snd Fst, '2>>ε),Λ(Snd*)>ε),'3>ε"]
    # examples = [u"<Λ(<Snd, <Snd Fst, '2>>ε),Λ(Snd*)>ε"]
    # examples = [u"<Λ(<<Snd,'4>ε,<Λ(Snd),'3>ε>ε),Λ(Snd+)>ε"]

    # examples = [u"<Λ(<Λ(<Λ(Snd+),<FstSnd,Snd>>ε),'3>ε),'2>ε"]
    # examples = [u"<<Λ(Λ(<FstSnd,<Snd,FstSnd>ε>>+)),Λ(<'4,Snd>*)>ε,'5>ε"]

    C = u"<Snd,<FstSnd,<Snd,'1>->ε>*"
    B = u"<<Snd,'0>=branch('1," + C + u")"
    fact = u"<<Y(" + B + u")>Λ(" + B + u")><Snd,'%s>ε" % 100000
    examples = [fact]
    for example in examples:
        print 'EXAMPLE STARTED'
        start = time.time()
        k = CAM(example, only_result=True)
        k.evaluate()
        k.print_steps()
        print 'EXAMPLE ENDED, TOOK %s s\n' % (time.time() - start)
        del k
