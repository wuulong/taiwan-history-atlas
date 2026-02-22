import sqlite3
import argparse
import sys
import os

DB_PATH = "data/history_texts/taiwan_history.db"

def main():
    parser = argparse.ArgumentParser(description="從 taiwan_history.db 彈性匯出史料內容至檔案")
    parser.add_argument("--volume", help="指定要匯出的卷名 (例如: 開闢紀)")
    parser.add_argument("--ids", help="指定要匯出的 content IDs (逗號分隔，例如: 1,2,5)")
    parser.add_argument("--query", help="自定義 SQL 查詢 (需回傳單一文字欄位)")
    parser.add_argument("--output", help="輸出檔案路徑 (預設輸出至 tmp/dump_output.md)", default="tmp/dump_output.md")
    
    args = parser.parse_args()

    if not any([args.volume, args.ids, args.query]):
        parser.print_help()
        sys.exit(1)

    # 確保 tmp 目錄存在
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    result_text = []

    try:
        if args.volume:
            print(f"📦 正在匯出卷次: {args.volume} ...")
            cursor.execute("""
                SELECT v.title, c.raw_text 
                FROM contents c 
                JOIN volumes v ON c.vol_id = v.id 
                WHERE v.title = ? 
                ORDER BY c.id
            """, (args.volume,))
            rows = cursor.fetchall()
            if rows:
                result_text.append(f"# {rows[0][0]}\n")
                result_text.extend([row[1] for row in rows])
            else:
                print(f"❌ 找不到卷次: {args.volume}")

        elif args.ids:
            id_list = [i.strip() for i in args.ids.split(",")]
            print(f"📦 正在匯出指定 IDs: {id_list} ...")
            placeholders = ",".join(["?"] * len(id_list))
            cursor.execute(f"SELECT raw_text FROM contents WHERE id IN ({placeholders}) ORDER BY id", id_list)
            rows = cursor.fetchall()
            result_text.extend([row[0] for row in rows])

        elif args.query:
            print(f"📦 正在執行自定義查詢: {args.query} ...")
            cursor.execute(args.query)
            rows = cursor.fetchall()
            # 假設查詢回傳的第一個欄位就是我們要的文字
            result_text.extend([str(row[0]) for row in rows])

        # 寫入檔案
        if result_text:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write("\n\n".join(result_text))
            print(f"✅ 匯出完成！檔案儲存至: {args.output}")
            print(f"📊 總字數: {sum(len(t) for t in result_text)}")
        else:
            print("⚠️ 沒有查得任何內容，未產生檔案。")

    except Exception as e:
        print(f"💥 發生錯誤: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
