# coding=utf-8
import operator
from copy import deepcopy

import re
from texttable import Texttable


class CAM:
    _transitions = {
        '<': lambda self: self._push(),
        ',': lambda self: self._swap(),
        '>': lambda self: self._cons(),
        '\'': lambda self: self._quote(),
        'Fst': lambda self: self._car(),
        'Snd': lambda self: self._cdr(),
        u'ε': lambda self: self._app(),
        u'Λ': lambda self: self._cur(),

        '+': lambda self: self._math_op(operator.add),
        '-': lambda self: self._math_op(operator.sub),
        '*': lambda self: self._math_op(operator.mul),
    }

    def __init__(self, code):
        self.code = code.replace(' ', '')
        self.term = ()
        self.stack = []

        self.history = []
        self.iteration = 0
        self.evaluated = False
        self.errors = False

        self.history.append([self.iteration, self.term, self.code, self.stack])

    def _push(self):
        self.stack.append(self.term)

    def _car(self):
        self.term = self.term[0]

    def _cdr(self):
        self.term = self.term[1]

    def _cons(self):
        self.term = (self.stack.pop(), self.term)

    def _cur(self):
        start_pos = 0
        end_pos = self.code.find(')')
        arg = self.code[start_pos:end_pos + 1]
        self.code = self.code[end_pos + 1:]
        self.term = {arg[1:-1]: self.term}

    def _quote(self):
        self.term = re.findall(r'\d+', self.code)[0]
        self.code = self.code[len(str(self.term)):]

    def _swap(self):
        tmp = self.stack.pop()
        self.stack.append(self.term)
        self.term = tmp

    def _app(self):
        self.code = self.term[0].keys()[0] + self.code
        self.term = (self.term[0].values()[0], self.term[1])

    def _math_op(self, f):
        self.term = f(int(self.term[0]), int(self.term[1]))

    def _get_next_token(self):
        # self.code = self.code.strip()
        for item in self._transitions.keys():
            if self.code.startswith(item):
                self.code = self.code[len(item):]
                return item
        return self.code

    def nex_step(self):
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
            self.nex_step()
            self.history.append([self.iteration, self.term, self.code, deepcopy(self.stack)])
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

        t = Texttable()
        data = [['№', 'Term', 'Code', 'Stack']] + [
            [i.encode('utf-8') if isinstance(i, basestring) else str(i) for i in item] for item in self.history]
        t.add_rows(data)
        t.set_cols_align(['l', 'r', 'r', 'r'])
        t.set_cols_valign(['m', 'm', 'm', 'm'])
        t.set_cols_width(autodetect_width(data))
        print t.draw()


if __name__ == "__main__":
    import time

    examples = [u"<Λ( Snd +),     <'1,'2>>ε", u"<Λ(Snd+),<'1,<Λ(Snd*),<'3,'4>>ε>>ε"]
    for example in examples:
        print 'EXAMPLE STARTED'
        start = time.time()
        k = CAM(example)
        k.evaluate()
        k.print_steps()
        print 'EXAMPLE ENDED, TOOK %s s\n' % (time.time() - start)
        del k
