import unittest

from UnitTesting.AlarmTests import *
from UnitTesting.DatabseTests import *
from UnitTesting.utilitiesTests import *
from UnitTesting.LEDControllerTests import *


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-V', dest="verbosity", action='count', default=0, help="Increase the level of logging output")
    parser.add_argument('--cov', default=None, help='--cov argument to pass to pytest')
    args = parser.parse_args()
    verbosity = ['-v'] * args.verbosity

    pytest_args = [__file__, '-l'] + verbosity

    if args.cov:
        pytest_args.append('--cov=' + args.cov)

    result = pytest.main(pytest_args)
    sys.exit(result)
