import atexit

import yices_lib as libyices
from yices_lib import String
from yices_utils import c_stderr
from context import YicesContext
import fix_env

class YicesExpression(object):
    """
    Simple python wrapper around Yices.
    """
    def __init__(self, yices_term, namespace=''):
        """
        :param yices_term: Yices C term which is wrapped.
        :type yices_term: libyices.term_t
        """
        # Negative numbers are used to report errors.
        assert yices_term > 0
        self.namespace = namespace
        self._yices_term = yices_term

    # Factory methods
    # ===============

    @classmethod
    def as_true_const(cls, namespace=''):
        return YicesExpression(libyices.yices_true(), namespace=namespace)

    @classmethod
    def from_bool_var(cls, var_name, namespace='', fresh=False):
        """
        Returns YicesExpression wrapping a fresh boolean variable.

        :param var_name: Name assigned to the boolean variable.
        :type var_name: str

        :param fresh: Flag to create a fresh variable
        instead of re-using an old one.
        :type fresh: bool

        :rtype: YicesExpression instance
        """
        return cls._from_var(
            var_name,
            libyices.yices_bool_type(),
            fresh,
            namespace=namespace,
        )

    @classmethod
    def from_real_var(cls, var_name, namespace='', fresh=False):
        """
        Returns YicesExpression wrapping a rational variable.

        :param var_name: Name assigned to the variable .
        :type var_name: str

        :param fresh: Flag to create a fresh variable
        instead of re-using an old one.
        :type fresh: bool

        :rtype: YicesExpression instance
        """
        return cls._from_var(
            var_name,
            libyices.yices_real_type(),
            fresh,
            namespace=namespace
        )

    @classmethod
    def _from_var(cls, var_name, var_type, fresh=False, namespace=''):
        """
        Helper method for <from_real_val> and <from_bool_var>.

        See their signatures.
        """
        c_str_var_name = String(namespace + var_name)

        if not fresh:  # Can re-use already existing variable.
            term = libyices.yices_get_term_by_name(c_str_var_name)
            if term >= 0:

                # Return already existing term if found.
                return YicesExpression(term, namespace=namespace)
                # return YicesExpression(cls.symbol_table[var_name])

        term = libyices.yices_new_uninterpreted_term(
            var_type
        )

        # cls.symbol_table[var_name] = term
        check = libyices.yices_set_term_name(
            term, c_str_var_name
        )
        assert check >= 0

        return YicesExpression(term, namespace=namespace)

    @classmethod
    def from_real_constant(cls, value, namespace=''):
        """
        Returns YicesExpression wrapping a rational value.

        :param value: Value assigned to the constant.
        :type value: float

        :rtype: YicesExpression instance
        """
        return YicesExpression(
            libyices.yices_parse_float(String(str(value))),
            namespace=namespace,
        )

    def to_context(self):
        return YicesContext.from_term(self)

    def __neg__(self):
        return YicesExpression(
            libyices.yices_neg(self._yices_term),
            namespace=self.namespace
        )

    def __invert__(self):
        return YicesExpression(
            libyices.yices_not(self._yices_term),
            namespace=self.namespace
        )

    def dispatch_func(self, o, func):
        if isinstance(o, (int, float)):
            o_term = libyices.yices_parse_float(String(str(o)))
        else:
            o_term = o._yices_term

        return YicesExpression(
            func(self._yices_term, o_term),
            namespace=self.namespace,
        )

    def __add__(self, o):
        return self.dispatch_func(o, libyices.yices_add)

    def __sub__(self, o):
        return self.dispatch_func(o, libyices.yices_sub)

    def __mul__(self, o):
        return self.dispatch_func(o, libyices.yices_mul)

    def __and__(self, o):
        return self.dispatch_func(o, libyices.yices_and2)

    def __or__(self, o):
        return self.dispatch_func(o, libyices.yices_xor2)

    def __eq__(self, o):
        return self.dispatch_func(o, libyices.yices_eq)

    def __le__(self, o):
        return self.dispatch_func(o, libyices.yices_arith_leq_atom)

    def __lt__(self, o):
        return self.dispatch_func(o, libyices.yices_arith_lt_atom)

    def __gt__(self, o):
        return self.dispatch_func(o, libyices.yices_arith_gt_atom)

    def __ge__(self, o):
        return self.dispatch_func(o, libyices.yices_arith_geq_atom)

    def term2stderr(self, width=80, height=20, offset=0):
        """
        Debugging helper.

        Prints the term to the <stderr> stream.
        """
        libyices.yices_pp_term(
            c_stderr,
            self._yices_term,
            width,
            height,
            offset,
        )

# Initialization
def init():
    if not getattr(init, '_initialized', False):
        libyices.yices_init()
    init._initialized = True

def reset_yices():
    libyices.yices_reset()

init()

@atexit.register
def cleanup():
    libyices.yices_exit()

