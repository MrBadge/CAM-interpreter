class TermException(Exception):
    pass


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
                return term if remove_brackets else br[0] + term + br[1], expr[i + 2:]
            elif br_sum < 0:
                raise TermException('Invalid brackets in expr: %s', expr)
            term += c
    raise TermException('Invalid brackets in expr: %s', expr)
