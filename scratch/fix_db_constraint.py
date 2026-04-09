import pyodbc

def fix_db():
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=10.200.8.5\\efficacis3;DATABASE=EnterpriseAdmin_AMC;UID=sa;PWD=Twinc3pt.'
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        print("Dropping old constraint...")
        cursor.execute("ALTER TABLE Custom.CajaCierreTarjeta DROP CONSTRAINT CK__CajaCierre__tipo__65ECCAC7")
        print("Old constraint dropped.")
        
        print("Adding new constraint...")
        cursor.execute("ALTER TABLE Custom.CajaCierreTarjeta ADD CONSTRAINT CK__CajaCierre__tipo_pago CHECK ([tipo]='BIOPAGO' OR [tipo]='TDC' OR [tipo]='TDD' OR [tipo]='PAGO_MOVIL')")
        print("New constraint added.")
        
        conn.commit()
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_db()
