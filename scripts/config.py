import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

import os

# 預設路徑 (相對於儲存庫根目錄)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "taiwan_history.db")
TXT_PATH = os.path.join(BASE_DIR, "data", "臺灣通史.txt")

# 1920 SHP 檔由使用者自行下載後配置 (可修改此處或在腳本中啟動 AI 適配)
SHP_B_PATH = os.path.join(BASE_DIR, "data", "shp", "1920b_1.shp")
SHP_A_PATH = os.path.join(BASE_DIR, "data", "shp", "1920a_1.shp")

# 輸出路徑
KML_OUTPUT_PATH = os.path.join(BASE_DIR, "data", "Taiwan_History_Geo.kml")
