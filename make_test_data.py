"""
make_test_data.py — ①（loader.py など）の入力処理をケースごとに検証するための
テスト用CSVを test_data/ に生成する。

【重要な制約】
- 出力は test_data/ 配下のみ。data/ には一切触れない。
- loader.py などの本体コードはここでは変更しない。テストデータを作るだけ。
- このスクリプトはテストを実行しない（test_data/ を作るだけで終わる）。

使い方:
    python make_test_data.py
    → test_data/ 以下に、ケースごとのサブフォルダ（A1, A2, ..., C3）ができる。

各サブフォルダは、それ単体で loader.load_all("test_data/<ケース名>") のように
渡せる、独立した「data/ 相当のフォルダ」になっている。
"""

import csv
import os
import shutil

TEST_DATA_DIR = "test_data"

# 通常のCSVの列（順番も含めて正常な形）
HEADER = ["日付", "商品コード", "商品名", "カテゴリ", "数量", "単価", "売上金額"]


def case_dir(name):
    """ケース名から test_data/<name> のパスを作る。"""
    return os.path.join(TEST_DATA_DIR, name)


def write_csv(path, header, rows, encoding="utf-8-sig"):
    """1つのCSVファイルを作る。

    header: 列名のリスト
    rows:   行のリストのリスト。空リスト [] を1つ混ぜると、そこに空行ができる
            （A7で「ファイル途中の空行」を作るのに使う）。
    encoding: 既定はBOM付きUTF-8（本物のdata/と同じ）。A6だけBOM無しにする。
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding=encoding) as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# A. 吸収してほしいもの（正常終了するはず）
# ---------------------------------------------------------------------------

def make_A1():
    """A1: 店舗数が違う（3店舗だけ）。それ以外は正常。"""
    d = case_dir("A1")
    for slug in ("shinjuku", "yokohama", "nagoya"):
        write_csv(os.path.join(d, f"sales_202610_{slug}.csv"), HEADER, [
            ["2026-10-01", "D-101", "ブレンドコーヒー", "ドリンク", 3, 480, "1,440"],
            ["2026-10-02", "F-201", "たまごサンド", "フード", 2, 620, "1,240"],
        ])


def make_A2():
    """A2: 期間が違う（1ヶ月だけ）。5店舗そろっているが月は1つだけ。"""
    d = case_dir("A2")
    for slug in ("shinjuku", "yokohama", "nagoya", "umeda", "hakata"):
        write_csv(os.path.join(d, f"sales_202610_{slug}.csv"), HEADER, [
            ["2026-10-01", "D-101", "ブレンドコーヒー", "ドリンク", 3, 480, "1,440"],
        ])


def make_A3():
    """A3: 列の並び順が違う（日付が先頭ではない）。"""
    d = case_dir("A3")
    shuffled_header = ["商品コード", "商品名", "カテゴリ", "日付", "単価", "数量", "売上金額"]
    write_csv(os.path.join(d, "sales_202610_shinjuku.csv"), shuffled_header, [
        ["D-101", "ブレンドコーヒー", "ドリンク", "2026-10-01", 480, 3, "1,440"],
        ["F-201", "たまごサンド", "フード", "2026-10-02", 620, 2, "1,240"],
    ])


def make_A4():
    """A4: 第3の日付形式（ドット区切り）2026.10.01。"""
    d = case_dir("A4")
    write_csv(os.path.join(d, "sales_202610_shinjuku.csv"), HEADER, [
        ["2026.10.01", "D-101", "ブレンドコーヒー", "ドリンク", 3, 480, "1,440"],
        ["2026.10.02", "F-201", "たまごサンド", "フード", 2, 620, "1,240"],
    ])


def make_A5():
    """A5: 金額に円記号 ¥2,040 のような値が混ざる。"""
    d = case_dir("A5")
    write_csv(os.path.join(d, "sales_202610_shinjuku.csv"), HEADER, [
        ["2026-10-01", "D-101", "ブレンドコーヒー", "ドリンク", 3, 480, "¥1,440"],
        ["2026-10-02", "F-201", "たまごサンド", "フード", 2, 620, "1,240"],
    ])


def make_A6():
    """A6: BOM無しのUTF-8（本物のdata/は全部BOM付きなので、その逆側を試す）。"""
    d = case_dir("A6")
    write_csv(os.path.join(d, "sales_202610_shinjuku.csv"), HEADER, [
        ["2026-10-01", "D-101", "ブレンドコーヒー", "ドリンク", 3, 480, "1,440"],
    ], encoding="utf-8")


def make_A7():
    """A7: 空行がファイルの「途中」にある（本物のdata/は末尾だけだった）。"""
    d = case_dir("A7")
    write_csv(os.path.join(d, "sales_202610_shinjuku.csv"), HEADER, [
        ["2026-10-01", "D-101", "ブレンドコーヒー", "ドリンク", 3, 480, "1,440"],  # CSV2行目
        ["2026-10-02", "F-201", "たまごサンド", "フード", 2, 620, "1,240"],       # CSV3行目
        [],                                                                     # CSV4行目（空行）
        ["2026-10-03", "S-301", "チーズケーキ", "スイーツ", 1, 520, 520],         # CSV5行目
    ])


def make_A8():
    """A8: 列名の前後に空白（" 売上金額 "）。"""
    d = case_dir("A8")
    spaced_header = ["日付", "商品コード", "商品名", "カテゴリ", "数量", "単価", " 売上金額 "]
    write_csv(os.path.join(d, "sales_202610_shinjuku.csv"), spaced_header, [
        ["2026-10-01", "D-101", "ブレンドコーヒー", "ドリンク", 3, 480, "1,440"],
    ])


def make_A9():
    """A9: 数量が0の行が混ざる。"""
    d = case_dir("A9")
    write_csv(os.path.join(d, "sales_202610_shinjuku.csv"), HEADER, [
        ["2026-10-01", "D-101", "ブレンドコーヒー", "ドリンク", 0, 480, 0],
        ["2026-10-02", "F-201", "たまごサンド", "フード", 2, 620, "1,240"],
    ])


# ---------------------------------------------------------------------------
# B. 止まってほしいもの（SalesDataErrorで止まるはず）
# ---------------------------------------------------------------------------

def make_B1():
    """B1: 金額に文字列 abc が混ざる。"""
    d = case_dir("B1")
    write_csv(os.path.join(d, "sales_202610_shinjuku.csv"), HEADER, [
        ["2026-10-01", "D-101", "ブレンドコーヒー", "ドリンク", 3, 480, "1,440"],
        ["2026-10-02", "F-201", "たまごサンド", "フード", 2, 620, "abc"],
    ])


def make_B2():
    """B2: 必須列（カテゴリ）が丸ごと無い。"""
    d = case_dir("B2")
    header_without_category = ["日付", "商品コード", "商品名", "数量", "単価", "売上金額"]
    write_csv(os.path.join(d, "sales_202610_shinjuku.csv"), header_without_category, [
        ["2026-10-01", "D-101", "ブレンドコーヒー", 3, 480, "1,440"],
    ])


def make_B3():
    """B3: config.SHOP_NAMES に無い店舗slug（sapporo）。"""
    d = case_dir("B3")
    write_csv(os.path.join(d, "sales_202610_sapporo.csv"), HEADER, [
        ["2026-10-01", "D-101", "ブレンドコーヒー", "ドリンク", 3, 480, "1,440"],
    ])


def make_B4():
    """B4: ファイル名が sales_*.csv の形にすら合っていない（指定通り）。"""
    d = case_dir("B4")
    write_csv(os.path.join(d, "uriage_2026_10.csv"), HEADER, [
        ["2026-10-01", "D-101", "ブレンドコーヒー", "ドリンク", 3, 480, "1,440"],
    ])


def make_B4b():
    """B4b（おまけ）: sales_*.csv には合うが、厳密な命名規則（年月6桁）には合わない。
    B4だけだと find_files の glob 自体が拾わず、parse_filename の
    正規表現チェックまで届かない（詳しくは回答の表を参照）。
    それを実際に踏ませるための追加ケース。
    """
    d = case_dir("B4b")
    write_csv(os.path.join(d, "sales_2026-10_umeda.csv"), HEADER, [
        ["2026-10-01", "D-101", "ブレンドコーヒー", "ドリンク", 3, 480, "1,440"],
    ])
    # find_files が「0件」にならないよう、正しい名前のファイルも1つ混ぜておく
    write_csv(os.path.join(d, "sales_202610_shinjuku.csv"), HEADER, [
        ["2026-10-01", "D-101", "ブレンドコーヒー", "ドリンク", 3, 480, "1,440"],
    ])


# ---------------------------------------------------------------------------
# C. 境界
# ---------------------------------------------------------------------------

def make_C1():
    """C1: フォルダの中にCSVが1つも無い。"""
    d = case_dir("C1")
    os.makedirs(d, exist_ok=True)  # 空のフォルダを作るだけ


def make_C2():
    """C2: CSVが1ファイルだけ。"""
    d = case_dir("C2")
    write_csv(os.path.join(d, "sales_202610_shinjuku.csv"), HEADER, [
        ["2026-10-01", "D-101", "ブレンドコーヒー", "ドリンク", 3, 480, "1,440"],
    ])


def make_C3():
    """C3: ヘッダー行だけで、データ行が0。"""
    d = case_dir("C3")
    write_csv(os.path.join(d, "sales_202610_shinjuku.csv"), HEADER, [])


# ---------------------------------------------------------------------------

def main():
    if os.path.exists(TEST_DATA_DIR):
        shutil.rmtree(TEST_DATA_DIR)

    makers = [
        make_A1, make_A2, make_A3, make_A4, make_A5, make_A6, make_A7, make_A8, make_A9,
        make_B1, make_B2, make_B3, make_B4, make_B4b,
        make_C1, make_C2, make_C3,
    ]
    for make in makers:
        make()

    print(f"{TEST_DATA_DIR}/ に {len(makers)} ケース分のフォルダを作成しました。")
    for make in makers:
        print(f"  - {TEST_DATA_DIR}/{make.__name__.removeprefix('make_')}")


if __name__ == "__main__":
    main()
