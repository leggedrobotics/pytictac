from pytictac import Timer


def func(x):
    return x * 2


# Compute
with Timer("func2"):
    func(2)
