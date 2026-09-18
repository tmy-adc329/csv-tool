# 店舗slug → 会議資料に出す日本語店名
SHOP_NAMES = {
    "shinjuku": "新宿店",
    "yokohama": "横浜店",
    "nagoya": "名古屋店",
    "umeda": "梅田店",
    "hakata": "博多店",
}

# 集計表で店舗を並べる順（この順で行を出す）
SHOP_ORDER = ["新宿店", "横浜店", "名古屋店", "梅田店", "博多店"]

# 集計表でカテゴリを並べる順
CATEGORY_ORDER = ["ドリンク", "フード", "スイーツ", "物販"]

# 「売上金額」と同じ意味で使われる列名（正規化前）
AMOUNT_COLUMN_ALIASES = {"売上金額", "金額"}

# 正規化後に使う金額列の名前
CANONICAL_AMOUNT_COLUMN = "売上金額"

# 商品別ランキングの件数（aggregate.py で使う）
TOP_N_PRODUCTS = 10

# 出力先フォルダ
OUTPUT_DIR = "output"
