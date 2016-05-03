# coding=utf-8

import unittest

import cam_compiler


class TestCAM(unittest.TestCase):
    def test_compiler(self):
        exprs = [
            u'(\\x.((\\z.zx2)*))3',
            u'(\\x.((\\z.z[x,2])*))3',
            u'(\\g.g1)(Y(\\f.\\n.if(=[n,0])then(1)else(*[n,f(-[n,1])])))'
        ]

        res = [
            u"<Λ(<Λ(<<Snd,FstSnd>ε,'2>ε),Λ(Snd*)>ε),'3>ε",
            u"<Λ(<Λ(<Snd, <FstSnd , '2>>ε),Λ(Snd*)>ε),'3>ε",
            u"<Λ(<Snd,'1>ε),<Λ(Λ(if<Λ(Snd=),<Snd,'0>>εbr('1,<Λ(Snd*),<Snd,<FstSnd,<Λ(Snd-),<Snd,'1>>ε>ε>>ε))),Y(if<Λ(Snd=),<Snd,'0>>εbr('1,<Λ(Snd*),<Snd,<FstSnd,<Λ(Snd-),<Snd,'1>>ε>ε>>ε))>ε>ε"
        ]

        for expr, r in zip(exprs, res):
            self.assertEqual(cam_compiler.compile_expr(expr).replace(' ', ''), r.replace(' ', ''))


if __name__ == "__main__":
    unittest.main()
