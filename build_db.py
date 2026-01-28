import psycopg2


DB_URL = "postgresql://sampledb_rc1x_user:rOWPnK5viO757ELXvod7ngxrWy2WZACo@dpg-d5t6r70gjchc73cup5e0-a.virginia-postgres.render.com/sampledb_rc1x"

with open('database/init.sql', 'r') as f:
    sql_commands = f.read()

try:
    print("Connecting to the database...")
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    print("Building tables...")
    cur.execute(sql_commands)
    
    conn.commit()
    print("Success! Tables created.")
    
except Exception as e:
    print("Error:", e)
finally:
    if 'conn' in locals():
        conn.close()