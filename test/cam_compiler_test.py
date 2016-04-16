# coding=utf-8

import unittest

import cam_compiler


class TestCAM(unittest.TestCase):
    def test_compiler(self):
        exprs = [
            '(\\x.((\\z.zx2)*))3',
            '(\\x.((\\z.z[x,2])*))3'
        ]

        res = [
            u"<Λ(<Λ(<<Snd,FstSnd>ε,'2>ε),Λ(Snd*)>ε),'3>ε",
            u"<Λ(<Λ(<Snd, <FstSnd , '2>>ε),Λ(Snd*)>ε),'3>ε"
        ]

        for expr, r in zip(exprs, res):
            self.assertEqual(cam_compiler.compile_expr(expr).replace(' ', ''), r.replace(' ', ''))


if __name__ == "__main__":
    unittest.main()
