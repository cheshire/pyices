import ctypes

import yices_lib as libyices
from yices_lib import String
from yices_utils import c_stderr
import fix_env

# Yices constants
STATUS_SAT = 3
STATUS_UNSAT = 4

class YicesContext(object):
    def __init__(self, namespace=None):
        self._yices_ctx = libyices.yices_new_context(None)
        self.namespace = namespace
        self._model = None

    @classmethod
    def from_term(self, term):
        """
        :type term: YicesExpression instance
        """
        out = YicesContext(namespace=term.namespace)
        out.add_assertion(term)
        return out

    def add_assertion(self, term):
        """
        :type term: YicesExpression instance
        """
        code = libyices.yices_assert_formula(
            self._yices_ctx,
            term._yices_term
        )
        if self.namespace is not None:
            assert self.namespace == term.namespace
        else:
            self.namespace = term.namespace
        assert code == 0, "Yices returned non-zero code"

    def get_bool_value(self, var_name):
        return self._get_yices_value(
            var_name,
            ctypes.c_bool(),
            libyices.yices_get_bool_value
        )

    def get_real_value(self, var_name):
        return self._get_yices_value(
            var_name,
            ctypes.c_double(),
            libyices.yices_get_double_value
        )

    def _get_yices_value(self, var_name, var_type, getter_func):
        term = self._get_term_by_name(var_name)
        out = var_type
        status = getter_func(
            self._model,
            term,
            ctypes.byref(out)
        )
        assert status == 0, "Failed to read the variable from the model"
        return out.value

    def _get_term_by_name(self, var_name):
        if not self.status == STATUS_SAT:
            raise LookupError("Satisfiability was not checked yet.\
             Call .check_sat() first")

        out = libyices.yices_get_term_by_name(
            String(self.namespace + var_name)
        )

        assert out > 0, "Variable not found"
        return out

    @property
    def is_unsat(self):
        return self.status == STATUS_UNSAT

    @property
    def status(self):
        return libyices.yices_context_status(self._yices_ctx)

    def check_sat(self):
        """
        Check satisfiability of the given expression.

        Generates a model.

        :rtype: bool
        """
        out = libyices.yices_check_context(self._yices_ctx, None)

        if self._model is not None:
            libyices.yices_free_model(self._model)
            self._model = None

        if out == STATUS_SAT:
            self._model = libyices.yices_get_model(self._yices_ctx, 1)
            return True
        elif out == STATUS_UNSAT:
            return False
        else:
            raise Exception("Yices has returned unexpected code")

    def push(self):
        assert libyices.yices_push(self._yices_ctx) == 0

    def pop(self):
        assert libyices.yices_pop(self._yices_ctx) == 0

    def model2stderr(self):
        """
        Debugging helper.

        Prints model to stderr (Provided it exists.)
        """
        libyices.yices_print_model(c_stderr, self._model)

    def del_context(self):
        libyices.yices_free_context(self._yices_ctx)
