"""
main.py — エントリポイント。data/ を読み、集計し、output/ にExcelを1つ出す。
使い方:  python main.py   （引数なし）
"""

import sys

import aggregate
import excel
import loader
from errors import SalesDataError


def main():
    try:
        df = loader.load_all()
    except SalesDataError as e:
        print(f"入力データに問題があります:\n  {e}", file=sys.stderr)
        return 1

    by_shop = aggregate.by_shop_month(df)
    by_category = aggregate.by_category_month(df)
    by_product = aggregate.top_products(df)
    summary_frame = aggregate.summary(df)

    year_month = df["年月"].max().replace("-", "")  # '2026-08' -> '202608'

    try:
        path = excel.write_report(by_shop, by_category, by_product, summary_frame, year_month)
    except PermissionError:
        print(
            "出力ファイルに書き込めませんでした。\n"
            "  output/ のExcelを開いたままなら、閉じてからもう一度実行してください。",
            file=sys.stderr,
        )
        return 1

    total = int(df["売上金額"].sum())
    print("集計が完了しました。")
    print(f"  対象: {df['年月'].min()} 〜 {df['年月'].max()} / {len(df)} 明細 / 総売上 {total:,} 円")
    print(f"  出力: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
