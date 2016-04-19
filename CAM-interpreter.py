#!/usr/bin/env python
# coding=utf-8
import operator
from copy import deepcopy
from math import log10

import re
from texttable import Texttable
from utils import get_term_in_brackets, parse_args_in_brackets, DictHack, UnicodeHack


class CAM:
    _transitions = {
        '>': lambda self: self._cons(),
        '<': lambda self: self.stack.append(self.term),
        ',': lambda self: self._swap(),
        '\'': lambda self: self._quote(),

        u'Λ': lambda self: self._cur(),
        '\\': lambda self: self._cur(),

        u'ε': lambda self: self._app(),
        'Eps': lambda self: self._app(),

        'Fst': lambda self: self._car(),
        'Snd': lambda self: self._cdr(),

        'br': lambda self: self._branch(),
        'Y': lambda self: self._rec(),

        '*': lambda self: self._math_op(operator.mul),
        '+': lambda self: self._math_op(operator.add),
        '-': lambda self: self._math_op(operator.sub),
        '=': lambda self: self._math_op(operator.eq)
    }
    _valid_tokens = _transitions.keys()
    _possible_token_len = list(set(map(len, _transitions.keys())))

    def __init__(self, code, save_history=True):
        self.code = UnicodeHack(code.replace(' ', ''))
        self.term = ()
        self.stack = []

        self.recursion_stack = {}
        self.recs_count = 0

        self.history = []
        self.iteration = 0
        self.evaluated = False
        self.errors = False

        self.save_history = save_history
        if self.save_history:
            self.history.append([0, (), self.code, []])

    def _rec(self):
        arg, code = get_term_in_brackets(self.code)
        rec_name = 'r' + str(self.recs_count)
        self.recs_count += 1
        self.recursion_stack[rec_name] = DictHack({arg: (self.term, rec_name)})
        self.term = self.recursion_stack[rec_name]
        self.code = code

    def _branch(self):
        args, code = get_term_in_brackets(self.code, remove_brackets=False)
        arg1, arg2 = parse_args_in_brackets(args)
        self.code = (arg1 if self.term else arg2) + code
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
        arg, self.code = get_term_in_brackets(self.code)
        self.term = DictHack({arg: self.term})

    def _quote(self):
        self.term = UnicodeHack(re.search(r'\d+', self.code).group())
        length = int(log10(int(self.term))) + 1 if self.term != '0' else len(self.term)
        self.code = self.code[length:]

    def _swap(self):
        tmp = self.stack.pop()
        self.stack.append(self.term)
        self.term = tmp

    def _app(self):
        if isinstance(self.term[0], basestring):
            self.term = (
                self.recursion_stack[self.term[0]] if self.term[0] in self.recursion_stack.keys() else self.term[0],
                self.term[1])
        self.code = self.term[0].keys()[0] + self.code
        self.term = (self.term[0].values()[0], self.term[1])

    def _math_op(self, f):
        self.term = f(int(self.term[0]), int(self.term[1]))

    def _get_next_token(self):
        for i in self._possible_token_len:
            if self.code[0:i] in self._valid_tokens:
                next_token = self.code[0:i]
                self.code = self.code[i:]
                return next_token
        raise Exception('Unknown token')

    def next_step(self):
        try:
            self._transitions[self._get_next_token()](self)
            self.iteration += 1
        except Exception, e:
            self.evaluated = True
            self.errors = True
            print 'Code could be invalid. Got exception: ' + str(e)

    def evaluate(self):
        while self.code and not self.evaluated:
            self.next_step()
            if self.save_history:
                self.history.append([self.iteration, self.term, UnicodeHack(self.code), deepcopy(self.stack)])
        self.evaluated = True

    def print_steps(self, show_result=True):
        def max_len_of_list_of_str(s):
            return max(len(line) for line in str(s).split('\n'))

        def autodetect_width(d):
            widths = [0] * len(d[0])
            for line in d:
                for _i in range(len(line)):
                    widths[_i] = max(widths[_i], max_len_of_list_of_str(line[_i]))
            return widths

        if self.save_history:
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
                if show_result:
                    print 'Result: %s' % self.term


if __name__ == "__main__":
    import time
    # from math import factorial
    # import cam_compiler

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
    B = u"<<Snd,'0>=br('1," + C + u")"
    fact = u"<<Y(" + B + u")>Λ(" + B + u")><Snd,'%s>ε" % 100000
    examples = [fact]
    for example in examples:
        print 'EXAMPLE STARTED'
        k = CAM(example, save_history=False)
        start = time.time()
        k.evaluate()
        # factorial(1000000)
        end = time.time() - start
        k.print_steps(show_result=False)
        print 'EXAMPLE ENDED, TOOK %s s\n' % end
        del k
