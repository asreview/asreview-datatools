import argparse

from asreview.data import ASReviewData


def convert(input_path, output_path):
    # read data in ASReview data object
    asdata = ASReviewData.from_file(input_path)

    asdata.to_file(output_path)


def _parse_arguments_convert():
    parser = argparse.ArgumentParser(prog="asreview data convert")
    parser.add_argument("input_path", type=str, help="The file path of the dataset.")
    parser.add_argument("output_path", type=str, help="The file path of the dataset.")
    return parser
