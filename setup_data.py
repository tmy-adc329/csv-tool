"""
ポートフォリオ(1)用のサンプルCSVを生成するスクリプト。

使い方:
    1. 作業フォルダを作る
    2. このファイルをそこに置く
    3. コマンドプロンプトで  python setup_data.py

data/ に 15 個のCSV（5店舗 x 3ヶ月）と output/ が作られます。

注意: このデータは実務を模して意図的に汚してあります。
      - ファイルによって列名が違う（売上金額 / 金額）
      - 日付形式が混在（2026-06-01 / 2026/7/1）
      - 金額にカンマが入る行がある（"2,040"）
      - BOM付きUTF-8
      - 一部ファイルの末尾に空行
      素直に読むだけでは必ず落ちます。これを吸収するのがツールの価値です。
"""

import csv
import os
import random

random.seed(20260903)

SHOPS = {
    "shinjuku": "新宿店",
    "yokohama": "横浜店",
    "nagoya": "名古屋店",
    "umeda": "梅田店",
    "hakata": "博多店",
}

# (商品コード, 商品名, カテゴリ, 単価)
ITEMS = [
    ("D-101", "ブレンドコーヒー", "ドリンク", 480),
    ("D-102", "カフェラテ", "ドリンク", 560),
    ("D-103", "アイスティー", "ドリンク", 500),
    ("F-201", "たまごサンド", "フード", 620),
    ("F-202", "ミックスサンド", "フード", 680),
    ("F-203", "キッシュプレート", "フード", 980),
    ("S-301", "チーズケーキ", "スイーツ", 520),
    ("S-302", "ガトーショコラ", "スイーツ", 540),
    ("G-401", "ドリップバッグ10個入", "物販", 1200),
    ("G-402", "オリジナルタンブラー", "物販", 2800),
]

# (年, 月, その月の日数)
MONTHS = [(2026, 6, 30), (2026, 7, 31), (2026, 8, 31)]


def main():
    os.makedirs("data", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    count = 0
    for year, month, last_day in MONTHS:
        for i, (slug, shop_name) in enumerate(SHOPS.items()):
            # わざと揺らす条件
            alt_header = (i % 3 == 1)      # 列名が「金額」になる
            comma_amount = (i % 2 == 0)    # 金額にカンマが入る
            slash_date = (month == 7)      # 日付が 2026/7/1 形式になる

            rows = []
            for day in range(1, last_day + 1):
                for _ in range(random.randint(2, 5)):
                    code, name, category, price = random.choice(ITEMS)
                    qty = random.randint(1, 12)
                    amount = qty * price

                    if slash_date:
                        date = f"{year}/{month}/{day}"
                    else:
                        date = f"{year}-{month:02d}-{day:02d}"

                    amount_str = f"{amount:,}" if comma_amount else str(amount)

                    rows.append([date, code, name, category, qty, price, amount_str])

            header = ["日付", "商品コード", "商品名", "カテゴリ", "数量", "単価",
                      "金額" if alt_header else "売上金額"]

            path = os.path.join("data", f"sales_{year}{month:02d}_{slug}.csv")
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(rows)
                if i % 4 == 3:
                    writer.writerow([])  # 末尾の空行（実務あるある）
            count += 1

    print(f"data/ に {count} 個のCSVを作りました。")
    print("output/ も作りました（集計結果の出力先）。")


if __name__ == "__main__":
    main()