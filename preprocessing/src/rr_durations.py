from __future__ import annotations

import unicodedata

import argparse
import csv
import math
from pathlib import Path
from typing import Optional, Tuple, List, Dict

import numpy as np


# -----------------------------
# Tolerant TXT reader
# -----------------------------
def load_txt(path: Path) -> np.ndarray:
    """
    Reads TXT files with tolerance for:
      - separators: whitespace, tab
      - comments starting with '#'
    If a comma/semicolon is detected in the file, also tries CSV/;
    as a fallback.
    """
    data = np.genfromtxt(
        path,
        delimiter=None,   # whitespace
        comments="#",
        dtype=float,
        invalid_raise=False,
    )

    # Fallback if the file appears to use ',' or ';'
    txt = path.read_text(errors="ignore")
    if ("," in txt) or (";" in txt):
        for delim in [",", ";", "\t"]:
            d2 = np.genfromtxt(
                path,
                delimiter=delim,
                comments="#",
                dtype=float,
                invalid_raise=False,
            )
            # If the format changed (e.g., from 1D to 2D, or the number of columns increased), use it
            if np.size(d2) > 0 and (np.ndim(d2) != np.ndim(data) or (hasattr(d2, "shape") and hasattr(data, "shape") and d2.shape != data.shape)):
                data = d2
                break

    if np.size(data) == 0:
        return np.array([], dtype=float)

    return np.array(data, dtype=float)


# -----------------------------
# Detection of [t, RR] pattern
# -----------------------------
def detect_two_col_timestamp_rr(data: np.ndarray) -> Optional[Tuple[np.ndarray, np.ndarray]]:
    """
    Detects the [timestamp, RR] pattern in 2 columns:
      - increasing timestamp (almost always)
      - diff(timestamp) ~ RR (for most points)
    Returns (t, rr) if recognized; otherwise None.
    """
    if data.ndim != 2 or data.shape[1] < 2 or data.shape[0] < 5:
        return None

    t = data[:, 0].astype(float)
    rr = data[:, 1].astype(float)

    m = np.isfinite(t) & np.isfinite(rr) & (rr > 0)
    t, rr = t[m], rr[m]
    if t.size < 5:
        return None

    dt = np.diff(t)
    if np.mean(dt >= 0) < 0.95:
        return None

    rr2 = rr[1:]
    dt2 = dt[: rr2.size]
    if rr2.size < 3:
        return None

    err = np.abs(dt2 - rr2)
    med_err = float(np.median(err))

    # Tolerance: 30 ms or 10% of the median RR
    tol = max(0.03, 0.10 * float(np.median(rr2)))

    if med_err <= tol:
        return t, rr

    return None


# -----------------------------
# Generic RR column selection
# -----------------------------
def _robust_rr_score(x: np.ndarray) -> float:
    """
    Score indicating how 'RR-like' a column is.
    Heuristics: positive values, plausible range, plausible variability.
    """
    x = x[np.isfinite(x)]
    if x.size < 10:
        return -1.0

    pos_frac = float(np.mean(x > 0))
    if pos_frac < 0.95:
        return -1.0

    med = float(np.median(x))
    iqr = float(np.subtract(*np.percentile(x, [75, 25])))
    mad = float(np.median(np.abs(x - med)) + 1e-12)

    plausible_s = 0.25 <= med <= 2.5
    plausible_ms = 250 <= med <= 2500
    plaus = 1.0 if (plausible_s or plausible_ms) else 0.0

    rel_iqr = iqr / (abs(med) + 1e-12)
    var_ok = 0.005 <= rel_iqr <= 0.7

    score = 0.0
    score += 2.0 * plaus
    score += 1.5 * (1.0 if var_ok else 0.0)
    score += 1.0 * pos_frac
    score -= 0.5 if mad < 1e-6 else 0.0

    p99 = float(np.percentile(x, 99))
    if plausible_s and p99 > 10:
        score -= 1.0
    if plausible_ms and p99 > 10000:
        score -= 1.0

    return score


def pick_rr_column(data: np.ndarray) -> Tuple[np.ndarray, int]:
    """
    If data is 1D -> RR is the vector itself.
    If 2D -> selects the most RR-like column.
    """
    if data.ndim == 1:
        return data.astype(float), 0

    best_col = 0
    best_score = -math.inf
    for j in range(data.shape[1]):
        col = data[:, j].astype(float)
        score = _robust_rr_score(col)
        if score > best_score:
            best_score = score
            best_col = j

    rr = data[:, best_col].astype(float)
    return rr, best_col


# -----------------------------
# Unit + duration inference
# -----------------------------
def infer_unit_and_minutes_from_rr(rr: np.ndarray) -> Tuple[Optional[str], float, int]:
    """
    Calculates duration using sum(RR) and attempts to infer the unit (ms or s).
    Returns (unit, minutes, n_valid).
    """
    rr = rr.astype(float)
    rr = rr[np.isfinite(rr)]
    rr = rr[rr > 0]
    n = int(rr.size)
    if n < 2:
        return None, float("nan"), n

    med = float(np.median(rr))
    if med > 10:  # ms
        unit = "ms"
        total_seconds = float(np.sum(rr)) / 1000.0
    else:         # s
        unit = "s"
        total_seconds = float(np.sum(rr))

    return unit, total_seconds / 60.0, n


def duration_minutes(data: np.ndarray) -> Tuple[Optional[str], float, int, str, Optional[int]]:
    """
    Returns:
      (unit, minutes, n_valid, method, rr_col_index)

    method:
      - 'timestamp+rr' (when [t, RR] is detected in seconds)
      - 'sum(rr)'      (fallback)
    rr_col_index:
      - RR column index when using 'sum(rr)' with 2D data
      - 1 when using 'timestamp+rr' (RR is the 2nd column)
      - 0 when using 1D data
    """
    # 1) Special case: two columns [timestamp, RR]
    two_col = detect_two_col_timestamp_rr(data)
    if two_col is not None:
        t, rr = two_col
        dur_s = float(t[-1] - t[0] + rr[-1])
        return "s", dur_s / 60.0, int(rr.size), "timestamp+rr", 1

    # 2) Fallback: use RR (1 column or select the most RR-like column)
    rr, rr_col = pick_rr_column(data)
    unit, minutes, n_valid = infer_unit_and_minutes_from_rr(rr)
    return unit, minutes, n_valid, "sum(rr)", rr_col


def sort_key(path: Path):
    # File name without the path
    name = path.name

    # Normalize accents (ç → c, á → a, etc.)
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))

    # Ignore uppercase/lowercase differences
    return name.casefold()


# -----------------------------
# Folder processing
# -----------------------------
def process_folder(folder: Path, out_csv: Optional[Path] = None) -> List[Dict]:
    rows: List[Dict] = []

    for path in sorted(folder.rglob("*.txt"), key=sort_key):
        try:
            data = load_txt(path)

            if data.size == 0:
                rows.append(
                    {
                        "file": str(path.relative_to(folder)),
                        "duration_min": float("nan"),
                        "unit": "",
                        "n_valid": 0,
                        "method": "",
                        "rr_col_index": "",
                        "error": "empty file or unreadable",
                    }
                )
                continue

            unit, minutes, n_valid, method, rr_col_index = duration_minutes(data)

            rows.append(
                {
                    "file": str(path.relative_to(folder)),
                    "duration_min": minutes,
                    "unit": unit or "",
                    "n_valid": n_valid,
                    "method": method,
                    "rr_col_index": rr_col_index if rr_col_index is not None else "",
                    "error": "",
                }
            )
        except Exception as e:
            rows.append(
                {
                    "file": str(path.relative_to(folder)),
                    "duration_min": float("nan"),
                    "unit": "",
                    "n_valid": 0,
                    "method": "",
                    "rr_col_index": "",
                    "error": repr(e),
                }
            )

    # Save CSV if requested
    if out_csv is not None:
        fieldnames = ["file", "duration_min", "unit", "n_valid", "method", "rr_col_index", "error"]
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in rows:
                for k in fieldnames:
                    r.setdefault(k, "")
                w.writerow(r)

    return rows


def main():
    ap = argparse.ArgumentParser(
        description="Scans a folder containing .txt RR-interval files (1 or 2 columns) and calculates duration (min)."
    )
    ap.add_argument("folder", type=str, help="Folder containing .txt files (subfolders are allowed).")
    ap.add_argument("--csv", type=str, default="", help="Path to save the CSV file (optional).")
    args = ap.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    if not folder.exists() or not folder.is_dir():
        raise SystemExit(f"Invalid folder: {folder}")

    out_csv = Path(args.csv).expanduser().resolve() if args.csv else None
    rows = process_folder(folder, out_csv=out_csv)

    # Print simple list: file -> duration
    for r in rows:
        if r.get("error"):
            print(f"{r['file']}: ERROR {r['error']}")
        else:
            print(
                f"{r['file']}: {r['duration_min']:.3f} min "
                f"(unit={r['unit']}, method={r['method']}, rr_col={r['rr_col_index']}, n={r['n_valid']})"
            )

    if out_csv:
        print(f"\nCSV saved to: {out_csv}")


if __name__ == "__main__":
    main()