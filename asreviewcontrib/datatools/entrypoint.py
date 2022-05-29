import argparse

from asreview.data import ASReviewData
from asreview.entry_points import BaseEntryPoint
from asreviewcontrib.datatools.describe import describe, _parse_arguments_describe
from asreviewcontrib.datatools.convert import convert, _parse_arguments_convert
from asreviewcontrib.datatools.dedup import dedup, _parse_arguments_dedup


DATATOOLS = ["describe", "dedup", "convert"]

class DataEntryPoint(BaseEntryPoint):
    description = "Home of all data tools for ASReview."
    extension_name = "asreview-datatools"

    def __init__(self):
        from asreviewcontrib.datatools.__init__ import __version__
        super(DataEntryPoint, self).__init__()

        self.version = __version__

    def execute(self, argv):

        if len(argv) > 1 and argv[0] in DATATOOLS:

            if argv[0] == "describe":
                args_describe_parser = _parse_arguments_describe()
                args_describe = vars(args_describe_parser.parse_args(argv[1:]))
                describe(**args_describe)
            if argv[0] == "convert":
                args_convert_parser = _parse_arguments_convert()
                args_convert = vars(args_convert_parser.parse_args(argv[1:]))
                convert(**args_convert)

            if argv[0] == "dedup":
                args_dedup_parser = _parse_arguments_dedup()
                args_dedup = vars(args_dedup_parser.parse_args(argv[1:]))
                dedup(**args_dedup)

        # Print help message if subcommand not given or incorrect
        else:

            parser = argparse.ArgumentParser(
                prog="asreview data",
                formatter_class=argparse.RawTextHelpFormatter,
                description="Tools for data preprocessing for ASReview."
            )
            parser.add_argument(
                "subcommand",
                nargs="?",
                default=None,
                help=f"The datatool to launch. Available commands:\n\n"
                f"{DATATOOLS}"
            )
            parser.add_argument(
                "-V",
                "--version",
                action="version",
                default=False,
                version=f"{self.extension_name}: {self.version}",
            )
            args, _ = parser.parse_known_args()

            print(args)
            # output the version
            if args.version:
                print(__version__)
                return

            parser.print_help()
