class SalesDataError(Exception):
    """入力データの不備。どのファイルの何行目が原因かを持つ。"""

    def __init__(self, path, line, message):
        self.path = path
        self.line = line
        self.message = message
        where = path if line is None else f"{path} の {line}行目"
        super().__init__(f"{where}: {message}")