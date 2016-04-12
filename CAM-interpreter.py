# coding=utf-8
import operator
import re


class KAM:
    code = ''
    term = ()
    stack = []
    evaluated = False
    errors = False
    iteration = 0

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
        self.code = code

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

    def _get_next_token(self, code):
        for item in self._transitions.keys():
            if self.code.startswith(item):
                self.code = self.code[len(item):]
                return item
        return code

    def nex_step(self):
        try:
            self._transitions[self._get_next_token(self.code)](self)
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
            print '%4d)   %35s     %35s     %35s' % (self.iteration, self.term, self.code, self.stack)
            self.nex_step()
        if not self.errors:
            print '%4d)   %35s     %35s     %35s' % (self.iteration, self.term, self.code, self.stack)
        self.evaluated = True


# KAM(u"<Λ(Snd+),<'1,'2>>ε").evaluate()

KAM(u"<Λ(Snd+),<'1,<Λ(Snd*),<'3,'4>>ε>>ε").evaluate()
