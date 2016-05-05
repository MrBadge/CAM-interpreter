# coding=utf-8
import logging

from utils import UnicodeHack

_C = u"<Snd,<FstSnd,<Snd,'1>->ε>*"
_B = u"if<Snd,'0>=br('1," + _C + u")"

LIBRARY = [
    ('x + y', u"<Λ(<Snd, <x, y>>ε),Λ(Snd+)>ε", 'c', lambda x, y: u"<Λ(<Snd, <'%s, '%s>>ε),Λ(Snd+)>ε" % (x, y)),

    ('x + y * z', u"<Λ(Snd+),<x,<Λ(Snd*),<y,z>>ε>>ε", 'c',
     lambda x, y, z: u"<Λ(Snd+),<'%s,<Λ(Snd*),<'%s,'%s>>ε>>ε" % (x, y, z)),

    ('n!', u"<<Y(" + _B + u")>Λ(" + _B + u")><Snd,'n>ε", 'c',
     lambda n: u"<<Y(" + _B + u")>Λ(" + _B + u")><Snd,'%s>ε" % n),

    ('(Artem\'s code) n!', u"<Y(if<Snd,'0>=br('1,<Snd,<FstSnd,<Snd,'1>->ε>*)),'n>ε", 'c',
     lambda n: u"<Y(if<Snd,'0>=br('1,<Snd,<FstSnd,<Snd,'1>->ε>*)),'%s>ε" % n),

    ('t + u * t', u"((\\x.\\f.+[x,f x])t)(\\x.*[u,x])", 'l',
     lambda t, u: u"((\\x.\\f.+[x,f x])%s)(\\x.*[%s,x])" % (t, u)),

    ('t + u', u"(\\f.\\x.f x)(\\x.+[t,x])u", 'l',
     lambda t, u: u"(\\f.\\x.f x)(\\x.+[%s,x])%s" % (t, u)),
    ('t!', u"(\\g.g t)(Y(\\f.\\n.if(=[n,0])then(1)else(*[n,f(-[n,1])])))", 'l',
     lambda t: u"(\\g.g%s)(Y(\\f.\\n.if(=[n,0])then(1)else(*[n,f(-[n,1])])))" % t),

    ('fib t', u"(\\g.g t)(Y(\\f.\\n.if(=[n,0])then(1)else(if(=[n,1])then(1)else(+[f(-[n,1]), f(-[n,2])]))))", 'l',
     lambda t: u"(\\g.g%s)(Y(\\f.\\n.if(=[n,0])then(1)else(if(=[n,1])then(1)else(+[f(-[n,1]), f(-[n,2])]))))" % t),
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
    return LIBRARY[int(i) - 1][3], LIBRARY[int(i) - 1][2]
