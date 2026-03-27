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
        "professor": "test123",
        "viewer": "test123",
        "123": "123",
        "1": "1",
        "11": "11",
        "111": "111",
        "2": "2",
        "3": "3",
        "4": "4",
        "5": "5",
        "6": "6",
        "7": "7",
        "8": "8",
        "9": "9",
        "10": "10",
        "11":"11",
        "12":"12",
        "13":"13",
        "14":"14",
        "15":"15",
        "16":"16",
        "17":"17",
        "18":"18",
        "19":"19",
        "20":"20",
        "21":"21",
        "22":"22",
        "23":"23",
        "24":"24",
        "25":"25",
        "26":"26",
        "27":"27",
        "28":"28",
        "29":"29",
        "30":"30",
    }