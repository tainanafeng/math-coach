import streamlit as st

# CSS集中管理

# --- 通用美化 CSS ---
def apply_global_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');

        .stApp {
            background-color: #F9F7F2; /* 燕麥奶底色 */
            font-family: 'Quicksand', sans-serif;
        }

        /* 頂部導航條：毛玻璃特效 */
        header[data-testid="stHeader"] {
            background-color: rgba(249, 247, 242, 0.7) !important; /* 半透明燕麥奶 */
            backdrop-filter: blur(12px) !important; /* 毛玻璃模糊核心 */
            -webkit-backdrop-filter: blur(12px) !important;
            border-bottom: 1px solid rgba(210, 180, 140, 0.2) !important;
            height: 3.5rem !important;
        }

        /* 漸變按鈕設計：淺木色調 */
        button, [data-testid="baseButton-secondary"], [data-testid="baseButton-primary"] {
            background: linear-gradient(135deg, #E5D3B3 0%, #D2B48C 100%) !important; /* 木質漸層 */
            color: #5D4037 !important;
            border: none !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            padding: 8px 20px !important;
            box-shadow: 0 4px 15px rgba(210, 180, 140, 0.2) !important;
            transition: all 0.3s ease !important;
        }
        button:hover { transform: translateY(-2px); filter: brightness(1.02); }

        /* 側邊欄：深燕麥色 */
        [data-testid="stSidebar"] { background-color: #EFE9DB !important; }
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] h3 { color: #5D4037 !important; }

        /* 對話氣泡 */
        .chat-row { display: flex; margin-bottom: 20px; }
        .chat-row.user-row { justify-content: flex-end; padding-right: 10%; }
        .chat-row.ai-row { justify-content: flex-start; }
        .bubble { padding: 15px 22px; border-radius: 20px; max-width: 75%; line-height: 1.6; }
        .user-bubble { background-color: #E5D3B3; color: #5D4037; border-bottom-right-radius: 4px; } /* 淺木色使用者氣泡 */
        .ai-bubble { background-color: #FFFFFF; color: #5D4037; border: 2px solid #D2B48C; border-bottom-left-radius: 4px; }

        /* 隱藏註腳 */
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

# login 專用
def apply_login_style():
    st.markdown("""
    <style>
    /* ===== 背景：燕麥色格紋 ===== */
    .stApp {
        background-color: #F9F7F2;
        background-image:
            linear-gradient(rgba(210, 180, 140, 0.3) 1px, transparent 1px),
            linear-gradient(90deg, rgba(210, 180, 140, 0.3) 1px, transparent 1px);
        background-size: 35px 35px;
    }
    /* ===== 數學符號：淡木色 ===== */
    .math-doodle {
        position: fixed;
        color: rgba(93, 64, 55, 0.08);
        font-size: 120px;
        font-weight: 700;
        z-index: 0;
        pointer-events: none;
        user-select: none;
        filter: blur(1px);
    }
    /* ===== Glass 卡片 ===== */
    .glass-card {
        text-align: center;
        padding: 50px;
        border-radius: 28px;
        background: linear-gradient(
            135deg,
            rgba(255, 253, 249, 0.9),
            rgba(240, 230, 210, 0.7)
        );
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border: 1px solid rgba(210, 180, 140, 0.4);
        box-shadow:
            0 25px 60px rgba(93, 64, 55, 0.1),
            inset 0 1px 0 rgba(255,255,255,0.7);
    }
    .glass-card:hover {
        transform: translateY(-6px) scale(1.01);
        box-shadow:
            0 35px 80px rgba(93, 64, 55, 0.15),
            inset 0 1px 0 rgba(255,255,255,0.8);
    }
    /* ===== 輸入框 ===== */
    input {
        border-radius: 12px !important;
        border: 1px solid rgba(210, 180, 140, 0.4) !important;
        padding: 10px !important;
    }
    </style>

    <!-- 數學符號背景 -->               
    <div class="math-doodle" style="top:8%; left:8%; transform: rotate(15deg);">∑</div>
    <div class="math-doodle" style="top:65%; left:82%; transform: rotate(-15deg);">π</div>
    <div class="math-doodle" style="top:35%; left:78%; transform: rotate(10deg);">√x</div>
    <div class="math-doodle" style="top:78%; left:12%; transform: rotate(-20deg);">f(x)</div>
    """, unsafe_allow_html=True)

# main_page 專用
def apply_main_page_style():
    # 設置防禦性 CSS 與防跳轉鎖定
    st.markdown("""
        <style>
        /* 全域背景：燕麥奶格紋 */
        .stApp { 
            background-color: #F9F7F2 !important; 
            background-image:
                linear-gradient(rgba(210, 180, 140, 0.15) 1px, transparent 1px),
                linear-gradient(90deg, rgba(210, 180, 140, 0.15) 1px, transparent 1px) !important;
            background-size: 35px 35px !important;
        }

        /* 主內容區域：確保文字滾動不被遮擋 */
        [data-testid="stMain"] { background: transparent !important; }
   
        .block-container {
            height: calc(100vh - 145px) !important;
            overflow-y: auto !important;
            /*scroll-behavior: smooth !important; 平滑捲動 */
            padding-bottom: 50px !important;
        }

        /* 底部容器：徹底透明化，移除預設遮罩 */
        [data-testid="stChatInputContainer"], 
        .stChatFloatingInputContainer {
            background-color: transparent !important;
            background-image: none !important;
            border: none !important;
        }
                
        /* 為了視覺區隔，我們只給輸入框本身顏色，而不是給整個底部條顏色 */
        [data-testid="stChatInput"] {
            background-color: #EFE9DB !important; /* 燕麥色，與 config.toml 一致 */
            border: 1px solid rgba(210, 180, 140, 0.3) !important;
            border-radius: 16px !important;
            /* 讓它離底邊有一點距離，增加呼吸感 */
            margin-bottom: 15px !important;
            box-shadow: 0 4px 20px rgba(93, 64, 55, 0.1) !important;
        }
                
        /* 滾動條美化 */                
        .block-container::-webkit-scrollbar { width: 8px; }
        .block-container::-webkit-scrollbar-thumb { background-color: #E5D3B3; border-radius: 10px; }
        </style>
    """, unsafe_allow_html=True)