"""
loader.py — data/ の売上CSVを読み込み、1枚の「きれいな縦持ちDataFrame」にする。

吸収する汚れ:
  - 列名の揺れ（売上金額 / 金額）
  - 日付形式の揺れ（2026-06-01 / 2026/7/1）
  - カンマ付き金額（"2,040"）と素の数値（620）の混在
  - BOM付きUTF-8
  - 空行

変換に失敗した行は SalesDataError（ファイル名＋CSV行番号つき）で報告して止まる。
"""

import glob
import os
import re

import pandas as pd

from config import SHOP_NAMES, AMOUNT_COLUMN_ALIASES, CANONICAL_AMOUNT_COLUMN
from errors import SalesDataError

# ファイル名の形: sales_YYYYMM_<slug>.csv
FILENAME_RE = re.compile(r"^sales_(\d{4})(\d{2})_(.+)\.csv$")

# 正規化後、必ずこの列がこの順で入っている
OUTPUT_COLUMNS = [
    "日付", "店舗", "年月",
    "商品コード", "商品名", "カテゴリ",
    "数量", "単価", "売上金額",
    "ファイル名", "元行番号",
]

# 金額列以外に、CSVに必ずあるべき列
REQUIRED_INPUT_COLUMNS = ["日付", "商品コード", "商品名", "カテゴリ", "数量", "単価"]


def find_files(data_dir="data"):
    """data_dir 直下の sales_*.csv を名前順で返す。1つも無ければ止める。"""
    files = sorted(glob.glob(os.path.join(data_dir, "sales_*.csv")))
    if not files:
        raise SalesDataError(data_dir, None, "sales_*.csv が1つも見つかりません")
    return files


def parse_filename(path):
    """ファイル名から (年月, 日本語店名) を取り出す。例: ('2026-06', '新宿店')。"""
    name = os.path.basename(path)
    m = FILENAME_RE.match(name)
    if m is None:
        raise SalesDataError(path, None, f"想定外のファイル名です: {name}")
    year, month, slug = m.groups()
    if slug not in SHOP_NAMES:
        raise SalesDataError(path, None, f"未知の店舗slugです: {slug}")
    return f"{year}-{month}", SHOP_NAMES[slug]


def normalize_columns(df, path):
    """列名の前後空白を落とし、金額列の別名（金額）を正規名（売上金額）に統一する。"""
    df = df.rename(columns=lambda c: c.strip())
    found = [c for c in df.columns if c in AMOUNT_COLUMN_ALIASES]
    if len(found) == 0:
        raise SalesDataError(path, None, f"金額列が見つかりません: {list(df.columns)}")
    if len(found) > 1:
        raise SalesDataError(path, None, f"金額列が複数あります: {found}")
    return df.rename(columns={found[0]: CANONICAL_AMOUNT_COLUMN})


def parse_amount(s, label="金額", path=None, line_numbers=None):
    """カンマ付き文字列・素の数値が混じった Series を、整数(Int64)の Series にする。

    path と line_numbers を渡すと、失敗時に SalesDataError（何行目か付き）を投げる。
    渡さなければ ValueError を投げる（単体テスト用）。
    """
    text = s.astype("string").str.replace(",", "", regex=False).str.strip()
    numeric = pd.to_numeric(text, errors="coerce")
    bad = numeric.isna() & s.notna()
    if bad.any():
        bad_value = s[bad].iloc[0]
        if path is not None and line_numbers is not None:
            raise SalesDataError(path, int(line_numbers[bad].iloc[0]),
                                 f"{label}を数値に変換できません: {bad_value!r}")
        raise ValueError(f"{label}を数値に変換できません: {bad_value!r}")
    return numeric.astype("Int64")


def parse_dates(s, path=None, line_numbers=None):
    """'2026-06-01' も '2026/7/1' も datetime に変換した Series を返す。"""
    parsed = pd.to_datetime(s, errors="coerce", format="mixed")
    bad = parsed.isna() & s.notna()
    if bad.any():
        bad_value = s[bad].iloc[0]
        if path is not None and line_numbers is not None:
            raise SalesDataError(path, int(line_numbers[bad].iloc[0]),
                                 f"日付を解釈できません: {bad_value!r}")
        raise ValueError(f"日付を解釈できません: {bad_value!r}")
    return parsed


def read_one(path):
    """CSVを1つ読み、OUTPUT_COLUMNS の形に正規化した DataFrame を返す。"""
    year_month, shop = parse_filename(path)

    raw = pd.read_csv(path, encoding="utf-8-sig", dtype=str, skip_blank_lines=False)
    raw = raw.dropna(how="all")
    line_numbers = pd.Series(raw.index + 2, index=raw.index)

    df = normalize_columns(raw, path)
    missing = [c for c in REQUIRED_INPUT_COLUMNS if c not in df.columns]
    if missing:
        raise SalesDataError(path, None, f"必要な列がありません: {missing}")

    df["日付"] = parse_dates(df["日付"], path, line_numbers)
    df["売上金額"] = parse_amount(df["売上金額"], "金額", path, line_numbers)
    df["数量"] = parse_amount(df["数量"], "数量", path, line_numbers)
    df["単価"] = parse_amount(df["単価"], "単価", path, line_numbers)

    df["店舗"] = shop
    df["年月"] = year_month
    df["ファイル名"] = os.path.basename(path)
    df["元行番号"] = line_numbers

    return df[OUTPUT_COLUMNS]


def load_all(data_dir="data"):
    """data_dir の全CSVを読み、1枚の縦持ち DataFrame に連結して返す。"""
    frames = [read_one(path) for path in find_files(data_dir)]
    return pd.concat(frames, ignore_index=True)


if __name__ == "__main__":
    result = load_all()
    print("形:", result.shape)
    print(result.head())
    print(result.dtypes)