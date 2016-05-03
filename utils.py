BRACKETS = [
    "()",
    "<>",
    "[]"
    "{}"
]


class TermException(Exception):
    pass


class UnicodeHack(unicode):
    def __repr__(self):
        return unicode.__repr__(self)[2:-1].decode("unicode_escape").encode('utf-8')


class DictHack(dict):
    def __repr__(self):
        return dict.__repr__(self)[1:-1]


def get_term_in_brackets(expr, br='()', remove_brackets=True, exception=True):
    if expr[0] == br[0]:
        br_sum = 1
        term = ''
        for i, c in enumerate(expr[1:]):
            if c == br[0]:
                br_sum += 1
            elif c == br[1]:
                br_sum -= 1
            if br_sum == 0:
                return UnicodeHack(term) if remove_brackets else UnicodeHack(br[0] + term + br[1]), expr[i + 2:]
            elif br_sum < 0:
                if exception:
                    raise TermException('Invalid brackets in expr: %s', expr)
                else:
                    return None, None
            term += c
    if exception:
        raise TermException('Invalid brackets in expr: %s', expr)
    else:
        return None, None


def parse_args_in_brackets(expr, br='()'):
    br_sums = {}
    for b in BRACKETS:
        br_sums[b] = 0
    br_sums[br] += 1
    for i, c in enumerate(expr[1:]):
        for b in BRACKETS:
            if c == b[0]:
                br_sums[b] += 1
            elif c == b[1]:
                br_sums[b] -= 1
        if c == ',' and br_sums[br] == 1:
            is_balanced = True
            for b in BRACKETS:
                if b != br and br_sums[b] != 0:
                    is_balanced = False
                    break
            if is_balanced:
                return expr[1:i + 1], expr[i + 2:-1]
    return None


def is_in_brackets(expr, br='()'):
    if expr[0] != br[0] or expr[-1] != br[1]:
        return False
    br_sum = 0
    for c in expr:
        if c == br[0]:
            br_sum += 1
        elif c == br[1]:
            br_sum -= 1
    return br_sum == 0
