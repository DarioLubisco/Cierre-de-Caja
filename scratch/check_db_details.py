import pyodbc

def check_db():
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=10.200.8.5\\efficacis3;DATABASE=EnterpriseAdmin_AMC;UID=sa;PWD=Twinc3pt.'
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        print("\n--- Columns in Custom.CajaCierre ---")
        cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'CajaCierre' AND TABLE_SCHEMA = 'Custom'")
        for row in cursor.fetchall():
            print(f"{row[0]} ({row[1]})")

        print("\n--- Constraints for Custom.CajaCierreTarjeta ---")
        cursor.execute("SELECT name, definition FROM sys.check_constraints WHERE parent_object_id = OBJECT_ID('Custom.CajaCierreTarjeta')")
        for row in cursor.fetchall():
            print(f"Constraint: {row[0]}, Definition: {row[1]}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
