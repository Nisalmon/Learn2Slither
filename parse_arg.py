import argparse


def parse(args):
    parser = argparse.ArgumentParser(
        prog="Learn2Slyther",
        description="An agent learning to play Snake"
    )
    parser.add_argument("-session", type=int, default=1)
    parser.add_argument("-visual", type=str, choices=("on", "off"),
                        default="on")
    parser.add_argument("-dontlearn", action="store_true")
    parser.add_argument("-save", default=None, type=str)
    parser.add_argument("-load", default=None, type=str)
    parser.add_argument("-step-by-step", action="store_true")
    args = parser.parse_args()
    return args
