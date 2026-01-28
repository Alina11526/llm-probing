# pipeline/utils_csv.py

import csv
import os
import pandas as pd
from typing import List
import tempfile


def safe_read_csv(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV not found: {path}")

    try:
        return pd.read_csv(path)
    except Exception as e:
        print(f"[WARN] CSV corrupted, trying tolerant read: {path}")
        return pd.read_csv(
            path,
            engine="python",
            on_bad_lines="skip"
        )


def safe_write_csv(df: pd.DataFrame, path: str):
    """
    Atomic CSV write:
    - write to temp file first
    - fsync
    - replace original in one step
    """

    dir_name = os.path.dirname(path)
    os.makedirs(dir_name, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        mode="w",
        delete=False,
        dir=dir_name,
        suffix=".tmp",
        encoding="utf-8",
        newline=""
    ) as tmp:
        tmp_path = tmp.name

        df.to_csv(
            tmp,
            index=False,
            quoting=csv.QUOTE_ALL,
            escapechar="\\"
        )
        tmp.flush()
        os.fsync(tmp.fileno())

    os.replace(tmp_path, path)


def ensure_columns(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    """
    Ensure columns exist (used for gpt / deepseek / bert)
    """
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    return df.reset_index(drop=True)

