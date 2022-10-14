import argparse
import warnings
from pathlib import Path

import pandas as pd
from asreview import ASReviewData
from asreview.data.base import load_data


def _check_order_arg(order):
    allowed_orders = ["riu", "rui", "uri", "uir", "iru", "iur"]
    if order not in allowed_orders:
        raise ValueError(
            f"An unsupported order was given with --priority, choose one of the following: {allowed_orders}"
        )

    return


def _check_resolve_arg(resolve):
    allowed_resolve = ["continue", "abort", "keep"]
    if resolve not in allowed_resolve:
        raise ValueError(
            f"An unsupported method for conflict resolving was given with --conflict_resolve, choose one "
            f"of the following: {allowed_resolve}"
        )

    return


def _check_suffix(input_files, output_file):
    # Also raises ValueError on URLs that do not end with a file extension
    suffixes = [Path(item).suffix for item in input_files if item is not None]
    suffixes.append(Path(output_file).suffix)

    set_ris = {'.txt', '.ris'}
    set_tabular = {'.csv', '.tab', '.tsv', '.xlsx'}
    set_suffixes = set(suffixes)

    if len(set(suffixes)) > 1:
        if not (set_suffixes.issubset(set_ris) or set_suffixes.issubset(set_tabular)):
            raise ValueError(
                "Several file types were given, all input files as well as the output file should be of the same type."
            )


def _check_label_errors(as_lab, path_lab):
    if as_lab is not None:
        if as_lab.labels is None:
            warnings.warn(
                f"No labels were found in '{path_lab}', continuing with its records marked as "
                f"unlabeled. If this is not correct, check if your data format complies with: "
                f"https://asreview.readthedocs.io/en/latest/data_format.html"
            )

    return


def _append_df(list_df, as_obj, label):
    # retrieve part of dataframe with label -1, 0 or 1
    df_slice = as_obj.df[as_obj.labels == label].reset_index(drop=True)

    if not df_slice.empty:
        list_df.append(df_slice)

    return


def _concat_label(list_df, label, pid="doi"):
    # if there are any dataframes with the given label, concatenate and drop duplicates on pid and title/abstract
    if list_df:
        df_all = pd.concat(list_df).reset_index(drop=True)
        df_all["included"] = label
        n_total = len(df_all)

        df_all = ASReviewData(df=df_all).drop_duplicates(pid=pid).reset_index(drop=True)

        n_total_dedup = n_total - len(df_all)
        print(
            f"Detected {n_total} records with label '{label}', from which {n_total_dedup} duplicate records with the "
            f"same label were removed."
        )
    else:
        df_all = pd.DataFrame()

    return df_all


def compose(output_file, input_files, pid="doi", order="riu", resolve="continue"):
    # check whether valid order and conflict resolve arguments are given
    _check_order_arg(order)
    _check_resolve_arg(resolve)

    # check whether all input has the same file extension
    _check_suffix(input_files, output_file)

    # load all input files and URLs into ASReviewData objects, fill with None if input was not specified
    as_rel, as_irr, as_lab, as_unl = [
        load_data(item) if item is not None else None for item in input_files
    ]

    # check whether input files are correctly labeled
    _check_label_errors(as_lab, input_files[2])

    # create lists to append dataframes with a specific label to
    list_df_rel, list_df_irr, list_df_unl = [], [], []

    # split labeled input data in relevant, irrelevant and unlabeled and add to list of dataframes for that label
    if as_lab is not None:
        if as_lab.labels is not None:
            _append_df(list_df_rel, as_lab, 1)
            _append_df(list_df_irr, as_lab, 0)
            _append_df(list_df_unl, as_lab, -1)
        else:
            list_df_unl.append(as_lab.df)

    # add dataframe to list of dataframes for that label
    if as_rel is not None:
        list_df_rel.append(as_rel.df)
    if as_irr is not None:
        list_df_irr.append(as_irr.df)
    if as_unl is not None:
        list_df_unl.append(as_unl.df)

    # concatenate all dataframes with the same label, drop duplicates and map them in a dictionary
    dict_dfs = {
        "r": _concat_label(list_df_rel, 1, pid),
        "i": _concat_label(list_df_irr, 0, pid),
        "u": _concat_label(list_df_unl, -1, pid),
    }

    # map letters to corresponding term
    dict_terms = {"r": "relevant", "i": "irrelevant", "u": "unlabeled"}

    # concatenate in specified order, only the first duplicate entry is kept
    as_conflict = ASReviewData(
        df=pd.concat(
            [dict_dfs[order[0]], dict_dfs[order[1]], dict_dfs[order[2]]]
        ).reset_index(drop=True)
    )

    # check for label conflicts
    df_conflicting_dups = as_conflict.df[as_conflict.duplicated(pid)]
    as_conflicts_only = ASReviewData(df=df_conflicting_dups.reset_index(drop=True))
    if len(df_conflicting_dups) > 0:
        # create a dataframe with the relevant info for the user
        if pid in as_conflicts_only.df.columns:
            df_info_conflicts = pd.DataFrame(
                {
                    pid: as_conflicts_only.df[pid].fillna(""),
                    "Title": as_conflicts_only.title,
                    "Abstract": as_conflicts_only.abstract,
                }
            )
        else:
            df_info_conflicts = pd.DataFrame(
                {
                    "Title": as_conflicts_only.title,
                    "Abstract": as_conflicts_only.abstract,
                }
            )

        # pandas settings to print properly
        with pd.option_context(
            "display.max_rows",
            None,
            "display.max_columns",
            3,
            "max_colwidth",
            40,
            "display.width",
            500,
            "display.colheader_justify",
            "left"
        ):
            print(
                f"\nSome records have inconsistent labels in the input files. This may be intentional because you are "
                f"trying to overwrite labels in an input file with labels from another input file. However, "
                f"it may also be because some records are unintentionally labeled inconsistently.\n\n"
                f"The following records have inconsistent labels in the input files:\n"
                f"{df_info_conflicts}\n"
            )

        if resolve == "abort":
            raise ValueError("Abort composing because inconsistent labels were found.")

        elif resolve == "continue":
            warnings.warn(
                f"Continuing, keeping one label for records with inconsistent labels, keeping labels using the "
                f"following priority:\n1. {dict_terms[order[0]]}\n2. {dict_terms[order[1]]}\n3. {dict_terms[order[2]]}"
            )
            df_composed = as_conflict.drop_duplicates(pid=pid).reset_index(drop=True)

        elif resolve == "keep":
            warnings.warn(
                f"Continuing, keeping all labels for duplicate records with inconsistent labels."
            )
            df_composed = as_conflict.df

    else:
        df_composed = as_conflict.df

    # move included column to the end of dataframe
    included = df_composed.pop("included")
    df_composed = df_composed.assign(included=included)

    # prepare collected labels to pass to the output file
    labels = [[index, row["included"]] for index, row in df_composed.iterrows()]

    # pass the new labels to the output file
    as_composed = ASReviewData(df=df_composed)
    as_composed.to_file(output_file, labels=labels)


def _parse_arguments_compose():
    parser = argparse.ArgumentParser(prog="ASReview merge data")
    parser.add_argument("output_path", type=str, help="The output file path.")
    parser.add_argument(
        "--relevant", "-r", type=str, help="A dataset with relevant records."
    )
    parser.add_argument(
        "--irrelevant", "-i", type=str, help="A dataset with irrelevant records."
    )
    parser.add_argument("--labeled", "-l", type=str, help="A labeled dataset.")
    parser.add_argument("--unlabeled", "-u", type=str, help="An unlabeled dataset.")
    parser.add_argument(
        "--priority",
        "-p",
        type=str,
        default="riu",
        help="Hierarchy of labels in case of duplicates." "Default: riu.",
    )
    parser.add_argument(
        "--conflict_resolve",
        "-c",
        type=str,
        default="continue",
        help="Method for dealing with " "conflicting labels.",
    )
    parser.add_argument(
        "--pid",
        type=str,
        default="doi",
        help="Persistent identifier used for deduplication. " "Default: doi.",
    )
    return parser
