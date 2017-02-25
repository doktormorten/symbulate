import numpy as np

from math import floor
from copy import deepcopy

from .probability_space import ArbitrarySpace
from .random_variables import RV
from .results import RandomProcessResults
from .utils import is_scalar, is_vector, get_dimension

class TimeIndex:

    def __init__(self, fs=1):
        self.fs = fs

class RandomProcess:

    def __init__(self, probSpace, timeIndex, fun=lambda x, t: None):
        self.probSpace = probSpace
        self.timeIndex = timeIndex
        self.fun = fun

    def draw(self):
        seed = np.random.randint(1e9)
        def f(t):
            if self[t] is None:
                raise Exception("RandomProcess is not defined at time %s." % str(t))
            elif is_scalar(self[t]):
                return self[t]
            elif isinstance(self[t], RV):
                np.random.seed(seed)
                return self[t].draw()
            else:
                raise Exception("RandomProcess at time t must be a RV.")
        return f

    def sim(self, n):
        return RandomProcessResults([self.draw() for _ in range(n)], self.timeIndex)

    def __getitem__(self, t):
        fun_copy = deepcopy(self.fun)
        if is_scalar(t):
            return RV(self.probSpace, lambda x: fun_copy(x, t))
        elif isinstance(t, RV):
            return RV(self.probSpace, lambda x: fun_copy(x, t.fun(x)))
    
    def __setitem__(self, t, value):
        # copy existing function to use inside redefined function
        fun_copy = deepcopy(self.fun)
        if is_scalar(value):
            def fun_new(x, s):
                if s == t:
                    return value
                else:
                    return fun_copy(x, s)
        elif isinstance(value, RV):
            def fun_new(x, s):
                if s == t:
                    return value.fun(x)
                else:
                    return fun_copy(x, s)
        else:
            raise Exception("The value of the process at any time t must be a RV.")
        self.fun = fun_new

    def apply(self, function):
        def fun(x, t):
            return function(self.fun(x, t))
        return RandomProcess(self.probSpace, self.timeIndex, fun)

    def check_same_probSpace(self, other):
        if is_scalar(other):
            return
        else:
            self.probSpace.check_same(other.probSpace)

    # The code for most operations (+, -, *, /, ...) is the
    # same, except for the operation itself. The following 
    # factory function takes in the the operation and 
    # generates the code to perform that operation.
    def _operation_factory(self, op):

        def op_fun(self, other):
            self.check_same_probSpace(other)
            if is_scalar(other):
                def fun(x, t):
                    return op(self.fun(x, t), other)
            elif isinstance(other, RV):
                def fun(x, t):
                    return op(self.fun(x, t), other)
            elif isinstance(other, RandomProcess):
                def fun(x, t):
                    return op(self.fun(x, t), other.fun(x, t))
            return RandomProcess(self.probSpace, self.timeIndex, fun)

        return op_fun

    # e.g., X(t) + Y(t) or X(t) + Y or X(t) + 3
    def __add__(self, other):
        op_fun = self._operation_factory(lambda x, y: x + y)
        return op_fun(self, other)

    def __radd__(self, other):
        return self.__add__(other)

    # e.g., X(t) - Y(t) or X(t) - Y or X(t) - 3
    def __sub__(self, other):
        op_fun = self._operation_factory(lambda x, y: x - y)
        return op_fun(self, other)

    def __rsub__(self, other):
        return -1 * self.__sub__(other)

    def __neg__(self):
        return -1 * self

    # e.g., X(t) * Y(t) or X(t) * Y or X * 2
    def __mul__(self, other):
        op_fun = self._operation_factory(lambda x, y: x * y)
        return op_fun(self, other)
    
    def __rmul__(self, other):
        return self.__mul__(other)

    # e.g., X(t) / Y(t) or X(t) / Y or X / 2
    def __truediv__(self, other):
        op_fun = self._operation_factory(lambda x, y: x / y)
        return op_fun(self, other)

    def __rtruediv__(self, other):
        op_fun = self._operation_factory(lambda x, y: y / x)
        return op_fun(self, other)

    # e.g., X(t) ** Y(t) or X(t) ** Y or X(t) ** 2
    def __pow__(self, other):
        op_fun = self._operation_factory(lambda x, y: x ** y)
        return op_fun(self, other)

    def __rpow__(self, other):
        op_fun = self._operation_factory(lambda x, y: y ** x)
        return op_fun(self, other)

    # Alternative notation for powers: e.g., X ^ 2
    def __xor__(self, other):
        return self.__pow__(other)
    
    # Alternative notation for powers: e.g., 2 ^ X
    def __rxor__(self, other):
        return self.__rpow__(other)

