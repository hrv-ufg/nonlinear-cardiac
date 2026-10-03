import numpy as np
import logging
import os
from config import CONTROL_DIR, TEST_DIR


def load_rr_intervals(file_path):
    """Loads RR intervals from a file."""
    try:
        logging.debug(f"Loading file: {file_path}")
        data = np.loadtxt(file_path, dtype=float, delimiter=" ", encoding="ISO-8859-1")
        logging.debug(f"File loaded successfully: {file_path}")

        # If the data has only one column, return it directly
        if data.ndim == 1:  # Case where there is only one column
            logging.debug("File contains only one column.")
            return data / 1000 if max(data) > 100 else data

        else:
            # If there are two columns, return only the second column (RR intervals)
            logging.debug("File contains two columns.")
            return data[:, 1]  # Return the second column (RR intervals)

    except Exception as e:
        logging.error(f"Error loading file {file_path}: {e}")
        return None


def save_rr_intervals(file_path, data):
    """Saves the processed RR intervals to a file."""
    try:
        logging.debug(f"Saving file: {file_path}")
        np.savetxt(file_path, data, fmt="%.3f")
        logging.debug(f"File saved successfully: {file_path}")
    except Exception as e:
        logging.error(f"Error saving file {file_path}: {e}")


def save_removed_files(removed_files, param, threshold, output_dir, file_name):
    """Saves the removed files to a file."""
    title = f"{'=' * 10} LIST OF FILES REMOVED WITH {param.upper()} BELOW {threshold:.1f} {'=' * 10}\n\n"

    output_file = os.path.join(output_dir, file_name)
    logging.debug(f"Saving removed files list: {output_file}")

    count_control = sum(CONTROL_DIR in file for file in removed_files.keys())
    count_test = sum(TEST_DIR in file for file in removed_files.keys())

    first_subtitle = (
        f"Number of files removed: {CONTROL_DIR}: {count_control} "
        f"and {TEST_DIR}: {count_test}\n\n"
    )
    second_subtitle = f"Format: X.File Name | {param.capitalize()}\n\n"

    with open(output_file, "w") as f:
        f.write(title)
        f.write(first_subtitle)
        f.write(second_subtitle)
        for file, quality in removed_files.items():
            f.write(file)
            f.write(f" | {quality:.2f}\n")

    logging.debug(f"Removed files list successfully saved to: {output_file}")