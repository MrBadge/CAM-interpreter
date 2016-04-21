class TermException(Exception):
    pass


class UnicodeHack(unicode):
    def __repr__(self):
        return unicode.__repr__(self)[2:-1].decode("unicode_escape").encode('utf-8')


class DictHack(dict):
    def __repr__(self):
        return dict.__repr__(self)[1:-1]


def get_term_in_brackets(expr, br='()', remove_brackets=True):
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
                raise TermException('Invalid brackets in expr: %s', expr)
            term += c
    raise TermException('Invalid brackets in expr: %s', expr)


def parse_args_in_brackets(expr, br='()'):
    br_sum = 1
    for i, c in enumerate(expr[1:]):
        if c == br[0]:
            br_sum += 1
        elif c == br[1]:
            br_sum -= 1
        elif c == ',' and br_sum == 1:
            return expr[1:i + 1], expr[i + 2:-1]
    return None