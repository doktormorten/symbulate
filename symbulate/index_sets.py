class IndexSet:

    def __init__(self):
        return

    def __getitem__(self, t):
        if t in self:
            return t
        else:
            raise KeyError("Time %.2f not in index set." % t)
        
    def __contains__(self, value):
        return False

    def check_same(self, index):
        """Checks whether the current IndexSet matches another.

        Args:
          index: Another IndexSet

        Raises:
          Exception: Two index sets do not match.
        """
        return


class Reals(IndexSet):

    def __init__(self):
        return

    def __contains__(self, value):
        return isinstance(value, (int, float))

    def check_same(self, index):
        if not isinstance(index, Reals):
            raise Exception("Index sets do not match.")


class Naturals(IndexSet):

    def __init__(self):
        return

    def __contains__(self, value):
        return value.is_integer() and value >= 0

    def check_same(self, index):
        if not isinstance(index, Integers):
            raise Exception("Index sets do not match.")
    

class DiscreteTimeSequence(IndexSet):

    def __init__(self, fs):
        self.fs = fs

    def __getitem__(self, n):
        return n / self.fs
        
    def __contains__(self, value):
        return (value * self.fs).is_integer()

    def check_same(self, index):
        if not (
            isinstance(index, DiscreteTimeSequence) and
            (self.fs == index.fs)
        ):
            raise Exception("Index sets do not match.")


class Integers(DiscreteTimeSequence):

    def __init__(self):
        self.fs = 1