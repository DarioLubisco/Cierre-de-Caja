import pyodbc
import os

def check_db():
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=10.200.8.5\\efficacis3;DATABASE=EnterpriseAdmin_AMC;UID=sa;PWD=Twinc3pt.'
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        print("--- Checking Constraints for Custom.CajaCierreTarjeta ---")
        cursor.execute("SELECT name, definition FROM sys.check_constraints WHERE parent_object_id = OBJECT_ID('Custom.CajaCierreTarjeta')")
        for row in cursor.fetchall():
            print(f"Constraint: {row[0]}\nDefinition: {row[1]}\n")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
