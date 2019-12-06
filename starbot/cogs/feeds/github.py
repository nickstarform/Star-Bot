"""."""

# internal modules

# external modules

# relative modules

# global attributes
__all__ = ('test', 'main', 'Default')
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


def main():
    """
    Summary line.

    Extended description of function.

    Parameters
    ----------
    arg1 : int
        Description of arg1
    arg2 : str
        Description of arg2

    Returns
    -------
    int
        Description of return value
    """
    pass


class Default():
    """
    Cog of Owner Commands to run.

    Parameters
    ----------
    arg1 : type
        blah

    Returns
    -------
    """

    def __init__(self):
        """Initialization."""
        super().__init__()


def test():
    """Testing function for module."""
    pass


if __name__ == "__main__":
    """Directly Called."""

    print('Testing module')
    test()
    print('Test Passed')

# end of code

# end of file
