# coding=utf-8
from utils import get_term_in_brackets, TermException, is_in_brackets


class Term(object):
    parent = None
    term_tree = None

    @staticmethod
    def _parse_pair(expr):
        br_sum = 1
        for i, c in enumerate(expr[1:]):
            if c == '[':
                br_sum += 1
            elif c == ']':
                br_sum -= 1
            elif c == ',' and br_sum == 1:
                return expr[1:i + 1], expr[i + 2:-1]
        return None

    @staticmethod
    def _get_number(expr):
        i = 0
        while i < len(expr) and expr[i].isdigit():
            i += 1
        return expr[:i], expr[i:]

    @classmethod
    def _get_next_conditional_term(cls, expr):
        condition, rest = cls._get_next_term(expr[2:])

        if rest[:4] == 'then':
            true_branch, rest = cls._get_next_term(rest[4:])
        else:
            raise TermException('Invalid conditional term (then not found): %s' % expr)

        if rest[:4] == 'else':
            false_branch = cls._get_term(rest[4:])
        else:
            raise TermException('Invalid conditional term (else not found): %s' % expr)

        return cls.get_conditional_term(condition, true_branch, false_branch), ''

    @classmethod
    def _get_next_term(cls, expr):
        expr = cls._preprocess_expr(expr)
        if expr[0] == '\\':
            return Term(expr), ''
        if expr[0] == '(':
            t, r = get_term_in_brackets(expr)
            return cls._get_term(t), r
        elif expr[0] == '[':
            t, r = get_term_in_brackets(expr, '[]', False)
            return Term(t), r
        elif expr[0].isdigit():
            t, r = cls._get_number(expr)
            return Constant(t), r
        elif len(expr) > 10 and expr[:2] == 'if' and 'then' in expr and 'else' in expr:
            return cls._get_next_conditional_term(expr)
        elif expr[0] in Variable.NAMES:
            return Variable(expr[0]), expr[1:]
        elif expr[0] in CombinatorY.NAMES:
            return CombinatorY(expr[0]), expr[1:]
        elif expr[0] in MathOperation.OPERATIONS:
            return MathOperation(expr[0]), expr[1:]

    @classmethod
    def _get_term(cls, expr):
        term, r = cls._get_next_term(expr)
        while r:
            if is_in_brackets(r):
                t = cls._get_term(r)
                r = ''
            else:
                t, r = cls._get_next_term(r)
            term = cls.get_term(Node.APPLICATION, term, t)
        return term

    @staticmethod
    def _preprocess_expr(expr):
        if ' ' in expr:
            expr = expr.replace(' ', '')

        while expr[0] == '(' and expr[-1] == ')':
            t, _ = get_term_in_brackets(expr)
            if len(t) == len(expr) - 2:
                expr = expr[1:-1]
            else:
                break
        return expr

    @staticmethod
    def get_term(op, left, right):
        res = Term()
        res.term_tree = Node(op, left, right, res)
        return res

    @staticmethod
    def get_conditional_term(condition, true_branch, false_branch):
        res = Term()
        res.term_tree = ConditionNode(condition, true_branch, false_branch, res)
        return res

    def __init__(self, expr=None):
        if expr is None:
            return

        expr = self._preprocess_expr(expr)

        if expr[0] == '\\':
            parts = expr.split('.')
            l = parts[0][1:]
            r = '.'.join(parts[1:])
            r = self._get_term(r)
            self.term_tree = Node(Node.LAMBDA_ABSTRACTION, Variable(l), r, self)
        elif expr[0] == '[':
            l, r = self._parse_pair(expr)
            self.term_tree = Node(Node.PAIR, self._get_term(l), self._get_term(r), self)
        else:
            self.init_with_term(self._get_term(expr))

    def init_with_term(self, term):
        self.term_tree = term.term_tree
        self.parent = term.parent
        self.term_tree.set_owner(self)

    def code(self):
        return self.term_tree.code()

    def __repr__(self):
        return str(self.term_tree)


class Constant(Term):
    value = None

    def __init__(self, value):
        Term.__init__(self)
        self.value = value

    def code(self):
        return u"'%s" % self.value

    def __repr__(self):
        return self.value


class CombinatorY(Term):
    NAMES = 'Y'

    def __init__(self, name):
        Term.__init__(self)
        self.name = name

    def code(self):
        return self.name

    def __repr__(self):
        return self.name


class Variable(Term):
    NAMES = ['x', 'y', 'z', 'f', 'g', 'n', 'm']
    name = None
    de_br_code = None
    var_list = []

    @classmethod
    def clear_var_list(cls):
        cls.var_list[:] = []

    @classmethod
    def get_var_list(cls):
        return filter(lambda x: not (
            x.parent.term_tree.op_type == Node.LAMBDA_ABSTRACTION and x.parent.term_tree.left == x),
                      cls.var_list)

    def __init__(self, name):
        Term.__init__(self)
        self.name = name
        self.var_list.append(self)

    def get_de_br_code(self):
        if self.parent.term_tree.op_type == Node.LAMBDA_ABSTRACTION and self.parent.term_tree.left == self:
            return None

        if not self.de_br_code:
            self.de_br_code = 0
            is_found = False
            p = self.parent
            while p:
                if p.term_tree.op_type == Node.LAMBDA_ABSTRACTION:
                    if p.term_tree.left.name == self.name:
                        is_found = True
                        break
                    self.de_br_code += 1
                p = p.parent
            if not is_found:
                raise TermException('Variable %s is free!' % self.name)

        return self.de_br_code

    def code(self):
        return u'Fst' * self.get_de_br_code() + u'Snd'

    def __repr__(self):
        return self.name


class MathOperation(Term):
    OPERATIONS = [
        '+',
        '*',
        '=',
        '-',
        'L',
        'M',
        '&',
        '|',
    ]

    op = None
    f = None

    def __init__(self, op):
        Term.__init__(self)
        self.op = op

    def code(self):
        # return u'%s' % self.op
        return u'Λ(Snd %s)' % self.op

    def __repr__(self):
        return self.op


class Node(object):
    LAMBDA_ABSTRACTION = 0
    APPLICATION = 1
    PAIR = 2

    op_type = APPLICATION

    left = None
    right = None
    owner = None

    def __init__(self, op_type, left, right, owner=None):
        self.op_type = op_type
        self.left = left
        self.right = right
        self.set_owner(owner)

    def set_owner(self, owner):
        self.owner = owner
        self.left.parent = self.owner
        self.right.parent = self.owner

    def code(self):
        if self.op_type == self.LAMBDA_ABSTRACTION:
            return u'Λ(%s)' % self.right.code()
        elif self.op_type == self.APPLICATION:
            if type(self.left) == CombinatorY:
                if self.right.term_tree.op_type == self.LAMBDA_ABSTRACTION and \
                                self.right.term_tree.right.term_tree.op_type == self.LAMBDA_ABSTRACTION:
                    # return u'Λ(%s)<Y(%s)>' % (self.right.term_tree.right.term_tree.right.code(),
                    #                           self.right.term_tree.right.term_tree.right.code())
                    return u'<%s, Y(%s)>ε' % (self.right.code(),
                                              self.right.term_tree.right.term_tree.right.code())
                else:
                    return u'<%s, Y(%s)>ε' % (self.right.code(), self.right.code())
            return u'<%s, %s>ε' % (self.left.code(), self.right.code())
        elif self.op_type == self.PAIR:
            return u'<%s, %s>' % (self.left.code(), self.right.code())

    def __repr__(self):
        if self.op_type == self.LAMBDA_ABSTRACTION:
            return '\\ %s . %s' % (str(self.left), str(self.right))
        elif self.op_type == self.APPLICATION:
            return '(%s)(%s)' % (str(self.left), str(self.right))
        elif self.op_type == self.PAIR:
            return '[%s, %s]' % (str(self.left), str(self.right))


class ConditionNode(Node):
    CONDITION_OP = 3

    def __init__(self, condition, true_term, false_term, owner=None):
        self.condition = condition
        Node.__init__(self, self.CONDITION_OP, true_term, false_term, owner)

    def set_owner(self, owner):
        super(ConditionNode, self).set_owner(owner)
        self.condition.parent = owner

    def code(self):
        return u'if%sbr(%s,%s)' % \
               (self.condition.code(), self.left.code(), self.right.code())

    def __repr__(self):
        return "if (%s) then (%s) else (%s)" % \
               (str(self.condition), str(self.left), str(self.right))


def compile_expr(expr):
    Variable.clear_var_list()
    t = Term(expr)
    return t.code()
