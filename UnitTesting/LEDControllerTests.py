from LEDController import LEDController

import pytest
import logging


FORMAT = "[%(funcName)20s] %(message)s"
logging.basicConfig(format=FORMAT)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

margin_of_error = 1

test_output_percentages = [0, 1, 20, 79, 85, 90, 95, 99, 100]


@pytest.mark.parametrize("value", test_output_percentages)
def test_scale_yields_reasonable_values(value):
    scaled = LEDController._scale(value)
    logger.debug("Scaled: " + str(scaled))
    assert 0 <= scaled <= 255


@pytest.mark.parametrize("value", test_output_percentages)
def test_led_controller_sets_led(value):
    controller = LEDController()
    assert 0 == controller.value_raw
    expected = LEDController._scale(value)
    controller.value = value

    assert expected == controller.value_raw


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-V",
        dest="verbosity",
        action="count",
        default=0,
        help="Increase the level of logging output",
    )
    args = parser.parse_args()
    verbosity = ["-v"] * args.verbosity

    pytest_args = [__file__, "-l"] + verbosity
    pytest.main(pytest_args)
