import logging

# カスタムロガーの設定
logger = logging.getLogger("custom_logger")
logger.setLevel(logging.INFO)

# ハンドラーの作成
handler = logging.StreamHandler()
format = "%(levelname)s : %(message)s"
formatter = logging.Formatter(format)
handler.setFormatter(formatter)

# ロガーにハンドラーを追加
logger.addHandler(handler)
