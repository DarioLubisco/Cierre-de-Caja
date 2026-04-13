import pyodbc

def check_user():
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=10.200.8.5\\efficacis3;DATABASE=EnterpriseAdmin_AMC;UID=sa;PWD=Twinc3pt.'
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Primero buscamos exactamente
        print("--- Buscando exactamente '12400678' ---")
        cursor.execute("SELECT CodVend, Descrip, Activo FROM dbo.SAVEND WHERE CodVend = '12400678'")
        rows = cursor.fetchall()
        for row in rows:
            print(f"Codigo: [{row[0]}], Nombre: {row[1]}, Activo: {row[2]}")
            
        # Buscamos parecido
        print("\n--- Buscando parecidos ---")
        cursor.execute("SELECT CodVend, Descrip, Activo FROM dbo.SAVEND WHERE CodVend LIKE '%12400678%'")
        rows = cursor.fetchall()
        for row in rows:
            print(f"Codigo: [{row[0]}], Nombre: {row[1]}, Activo: {row[2]}")
            
        if not rows:
            print("No se encontro nada con ese codigo.")

        # Listado de vendedores activos para ver nombres proximos
        print("\n--- Listado de los primeros 10 vendedores activos ---")
        cursor.execute("SELECT TOP 10 CodVend, Descrip FROM dbo.SAVEND WHERE Activo = 1")
        for row in cursor.fetchall():
            print(f"[{row[0].strip()}] - {row[1]}")

        # Buscamos en SSUSRS
        print("\n--- Buscando en SSUSRS (Usuarios del Sistema) ---")
        cursor.execute("SELECT CodUsua, Descrip, CodVend FROM SSUSRS WHERE (CodUsua = '12400678' OR CodVend = '12400678') AND Activo = 1")
        row = cursor.fetchone()
        if row:
            print(f"Encontrado en SSUSRS: Login/CodUsua={row[0].strip()}, Nombre={row[1].strip()}, CodVend_Asociado={row[2]}")
        else:
            print("No se encontro ningun USUARIO de sistema en SSUSRS con ese codigo o asociado a ese vendedor.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_user()
