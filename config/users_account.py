# 測試用帳號
import os
import json

TEST_USERS_JSON = os.getenv("TEST_USERS_JSON")

if TEST_USERS_JSON:
    TEST_USERS = json.loads(TEST_USERS_JSON)
else:
    # fallback：本機 / demo 預設帳號
    TEST_USERS = {
        "user1":  "Q8tL92FbW1",
        "user2":  "mK47pTz81B",
        "user3":  "Xv91LqT2sE",
        "user4":  "R7bYw38KpQ",
        "user5":  "gC52ZLm8tR",
        "user6":  "Tn84vBs93W",
        "user7":  "Hs67WqP49J",
        "user8":  "J3cPzL81tV",
        "user9":  "Lw95NqR27B",
        "user10": "Zt28HsQ56M",
        "manager": "test123",
        "mom": "test123",
        "dad": "test123",
        "professor": "test123"
    }
