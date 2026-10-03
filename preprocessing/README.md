# preprocessing

Preprocessing of RRi data for HRV calculation.

To run the code, start by installing the required dependencies:

```bash
pip install -r requirements.txt
```

Then, make sure the data is organized according to the following structure or change the paths in the `src/config.py` file:

```plaintext
hrv-cardiac/
├── data/
│   ├── control/
│   └── cardiac/
├── src/
│   ├── main.py
│   └── ...
├── README.md
└── requirements.txt
```

**The adopted methodology can be summarized in 4 steps:**

1. Discard the first 10 RRi entries from each file (patient);

2. Evaluate the stability of the RRi signals and discard files that do not meet the established threshold (90%). Signal stability is calculated based on:
   - Outlier Detection (RRi < 300 or RRi > 2000);
   - Ectopic Beat Detection (RRi+1/RRi must not vary by more than 20%, either upward or downward);

3. Transform the RRi signals into NNi (with 3 decimal places):
   - Replace Outliers using linear interpolation;
   - Replace Ectopic Beats using linear interpolation;

4. Truncate the NNi files, keeping the initial portion, based on a given time value (not the number of NNi). If the desired minimum time is not specified, the file with the shortest duration is used as the reference.

**At the end, the results will be saved in the `data/output/` directory, with 2 subdirectories:**

- `denoised/`: containing the complete NNi
- `truncated/`: containing the truncated NNi

- In addition, reports with basic statistical information about the initial data and the results will be saved, considering the `truncated/` directory, as shown in the example below:

```plaintext
        ---------- GROUP: X ----------
        Directory: ../data/output/truncated/X
        Number of Files: X
        Longest Duration (min): X
        File with Longest Duration: filename_trunc_X_min.txt
        Shortest Duration (min): X
        File with Shortest Duration: filename_trunc_X_min.txt
        Average Duration (min): X
        Quality Threshold (%): 90.0
        Average Quality (%): X
        Files Below Threshold: 0
        Files Above Threshold: 167
```
