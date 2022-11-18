import argparse

from asreview.data import load_data
from asreview.entry_points import BaseEntryPoint

from asreviewcontrib.datatools.compose import _parse_arguments_compose
from asreviewcontrib.datatools.compose import compose
from asreviewcontrib.datatools.convert import _parse_arguments_convert
from asreviewcontrib.datatools.convert import convert
from asreviewcontrib.datatools.describe import _parse_arguments_describe
from asreviewcontrib.datatools.describe import describe
from asreviewcontrib.datatools.stack import _parse_arguments_vstack
from asreviewcontrib.datatools.stack import vstack

DATATOOLS = ["describe", "dedup", "convert", "compose", "vstack"]


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

                args_dedup = dedup_parser.parse_args(argv[1:])

                # read data in ASReview data object
                asdata = load_data(args_dedup.input_path)
                initial_length = len(asdata.df)

                if args_dedup.pid not in asdata.df.columns:
                    print(
                        f"Not using {args_dedup.pid} for deduplication"
                        "because there is no such data."
                    )

                # retrieve deduplicated ASReview data object
                asdata.drop_duplicates(pid=args_dedup.pid, inplace=True)

                # count duplicates
                n_dup = initial_length - len(asdata.df)

                if args_dedup.output_path:
                    asdata.to_file(args_dedup.output_path)
                    print(
                        f"Removed {n_dup} duplicates from dataset with {initial_length} records."
                    )
                else:
                    print(
                        f"Found {n_dup} duplicates in dataset with {initial_length} records."
                    )
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

            if argv[0] == "vstack":
                args_vstack_parser = _parse_arguments_vstack()
                args_vstack = args_vstack_parser.parse_args(argv[1:])
                vstack(args_stack.output_path, args_stack.datasets)

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
