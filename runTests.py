import unittest

from UnitTesting.AlarmTests import *
from UnitTesting.DatabseTests import *
from UnitTesting.utilitiesTests import *
from UnitTesting.LEDControllerTests import *


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-V', dest="verbosity", action='count', default=0, help="Increase the level of logging output")
    args = parser.parse_args()
    verbosity = ['-v'] * args.verbosity

    pytest_args = [__file__, '-l'] + verbosity
    pytest.main(pytest_args)

    # unittest.main() - pytest runs these as well.