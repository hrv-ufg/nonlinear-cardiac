import os
import numpy as np
import logging
from config import QUALITY_THRESHOLD
from processing import evaluate_signal_quality
from utils import list_rr_files
from file_io import load_rr_intervals


def evaluate_directory_statistics(directory, quality_threshold=QUALITY_THRESHOLD):
    """
    Evaluates general statistics for the files in a directory.

    Args:
        directory (str): Path to the directory to be evaluated.

    Returns:
        dict: Statistics about the directory.
    """
    files_stats = {}  # Changed to use the file name as the key
    num_files = 0

    # Iterate over the files in the directory
    for file in list_rr_files(directory):
        num_files += 1

        # Read the RR-interval values
        rr_intervals = load_rr_intervals(file)
        duration = np.sum(rr_intervals)  # Total duration in seconds
        quality = evaluate_signal_quality(rr_intervals)

        # Store the information in files_stats using the file name as the key
        files_stats[file] = {"duration": duration, "quality": quality}

    if num_files == 0:
        logging.warning(f"No files found in {directory}")
        return None, None

    # Basic statistics
    durations = [stats["duration"] for stats in files_stats.values()]
    max_duration = np.max(durations)
    min_duration = np.min(durations)
    mean_duration = np.mean(durations)

    qualities = [stats["quality"] for stats in files_stats.values()]
    mean_quality = np.mean(qualities)
    below_threshold = sum(q < quality_threshold for q in qualities)
    above_threshold = len(qualities) - below_threshold

    stats = {
        "Directory": directory,
        "Number of Files": num_files,
        "Maximum Duration (min)": round(max_duration / 60, 2),
        "File with Maximum Duration": os.path.basename(
            max(files_stats, key=lambda x: files_stats[x]["duration"])
        ),
        "Minimum Duration (min)": round(min_duration / 60, 2),
        "File with Minimum Duration": os.path.basename(
            min(files_stats, key=lambda x: files_stats[x]["duration"])
        ),
        "Average Duration (min)": round(mean_duration / 60, 2),
        "Quality Threshold (%)": round(quality_threshold * 100, 1),
        "Average Quality (%)": round(mean_quality * 100, 2),
        "Files Below Threshold": below_threshold,
        "Files Above Threshold": above_threshold,
    }

    return stats, files_stats


def generate_section_lines(group_name, metrics, report):
    """
   Generates formatted lines for a group section (Control or Test).

    Args:
        group_name (str): Name of the group (Control or Test).
        metrics (list): List of metrics to be displayed.
        report (dict): Dictionary containing the statistics for each group.

    Returns:
        str: Formatted lines for the section.
    """
    lines = [f"{'-'*10} GROUP: {group_name.upper()} {'-'*10}"]
    lines.extend([f"{metric}: {report[group_name][metric]}" for metric in metrics])
    return "\n".join(lines)


def generate_statistics_report(
    control_dir, test_dir, output_file, quality_threshold=QUALITY_THRESHOLD
):
    """
   Generates a consolidated report of directory statistics.

    Args:
        control_dir (str): Path to the control directory.
        test_dir (str): Path to the test directory.
        output_file (str): File where the report will be saved.
    """
    control_stats, control_file_stats = evaluate_directory_statistics(
        control_dir, quality_threshold
    )
    test_stats, test_file_stats = evaluate_directory_statistics(
        test_dir, quality_threshold
    )

    if control_stats is None and test_stats is None:
        logging.warning("No statistics were generated — files are missing.")
        return

    report = {"Control": control_stats, "Test": test_stats}

    metrics = list(report["Control"].keys())

    # Generate the Control Group section
    control_section = generate_section_lines("Control", metrics, report)

    # Generate the Test Group section
    test_section = generate_section_lines("Test", metrics, report)

    # Display in the console
    title_initial = f"\n{'='*15} BASIC GROUP INFORMATION {'='*15}"
    logging.info(title_initial)
    logging.info(control_section)
    logging.info(test_section)

    # Save to file
    with open(output_file, "w") as f:
        f.write(f"{'='*15} BASIC GROUP INFORMATION {'='*15}\n\n")
        f.write(control_section + "\n\n")
        f.write(test_section + "\n")

    logging.info(f"Report saved to: {output_file}")

    return report, control_file_stats, test_file_stats


def generate_duration_and_quality_file_report(
    control_file_stats, test_file_stats, output_file
):
    title_duration = (
        f"{'='*10} FILE DURATION AND QUALITY REPORT {'='*10}\n\n"
        + "-> Files are sorted in ascending order of duration.\n\n"
        + "Format: X.File Name | Duration (min) | Quality (%)"
    )

    control_duration_report = generate_group_duration_report(
        control_file_stats, "Control"
    )

    test_duration_report = generate_group_duration_report(test_file_stats, "Test")

    logging.info(title_duration)
    logging.info(control_duration_report)
    logging.info(control_duration_report)

    with open(output_file, "w") as f:
        f.write(title_duration)
        f.write(control_duration_report)
        f.write(test_duration_report)


def generate_group_duration_report(group_file_stats, group_name):
    """
    Generates a detailed report with all files and their durations in minutes,
    separated by groups (control and test), sorted in ascending order.

    Args:
        control_dir (str): Path to the control directory.
        test_dir (str): Path to the test directory.
        output_file (str): File where the report will be saved.
    """

    # Generate formatted lines for the report
    # Report header
    lines = []

    lines.append(f"\n\nGROUP: {group_name.upper()}")

    total_files = len(group_file_stats)
    # Sort files by duration in ascending order
    sorted_files = sorted(group_file_stats.items(), key=lambda x: x[1]["duration"])

    for i, (file_path, file_data) in zip(range(total_files, 0, -1), sorted_files):
        file_name = os.path.basename(file_path)
        quality_percent = file_data["quality"] * 100
        duration_minute = file_data["duration"] / 60
        lines.append(
            f"   {i}. {file_name} | {duration_minute:.2f} | {quality_percent:.1f}"
        )

    logging.info("\n".join(lines))
    report = "\n".join(lines)

    return report