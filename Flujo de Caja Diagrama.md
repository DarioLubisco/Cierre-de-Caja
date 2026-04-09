# Cash Register Closing Process (Conciliation)

Below is the updated flow and data model for the closing (conciliation) process.

> [!TIP]
> **Diagrama Disponible:** Para visualizar el flujo operativo, abre el archivo [Flujo_Caja.mmd](file:///c:/source/Cierre%20de%20Caja/Flujo_Caja.mmd) o cópialo en el Mermaid Live Editor oficial.

## Data Model (SQL Server DDL)

```sql
-- Main closure header table
CREATE TABLE dbo.CajaCierre (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    vendedor_codigo VARCHAR(10) NOT NULL,
    vendedor_nombre VARCHAR(120) NULL,
    fecha_ini DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    -- System totals
    totefectivo DECIMAL(18,2) NOT NULL DEFAULT 0,
    totcheque DECIMAL(18,2) NOT NULL DEFAULT 0,
    tottarjeta DECIMAL(18,2) NOT NULL DEFAULT 0,
    totgiros DECIMAL(18,2) NOT NULL DEFAULT 0,
    totadelantos DECIMAL(18,2) NOT NULL DEFAULT 0,
    totretimp DECIMAL(18,2) NOT NULL DEFAULT 0,
    -- Manual (cashier) totals
    manual_efectivo_bs DECIMAL(18,2) NOT NULL DEFAULT 0,
    manual_divisas DECIMAL(18,2) NOT NULL DEFAULT 0,
    manual_euros DECIMAL(18,2) NOT NULL DEFAULT 0,
    manual_cheques DECIMAL(18,2) NOT NULL DEFAULT 0,
    manual_tdd DECIMAL(18,2) NOT NULL DEFAULT 0,
    manual_tdc DECIMAL(18,2) NOT NULL DEFAULT 0,
    manual_biopago DECIMAL(18,2) NOT NULL DEFAULT 0,
    manual_giros DECIMAL(18,2) NOT NULL DEFAULT 0,
    estado VARCHAR(20) NOT NULL DEFAULT 'BORRADOR', -- BORRADOR (Precierre) or FINALIZADO
    creado_por INT NOT NULL,
    creado_en DATETIME2(0) NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_CajaCierre_User FOREIGN KEY (creado_por) REFERENCES auth_user(id),
    CONSTRAINT CHK_CajaCierre_Estado CHECK (estado IN ('BORRADOR', 'FINALIZADO'))
);
GO

-- Differences tracking by category (for monthly reporting)
CREATE TABLE dbo.CajaCierreDiferencia (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    cierre_id BIGINT NOT NULL,
    vendedor_codigo VARCHAR(10) NOT NULL, -- Denormalized for easy reporting
    category VARCHAR(30) NOT NULL, -- EFECTIVO, TDD, TDC, BIOPAGO, CHEQUE
    sistema DECIMAL(18,2) NOT NULL DEFAULT 0,
    manual DECIMAL(18,2) NOT NULL DEFAULT 0,
    diferencia AS (manual - sistema) PERSISTED,
    CONSTRAINT FK_Diferencia_Cierre FOREIGN KEY (cierre_id) REFERENCES dbo.CajaCierre(id) ON DELETE CASCADE
);
GO
CREATE INDEX IX_CajaDiferencia_Vendedor ON dbo.CajaCierreDiferencia(vendedor_codigo);
GO

-- Cash (efectivo) breakdown
CREATE TABLE dbo.CajaCierreEfectivo (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    cierre_id BIGINT NOT NULL,
    denominacion INT NOT NULL, -- bill face value
    cantidad INT NOT NULL DEFAULT 0,
    total DECIMAL(18,2) NOT NULL, -- denominacion * cantidad (or coins total)
    CONSTRAINT FK_Efectivo_Cierre FOREIGN KEY (cierre_id) REFERENCES dbo.CajaCierre(id) ON DELETE CASCADE
);
GO
CREATE INDEX IX_CajaCierreEfectivo_Cierre ON dbo.CajaCierreEfectivo(cierre_id);
GO

-- Foreign currency (USD bills and EUR total)
CREATE TABLE dbo.CajaCierreDivisa (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    cierre_id BIGINT NOT NULL,
    moneda CHAR(3) NOT NULL CHECK (moneda IN ('USD','EUR')),
    denominacion INT NULL, -- NULL for EUR total row
    cantidad INT NOT NULL DEFAULT 0,
    total DECIMAL(18,2) NOT NULL,
    CONSTRAINT FK_Divisa_Cierre FOREIGN KEY (cierre_id) REFERENCES dbo.CajaCierre(id) ON DELETE CASCADE
);
GO
CREATE INDEX IX_CajaCierreDivisa_Cierre ON dbo.CajaCierreDivisa(cierre_id);
GO

-- Checks (cheques)
CREATE TABLE dbo.CajaCierreCheque (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    cierre_id BIGINT NOT NULL,
    banco VARCHAR(60) NOT NULL,
    referencia VARCHAR(60) NOT NULL,
    monto DECIMAL(18,2) NOT NULL,
    CONSTRAINT FK_Cheque_Cierre FOREIGN KEY (cierre_id) REFERENCES dbo.CajaCierre(id) ON DELETE CASCADE
);
GO
CREATE INDEX IX_CajaCierreCheque_Cierre ON dbo.CajaCierreCheque(cierre_id);
GO

-- Card / Biopago transactions (grouped under tarjetas)
CREATE TABLE dbo.CajaCierreTarjeta (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    cierre_id BIGINT NOT NULL,
    tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('TDD','TDC','BIOPAGO')),
    punto_de_venta VARCHAR(60) NOT NULL, -- Terminal / POS ID
    referencia VARCHAR(60) NOT NULL,
    monto DECIMAL(18,2) NOT NULL,
    CONSTRAINT FK_Tarjeta_Cierre FOREIGN KEY (cierre_id) REFERENCES dbo.CajaCierre(id) ON DELETE CASCADE
);
GO
CREATE INDEX IX_CajaCierreTarjeta_Cierre ON dbo.CajaCierreTarjeta(cierre_id);
GO

## Notes
- All object names use plain ASCII, no accents, to avoid encoding issues.
- Consider adding unique index on (cierre_id, referencia) for tarjeta and cheque tables.
- Add auditing columns (modified_at, modified_by) if needed.

## Extended Flow (Including Save)
Ver el flujo gráfico detallado en el archivo: [Flujo_Caja.mmd](file:///c:/source/Cierre%20de%20Caja/Flujo_Caja.mmd)

### Save Sequence

1. Frontend builds JSON payload.
2. API validates required fields.
3. Header created, details inserted.
4. Returns closure id.

## Suggested Index Enhancements

```sql
CREATE UNIQUE INDEX UX_Tarjeta_Cierre_Ref ON dbo.CajaCierreTarjeta(cierre_id, referencia);
CREATE UNIQUE INDEX UX_Cheque_Cierre_Ref ON dbo.CajaCierreCheque(cierre_id, referencia);
```

## Database Initialization

Since the backend is pure FastAPI (Django has been removed from the stack), this schema must be executed directly in SQL Server Management Studio (SSMS) or via a raw `pyodbc` setup script to initialize the application database.
