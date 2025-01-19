import argparse

from asreview.data import load_data
from asreview.entry_points import BaseEntryPoint

from asreviewcontrib.datatools import __version__
from asreviewcontrib.datatools.compose import _parse_arguments_compose
from asreviewcontrib.datatools.compose import compose
from asreviewcontrib.datatools.convert import _parse_arguments_convert
from asreviewcontrib.datatools.convert import convert
from asreviewcontrib.datatools.dedup import deduplicate_data
from asreviewcontrib.datatools.describe import _parse_arguments_describe
from asreviewcontrib.datatools.describe import describe
from asreviewcontrib.datatools.sample import _parse_arguments_sample
from asreviewcontrib.datatools.sample import sample
from asreviewcontrib.datatools.snowball import _parse_arguments_snowball
from asreviewcontrib.datatools.snowball import snowball
from asreviewcontrib.datatools.stack import _parse_arguments_vstack
from asreviewcontrib.datatools.stack import vstack

DATATOOLS = ["describe", "dedup", "convert", "compose", "vstack", "snowball", "sample"]


class DataEntryPoint(BaseEntryPoint):
    description = "Home of all data tools for ASReview."
    extension_name = "asreview-datatools"

    def __init__(self):
        from asreviewcontrib.datatools.__init__ import __version__

        super().__init__()

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
                dedup_parser = argparse.ArgumentParser(prog="asreview data dedup")
                dedup_parser.add_argument(
                    "input_path", type=str, help="The file path of the dataset."
                )
                dedup_parser.add_argument(
                    "--output_path",
                    "-o",
                    default=None,
                    type=str,
                    help="The file path of the dataset.",
                )
                dedup_parser.add_argument(
                    "--pid",
                    default="doi",
                    type=str,
                    help="Persistent identifier used for deduplication. Default: doi.",
                )
                dedup_parser.add_argument(
                    "--similar",
                    action='store_true',
                    help="Drop similar records.",
                )
                dedup_parser.add_argument(
                    "--threshold",
                    default=0.98,
                    type=float,
                    help="Similarity threshold for deduplication. Default: 0.98.",
                )
                dedup_parser.add_argument(
                    "--title_only",
                    action='store_true',
                    help="Use only title for deduplication.",
                )
                dedup_parser.add_argument(
                    "--stopwords",
                    action='store_true',
                    help="Ignore stopwords for deduplication, focusing on main words.",
                )
                dedup_parser.add_argument(
                    "--strict",
                    action='store_true',
                    help="Use a more strict similarity for deduplication.",
                )
                dedup_parser.add_argument(
                    "--stopwords_language",
                    default="english",
                    type=str,
                    help="Language for stopwords. Default: english.",
                )
                dedup_parser.add_argument(
                    "--verbose",
                    action='store_true',
                    help="Print verbose output.",
                )

                args_dedup = dedup_parser.parse_args(argv[1:])

                # read data in ASReview data object
                asdata = load_data(args_dedup.input_path)
                deduplicate_data(asdata, args_dedup)

            if argv[0] == "compose":
                args_compose_parser = _parse_arguments_compose()
                args_compose = args_compose_parser.parse_args(argv[1:])
                compose(
                    args_compose.output_path,
                    args_compose.relevant,
                    args_compose.irrelevant,
                    args_compose.labeled,
                    args_compose.unlabeled,
                    pid=args_compose.pid,
                    order=args_compose.hierarchy,
                    resolve=args_compose.conflict_resolve,
                )
            if argv[0] == "snowball":
                args_snowballing_parser = _parse_arguments_snowball()
                args_snowballing = vars(args_snowballing_parser.parse_args(argv[1:]))
                snowball(**args_snowballing)
            if argv[0] == "sample":
                args_sample_parser = _parse_arguments_sample()
                args_sample = vars(args_sample_parser.parse_args(argv[1:]))
                sample(**args_sample)
            if argv[0] == "vstack":
                args_vstack_parser = _parse_arguments_vstack()
                args_vstack = args_vstack_parser.parse_args(argv[1:])
                vstack(args_vstack.output_path, args_vstack.datasets)

        # Print help message if subcommand not given or incorrect
        else:
            parser = argparse.ArgumentParser(
                prog="asreview data",
                formatter_class=argparse.RawTextHelpFormatter,
                description="Tools for data preprocessing for ASReview.",
            )
            parser.add_argument(
                "subcommand",
                nargs="?",
                default=None,
                help=f"The datatool to launch. Available commands:\n\n" f"{DATATOOLS}",
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
