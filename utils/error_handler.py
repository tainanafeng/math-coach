# ====== 錯誤處理並自動重試 ====== #
import traceback
import logging
import time


# 設定簡單的 log（可寫入 SQLite 或檔案）
logging.basicConfig(
    filename="error.log",
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def format_error_msg(e: str):
    """
    統一格式的錯誤回應(給使用者)
    """
    return (
        "⚠ 系統發生了非預期的錯誤，請稍後再試。\n\n"
        "若持續發生此問題，請聯絡開發者。\n\n"
        f"(錯誤內容：{e})"
    )


def safe_call(func, *args, retries=2, delay=0.5, **kwargs):
    """
    通用 try-catch 包裝器(含自動重試)
        - 將錯誤記錄到 log
        - 避免整個服務崩潰
        - 回傳統一錯誤訊息給使用者
    - retries: 最大重試次數(不含第一次)
    - delay: 每次 retry 間隔秒數
    """
    for attempt in range(retries + 1):

        try:
            return func(*args, **kwargs), None

        except Exception as e:
            err_text = traceback.format_exc()
            logging.error(err_text)

            if attempt < retries:
                time.sleep(delay)
            else:
                return None, str(e)
            
"""
safe_call 會自動：

    重試最多 3 次(預設：第一次 + 2 次 retry)

    有 delay 防止瞬間 spam API

    最後一次失敗才會真的 return err

"""