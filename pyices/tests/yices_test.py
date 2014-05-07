import unittest

from pyices.expression import YicesExpression
from pyices.context import YicesContext
import pyices.fix_env


class PyicesTests(unittest.TestCase):
    def testConversion(self):
        x = YicesExpression.from_real_var("x")
        y = YicesExpression.from_real_var("y")
        z = YicesExpression.from_real_var("z")

        expr = (x == y + z) & (z >= 10) & (y >= 5)

        ctx = YicesContext.from_term(expr)
        sat = ctx.check_sat()

        self.assertEquals(
            sat,
            True
        )

        x_val = ctx.get_real_value("x")
        y_val = ctx.get_real_value("y")
        z_val = ctx.get_real_value("z")

        self.assertEquals(
            x_val, y_val + z_val
        )

        self.assertEquals(
            z_val >= 10, True
        )

        self.assertEquals(
            y_val >= 5, True
        )

    def testBooleanVariables(self):
        x = YicesExpression.from_real_var("x")
        x1 = YicesExpression.from_real_var("x1")

        s1 = YicesExpression.from_bool_var("s1")

        expr = (x < 5) & (
            (
                (x1 == x + 1) & s1
            ) | (
                (x1 == 10) & (~s1)
            )
        ) & (x1 > 6)

        ctx = YicesContext.from_term(expr)
        sat = ctx.check_sat()

        self.assertEquals(
            sat, True
        )

        self.assertEquals(
            ctx.get_bool_value("s1"), False
        )

    def testGt(self):
        z = YicesExpression.from_real_var("test")
        expr = z > 0

        ctx = YicesContext.from_term(expr)

        ctx.push()
        ctx.pop()

        sat = ctx.check_sat()

        self.assertEquals(
            sat, True
        )

        self.assertEquals(
            ctx.get_real_value("test") > 0, True
        )

    def testPushPop(self):
        """
        Test <push> and <pop> functionality of yices context object.
        """
        z = YicesExpression.from_real_var("hello", namespace='x__')
        ctx = YicesContext()
        ctx.add_assertion(z >= 0)
        ctx.push()
        ctx.add_assertion(z == 100)

        sat = ctx.check_sat()

        self.assertEquals(
            sat, True
        )
        self.assertEquals(
            ctx.get_real_value("hello"), 100
        )

        ctx.pop()
        ctx.push()

        ctx.add_assertion(z == 200)

        sat = ctx.check_sat()

        self.assertEquals(
            sat, True
        )
        self.assertEquals(
            ctx.get_real_value("hello"), 200
        )

        ctx.pop()
        ctx.add_assertion(z < -1)

        sat = ctx.check_sat()

        self.assertEquals(
            sat, False
        )

    def testPushPop2(self):
        z = YicesExpression.from_real_var("z", namespace='x_2')
        y = YicesExpression.from_real_var("y", namespace='x_2')
        ctx = YicesContext()
        ctx.add_assertion(z >= 0)
        ctx.add_assertion(z <= 10)
        ctx.add_assertion(z + y == 5)

        ctx.push()

        ctx.add_assertion(y >= 3)
        ctx.add_assertion(y <= 3)

        self.assertEquals(
            ctx.check_sat(), True
        )

        self.assertEquals(
            ctx.get_real_value("z"), 2
        )

        self.assertEquals(
            ctx.get_real_value("y"), 3
        )

        ctx.pop()
        ctx.push()

        ctx.add_assertion(y >= 10)
        ctx.add_assertion(z >= 2)

        self.assertEquals(
            ctx.check_sat(), False
        )

        ctx.pop()
        ctx.push()

        ctx.add_assertion(y <= 4)
        ctx.add_assertion(y >= 4)

        self.assertEquals(
            ctx.check_sat(), True
        )

        self.assertEquals(
             ctx.get_real_value("z"), 1
        )

        self.assertEquals(
             ctx.get_real_value("y"), 4
        )

        ctx.pop()

if __name__ == '__main__':
    unittest.main()
