# coding=utf-8
import logging

from utils import UnicodeHack

_C = u"<Snd,<FstSnd,<Snd,'1>->ε>*"
_B = u"<<Snd,'0>=br('1," + _C + u")"

LIBRARY = [
    ('4 + 3', u"<Λ(<Snd, <'-4, '3>>ε),Λ(Snd+)>ε", 'c'),
    ('1 + 3 * 4', u"<Λ(Snd+),<'1,<Λ(Snd*),<'3,'4>>ε>>ε", 'c'),
    ('2!', u"<<Y(" + _B + u")>Λ(" + _B + u")><Snd,'%s>ε" % 2, 'c'),
    ('5 + 4 * 5', u"((\\x.\\f.+[x,f x])5)(\\x.*[4,x])", 'l'),
    ('1 + 3', u"(\\f.\\x.f x)(\\x.+[1,x])3", 'l'),
]


def print_lib():
    i = 1
    for item in LIBRARY:
        print '%s) %s = %s' % (i, item[0], UnicodeHack(item[1]))
        i += 1
    print


def get_lib_example(i):
    if not i.isdigit() or int(i) not in range(1, len(LIBRARY) + 1):
        logging.error('Invalid library example number')
        return None, None
    return LIBRARY[int(i) - 1][1], LIBRARY[int(i) - 1][2]
