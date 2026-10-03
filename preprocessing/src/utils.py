import os
import logging


def list_rr_files(directory):
    """Lists all RR files in a directory."""
    files = sorted(
        [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if f.endswith(".txt")
        ]
    )
    logging.info(f"{len(files)} file(s) found in {directory}")
    return files


def get_output_path(file, output_dir, control_dir, test_dir, suffix):
    """
    Returns the output path for a processed file.
    """
    dir = control_dir if control_dir in file else test_dir
    output_dir = os.path.join(output_dir, os.path.basename(dir))
    output_file = os.path.join(
        output_dir, os.path.basename(file).replace(".txt", suffix)
    )
    return output_file


def get_relative_output_path(output_dir, group_dir):
    path = os.path.join(
        os.path.relpath(output_dir), os.path.basename(group_dir)
    )
    return path


def ask_user(question=None):
    while True:
        response = (
            input("Do you want to continue?" if question is None else question + "(y/n): ")
            .strip()
            .lower()
        )
        if response in ["y", "n"]:
            return response
        print("Invalid input! Type 'y' to continue or 'n' to exit.")