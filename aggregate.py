"""
aggregate.py — loader.load_all() が返す「きれいな縦持ちDataFrame」を受け取り、
SPEC の4つの集計表を作る。ファイルもExcelも知らない、純粋な集計だけ。
"""

import pandas as pd

import config

AMOUNT = "売上金額"
QTY = "数量"


def _month_columns(df):
    """データに含まれる年月を昇順のリストで返す。例: ['2026-06', '2026-07', '2026-08']"""
    return sorted(df["年月"].unique())


def _pivot_by(df, index_col, order):
    """index_col（店舗 or カテゴリ）× 年月 の売上合計に、合計の行と列を足して返す。"""
    table = pd.pivot_table(
        df, index=index_col, columns="年月", values=AMOUNT,
        aggfunc="sum", fill_value=0,
    )
    table = table.reindex(index=order, columns=_month_columns(df), fill_value=0)
    table["合計"] = table.sum(axis=1)
    table.loc["合計"] = table.sum(axis=0)
    return table.reset_index()


def by_shop_month(df):
    """店舗別 × 月別 の売上合計。"""
    return _pivot_by(df, "店舗", config.SHOP_ORDER)


def by_category_month(df):
    """カテゴリ別 × 月別 の売上合計。"""
    return _pivot_by(df, "カテゴリ", config.CATEGORY_ORDER)


def top_products(df, n=config.TOP_N_PRODUCTS):
    """商品別の売上合計。売上金額の降順で上位 n 件。"""
    grouped = df.groupby("商品コード", as_index=False).agg(
        商品名=("商品名", "first"),
        カテゴリ=("カテゴリ", "first"),
        販売点数=(QTY, "sum"),
        売上金額=(AMOUNT, "sum"),
    )
    grouped = grouped.sort_values("売上金額", ascending=False)
    return grouped.head(n).reset_index(drop=True)


def summary(df):
    """全体サマリ（対象期間・総売上・総販売点数・平均単価）。"""
    total_amount = int(df[AMOUNT].sum())
    total_qty = int(df[QTY].sum())
    avg_unit_price = round(total_amount / total_qty) if total_qty else 0
    months = _month_columns(df)
    rows = [
        ("対象期間", f"{months[0]} 〜 {months[-1]}"),
        ("総売上", total_amount),
        ("総販売点数", total_qty),
        ("平均単価", avg_unit_price),
    ]
    return pd.DataFrame(rows, columns=["項目", "値"])
