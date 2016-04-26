# coding=utf-8
import logging
import operator
from copy import deepcopy
from math import log10

import re
from texttable import Texttable
from utils import get_term_in_brackets, parse_args_in_brackets, DictHack, UnicodeHack


class CAM:
    _transitions = {
        '>': lambda self, _: self._cons(),
        '<': lambda self, _: self.stack.append(self.term),
        ',': lambda self, _: self._swap(),
        '\'': lambda self, fast: self._quote_new() if fast else self._quote(),

        u'Λ': lambda self, fast: self._cur_new() if fast else self._cur(),
        '\\': lambda self, fast: self._cur_new() if fast else self._cur(),

        u'ε': lambda self, fast: self._app_new() if fast else self._app(),
        'Eps': lambda self, fast: self._app_new() if fast else self._app(),

        'Fst': lambda self, _: self._car(),
        'Snd': lambda self, _: self._cdr(),

        'br': lambda self, fast: self._branch_new() if fast else self._branch(),
        'Y': lambda self, fast: self._rec_new() if fast else self._rec(),

        '*': lambda self, fast: self._math_op(operator.mul),
        '+': lambda self, fast: self._math_op(operator.add),
        '-': lambda self, fast: self._math_op(operator.sub),
        '=': lambda self, fast: self._math_op(operator.eq)
    }
    _valid_tokens = _transitions.keys()
    _possible_token_len = list(set(map(len, _transitions.keys())))
    nums_re = re.compile(r'-?\d+')
    betta_opt_rule = re.compile(r'<\\\((?P<X>.*)\),(?P<Z>.*)>Eps')
    betta_opt_rule_identifier = re.compile(r'<\\\(.*')

    def __init__(self, code, save_history=True, with_opt=True, fast_method=False):
        self.code = UnicodeHack(code.replace(' ', ''))
        if with_opt:
            self.code = CAM.optimize_code(self.code)
        self.term = ()
        self.stack = []

        self.recursion_stack = {}
        self.recs_count = 0

        self.history = []
        self.iteration = 0
        self.evaluated = False
        self.errors = False

        if fast_method:
            self.parsed_code = self._parse_code(self.code)

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

    def _rec_new(self):
        rec_name = 'r' + str(self.recs_count)
        self.recs_count += 1
        self.recursion_stack[rec_name] = (self.parsed_code.pop(), (self.term, rec_name))
        self.term = self.recursion_stack[rec_name]

    def _branch(self):
        args, code = get_term_in_brackets(self.code, remove_brackets=False)
        arg1, arg2 = parse_args_in_brackets(args)
        self.code = (arg1 if self.term else arg2) + code
        self.term = self.stack.pop()

    def _branch_new(self):
        args = self.parsed_code.pop()
        self.parsed_code += (args[0] if self.term else args[1])
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

    def _cur_new(self):
        self.term = (self.parsed_code.pop(), self.term)

    def _quote(self):
        self.term = int(UnicodeHack(re.search(self.nums_re, self.code).group()))
        length = int(log10(abs(self.term))) + 1 if self.term != 0 else 1
        self.code = self.code[length if int(self.term) >= 0 else length + 1:]

    def _quote_new(self):
        self.term = self.parsed_code.pop()[0]

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

    def _app_new(self):
        if isinstance(self.term[0], basestring):
            self.term = (
                self.recursion_stack[self.term[0]] if self.term[0] in self.recursion_stack.keys() else self.term[0],
                self.term[1])
        self.parsed_code += self.term[0][0]
        self.term = (self.term[0][1], self.term[1])

    def _math_op(self, f):
        self.term = f(self.term[0], self.term[1])

    def _get_next_token(self):
        for i in self._possible_token_len:
            if self.code[0:i] in self._valid_tokens:
                next_token = self.code[0:i]
                self.code = self.code[i:]
                return next_token
        raise Exception('Unknown token')

    def _get_next_token_new(self, code):
        for i in self._possible_token_len:
            if code[0:i] in self._valid_tokens:
                return UnicodeHack(code[0:i]), code[i:]
        raise Exception('Unknown token')

    def _parse_code(self, code):
        parsed_code = []
        while len(code):
            next_token, code = self._get_next_token_new(code)
            parsed_code.append(next_token)
            if next_token == u'Λ' or next_token == 'Y':
                arg, code = get_term_in_brackets(code)
                parsed_code.append(self._parse_code(arg))
            elif next_token == '\'':
                arg = int(UnicodeHack(re.search(self.nums_re, code).group()))
                parsed_code.append([arg])
                length = int(log10(abs(arg))) + 1 if arg != 0 else 1
                code = code[length if arg >= 0 else length + 1:]
            elif next_token == 'br':
                args, code = get_term_in_brackets(code, remove_brackets=False)
                arg1, arg2 = parse_args_in_brackets(args)
                parsed_code.append([self._parse_code(arg1), self._parse_code(arg2)])
        return parsed_code[::-1]

    @staticmethod
    def optimize_code(code):
        code = code.replace(u'Λ', '\\').replace(u'ε', 'Eps')
        was_optimized = True
        while was_optimized:
            was_optimized = False
            for item in re.finditer(CAM.betta_opt_rule, code):
                token, rest_code = get_term_in_brackets(item.group(), br='<>', remove_brackets=False)
                if rest_code[:3] != 'Eps':
                    continue
                arg1, arg2 = parse_args_in_brackets(token, br='<>')
                lambda_arg, _ = get_term_in_brackets(arg1[1:])
                code = code.replace('<%s,%s>Eps' % (arg1, arg2), '<%s>%s' % (arg2, lambda_arg))
                was_optimized = True

        code = UnicodeHack(code.replace('\\', u'Λ').replace('Eps', u'ε'))
        logging.info('Optimized code: %s' % code)
        return code

    def next_step(self):
        try:
            self._transitions[self._get_next_token()](self, False)
            self.iteration += 1
        except Exception, e:
            self.evaluated = True
            self.errors = True
            logging.error('Code could be invalid. Got exception: ' + str(e))

    def evaluate(self):
        while self.code and not self.evaluated:
            self.next_step()
            if self.save_history:
                self.history.append([self.iteration, self.term, UnicodeHack(self.code), deepcopy(self.stack)])
        self.evaluated = True

    def evaluate_fast(self):
        while self.parsed_code:
            self._transitions[self.parsed_code.pop()](self, True)
            self.iteration += 1
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
                [repr(i) for i in item] for item in self.history]
            t.add_rows(data)
            t.set_cols_align(['l', 'r', 'r', 'r'])
            t.set_cols_valign(['m', 'm', 'm', 'm'])
            t.set_cols_width(autodetect_width(data))
            print t.draw()
        else:
            if not self.errors:
                print '%s steps' % self.iteration
                if show_result:
                    print 'Result: %s' % repr(self.term)
