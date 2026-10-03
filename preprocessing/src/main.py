import os
import logging
import numpy as np
import shutil
from file_io import load_rr_intervals, save_rr_intervals, save_removed_files
from statistics_dir import (
    generate_statistics_report,
    generate_duration_and_quality_file_report,
)
from processing import (
    get_nn_intervals,
    evaluate_signal_quality,
    truncate_rr_intervals,
)
from utils import list_rr_files, get_output_path, ask_user, get_relative_output_path
from config import (
    OUTPUT_DIR,
    DENOISED_OUTPUT_DIR,
    TRUNCATED_OUTPUT_DIR,
    CONTROL_DIR,
    TEST_DIR,
    POLICY,
    LOW_RRI,
    HIGH_RRI,
    CLIP_START_LENGTH,
    QUALITY_THRESHOLD,
    MIN_LENGTH_SEG,
)
from logging_config import setup_logging


def empty_directory(directory):
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)


def create_truncated_output_dirs(truncatedOutputDir, control_dir, test_dir):
    os.makedirs(
        os.path.join(truncatedOutputDir, os.path.basename(control_dir)),
        exist_ok=True,
    )
    os.makedirs(
        os.path.join(truncatedOutputDir, os.path.basename(test_dir)),
        exist_ok=True,
    )


def process_data(
    control_dir=CONTROL_DIR,
    test_dir=TEST_DIR,
    min_length_seg=MIN_LENGTH_SEG,
    policy=POLICY,
    clip_start_length=CLIP_START_LENGTH,
    quality_threshold=QUALITY_THRESHOLD,
):

    logging.debug(
        f"Starting processing of directories: '{control_dir}' and '{test_dir}'"
    )

    # Clear the DENOISED_OUTPUT_DIR directory
    empty_directory(DENOISED_OUTPUT_DIR)

    files = []
    min_length = float("inf")
    min_file = None

    for directory in [control_dir, test_dir]:
        files.extend(list_rr_files(directory))

    if not files:
        logging.warning(
            f"No files found in directories '{control_dir}' and '{test_dir}'"
        )
        return

    removed_low_quality = {}

    for file in files[:]:
        rr_intervals = load_rr_intervals(file)

        if rr_intervals is not None:

            logging.info(f"Removing the first {clip_start_length} RRIs from the file")
            rr_intervals = rr_intervals[clip_start_length:]

            signal_quality = evaluate_signal_quality(rr_intervals)

            if signal_quality < quality_threshold:
                files.remove(file)

                # Save the file name and quality in the dictionary
                removed_low_quality[file] = round(signal_quality * 100, 2)

                logging.warning(
                    f"Low-quality signal ({signal_quality * 100:.2f}%), "
                    f"removed from the analysis: '{file}'"
                )

            else:
                logging.info(
                    f"Good-quality signal ({signal_quality * 100:.2f}%), "
                    f"kept for analysis: '{file}'"
                )

                rr_cleaned = get_nn_intervals(
                    rr_intervals, LOW_RRI, HIGH_RRI
                )

                length = np.sum(rr_cleaned)

                if length < min_length:
                    min_length = length
                    min_file = file

                output_file = get_output_path(
                    file,
                    DENOISED_OUTPUT_DIR,
                    control_dir,
                    test_dir,
                    "_denoised.txt",
                )

                save_rr_intervals(output_file, rr_cleaned)

    save_removed_files(
        removed_low_quality,
        "quality (%)",
        round((quality_threshold * 100), 1),
        DENOISED_OUTPUT_DIR,
        "removed_low_quality.txt",
    )

    min_length_minute = round((min_length / 60), 1)

    logging.info(
        f"The file with the shortest duration is '{min_file}' "
        f"with {min_length_minute} minutes"
    )

    if min_length_seg:
        min_length = min_length_seg
        min_length_minute = round((min_length / 60), 1)

    logging.info(f"Truncating signals to {min_length_minute} minutes")

    truncatedOutputDir = (
        f"{OUTPUT_DIR}/truncated_{min_length_minute}min_{policy}"
    )

    create_truncated_output_dirs(
        truncatedOutputDir, control_dir, test_dir
    )

    empty_directory(truncatedOutputDir)

    removed_low_duration = {}

    for file in files[:]:
        denoised_file = get_output_path(
            file,
            DENOISED_OUTPUT_DIR,
            control_dir,
            test_dir,
            "_denoised.txt",
        )

        rr_intervals = load_rr_intervals(denoised_file)

        rr_truncated, duration_truncated = truncate_rr_intervals(
            rr_intervals, min_length
        )

        if duration_truncated < min_length:
            logging.warning(
                f"File '{file}' removed: accumulated duration "
                f"({duration_truncated:.2f} s) is below the minimum "
                f"threshold ({min_length:.2f} s)"
            )

            removed_low_duration[file] = round(
                (duration_truncated / 60), 1
            )

            files.remove(file)

        else:
            output_file = get_output_path(
                file,
                truncatedOutputDir,
                control_dir,
                test_dir,
                f"_trunc_{min_length_minute}_min.txt",
            )

            save_rr_intervals(output_file, rr_truncated)

    save_removed_files(
        removed_low_duration,
        "duration (min)",
        round((min_length_seg / 60), 1),
        truncatedOutputDir,
        "removed_short_duration.txt",
    )

    logging.info("Truncation process completed")


def run_data_processing_and_analysis():
    logging.info("Starting data processing...")

    process_data(
        CONTROL_DIR,
        TEST_DIR,
        MIN_LENGTH_SEG,
        POLICY,
    )

    logging.info("Processing of all groups completed")

    trunc_control_dir = get_relative_output_path(
        TRUNCATED_OUTPUT_DIR,
        CONTROL_DIR,
    )

    trunc_test_dir = get_relative_output_path(
        TRUNCATED_OUTPUT_DIR,
        TEST_DIR,
    )

    report_file = os.path.join(
        OUTPUT_DIR,
        "truncated_report.txt",
    )

    generate_statistics_report(
        trunc_control_dir,
        trunc_test_dir,
        report_file,
    )


def run_data_analysis(
    output_dir,
    control_dir,
    test_dir,
    report_filename="report.txt",
    quality_threshold=QUALITY_THRESHOLD,
):
    logging.info("Performing a basic data analysis...")

    # Define the output file name for the report
    report_file = os.path.join(
        output_dir,
        report_filename,
    )

    # Generate the statistical report
    _, control_file_stats, test_file_stats = generate_statistics_report(
        control_dir,
        test_dir,
        report_file,
        quality_threshold,
    )

    if control_file_stats is None and test_file_stats is None:
        logging.warning(
            "No duration report was generated — files are missing."
        )
    else:
        generate_duration_and_quality_file_report(
            control_file_stats,
            test_file_stats,
            report_file.replace(
                ".txt",
                "_duration_and_quality.txt",
            ),
        )

    logging.info("Data analysis completed successfully.")


def main():
    setup_logging()

    if ask_user("Do you want to perform an initial data analysis?") == "s":
        run_data_analysis(
            OUTPUT_DIR,
            CONTROL_DIR,
            TEST_DIR,
            "initial_report.txt",
        )

        if ask_user("Do you want to continue with data processing?") == "s":
            run_data_processing_and_analysis()
    else:
        run_data_processing_and_analysis()


if __name__ == "__main__":
    main()