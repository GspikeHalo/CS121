# import sqlite3
#
# def get_database_size(db_file):
#     conn = sqlite3.connect(db_file)
#     cursor = conn.cursor()
#     cursor.execute("PRAGMA page_count")
#     page_count = cursor.fetchone()[0]
#     cursor.execute("PRAGMA page_size")
#     page_size = cursor.fetchone()[0]
#     conn.close()
#     return page_count * page_size / 1024 / 1024  # 将结果转换为 MB 单位
#
# # 指定 SQLite 数据库文件的路径
# db_file = "../../database/tf_idf_index.db"
#
# # 获取数据库大小
# database_size = get_database_size(db_file)
# print("Database size:", database_size, "MB")

import sqlite3

def export_tables_to_txt(db_file, output_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    with open(output_file, "w", encoding="utf-8") as file:
        for table_name in get_table_names(cursor):
            file.write(f"Table: {table_name}\n")
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            for row in rows:
                file.write(",".join(map(str, row)) + "\n")
            file.write("\n")

    conn.close()

def get_table_names(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return [row[0] for row in cursor.fetchall()]

# 指定 SQLite 数据库文件的路径
db_file = "../../database/tf_idf_index.db"
# 指定输出的文本文件路径
output_file = "tables.txt"

# 将数据库中的所有表转换为文本文件
export_tables_to_txt(db_file, output_file)
