import common.configs as configs
import sqlite3


def flush():
    conn = sqlite3.connect(configs.DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM course")
    conn.commit()
    conn.close()
