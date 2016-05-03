# coding=utf-8
import logging
import operator
from copy import deepcopy
from math import log10
from multiprocessing.pool import ThreadPool

import re
from texttable import Texttable
from utils import TermException
from utils import get_term_in_brackets, parse_args_in_brackets, DictHack, UnicodeHack

pool = ThreadPool(processes=4)


class CAM:
    _transitions = {
        '>': lambda self, _: self._cons(),
        '<': lambda self, fast: self._push_new() if fast else self._push(self.parallel),
        'if': lambda self, fast: self._if_new() if fast else self._if(),
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
    operation_opt_rule = re.compile(r'<<(.*?),(.*?)>>Snd(\*|\+|-|=)')

    def __init__(self, code, save_history=True, with_opt=True, fast_method=False, parallel=False):
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

        self.parallel = parallel
        self.fast_method = fast_method

        if self.fast_method:
            self.parsed_code = self._parse_code(self.code)

        self.save_history = save_history
        if self.save_history:
            self.history.append([0, (), self.code, []])

    @staticmethod
    def _calc_part(cam, code_part):
        sub_cam = CAM(code_part, save_history=cam.save_history, with_opt=False, fast_method=cam.fast_method,
                      parallel=cam.parallel)
        sub_cam.term = cam.term
        sub_cam.evaluate()
        return sub_cam.term

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

    def _if(self):
        self._push(False)

    def _if_new(self):
        self._push_new()

    def _push(self, parallel):
        if parallel:
            try:
                term, tmp = get_term_in_brackets('<' + self.code, br='<>', remove_brackets=False)
                args = parse_args_in_brackets(term, br='<>')
                self.code = tmp  # self.code[len(term) - 1:]
                if args:
                    t1 = pool.apply_async(CAM._calc_part, (self, args[0]))
                    t2 = pool.apply_async(CAM._calc_part, (self, args[1]))
                    self.term = (t1.get(), t2.get())
                else:
                    self.term = CAM._calc_part(self, term[1:-1])
            except TermException:
                self.stack.append(self.term)
        else:
            self.stack.append(self.term)

    def _push_new(self):
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

    @staticmethod
    def _get_next_token_new(code):
        for i in CAM._possible_token_len:
            if code[0:i] in CAM._valid_tokens:
                return UnicodeHack(code[0:i]), code[i:]
        raise Exception('Unknown token')

    @staticmethod
    def _parse_code(code):
        parsed_code = []
        while len(code):
            next_token, code = CAM._get_next_token_new(code)
            parsed_code.append(next_token)
            if next_token == u'Λ' or next_token == 'Y':
                arg, code = get_term_in_brackets(code)
                parsed_code.append(CAM._parse_code(arg))
            elif next_token == '\'':
                arg = int(UnicodeHack(re.search(CAM.nums_re, code).group()))
                parsed_code.append([arg])
                length = int(log10(abs(arg))) + 1 if arg != 0 else 1
                code = code[length if arg >= 0 else length + 1:]
            elif next_token == 'br':
                args, code = get_term_in_brackets(code, remove_brackets=False)
                arg1, arg2 = parse_args_in_brackets(args)
                parsed_code.append([CAM._parse_code(arg1), CAM._parse_code(arg2)])
        return parsed_code[::-1]

    @staticmethod
    def optimize_code(code):
        logging.info('Code before optimization: %s' % code)
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
            for item in re.finditer(CAM.operation_opt_rule, code):
                arg, rest_code = get_term_in_brackets(item.group(), br='<>', exception=False)
                if not arg or rest_code[:3] != 'Snd':
                    continue
                operation = rest_code[-1]
                code = code.replace('<%s>Snd%s' % (arg, operation), '%s%s' % (arg, operation))
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
        if self.fast_method:
            while self.parsed_code:
                self._transitions[self.parsed_code.pop()](self, True)
                self.iteration += 1
        else:
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
            header = ['№', 'Term', 'Code'] if self.parallel else ['№', 'Term', 'Code', 'Stack']
            data = [header] + [
                [repr(i) for i in item][:-1] if self.parallel else [repr(i) for i in item] for item in self.history]
            t.add_rows(data)
            t.set_cols_align(['l'] + ['r'] * (len(header) - 1))
            t.set_cols_valign(['m'] + ['m'] * (len(header) - 1))
            t.set_cols_width(autodetect_width(data))
            print t.draw()
        else:
            if not self.errors:
                print ' Steps: %10s' % self.iteration
                if show_result:
                    print 'Result: %10s' % repr(self.term)
