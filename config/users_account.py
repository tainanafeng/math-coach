# 測試用帳號(10位)
import os
import json

TEST_USERS_JSON = os.getenv("TEST_USERS_JSON")

if TEST_USERS_JSON:
    TEST_USERS = json.loads(TEST_USERS_JSON)
else:
    # fallback：本機 / demo 預設帳號
    TEST_USERS = {

    }