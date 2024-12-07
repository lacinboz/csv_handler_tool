import sqlite3


conn = sqlite3.connect('cleaned_data.db')
cursor = conn.cursor()


cursor.execute("PRAGMA table_info(cleaned_data)")
columns = cursor.fetchall()


null_rows = []
for column in columns:
    column_name = column[1]
    cursor.execute(f"SELECT rowid, {column_name} FROM cleaned_data WHERE {column_name} IS NULL")
    null_data = cursor.fetchall()
    
    if null_data:
        print(f"Null values ​​found: {column_name}")
        for row in null_data:
            null_rows.append(row)


if null_rows:
    for null_row in null_rows:
        print(null_row)
else:
    print("No null value found.")

conn.close()
