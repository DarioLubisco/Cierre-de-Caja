-- ══════════════════════════════════════════════════════════════════════════════
-- Custom.CajaTransaccionesDolares
-- Registra cada transacción guardada desde la Calculadora Mixta.
-- Entradas = monto recibido del cliente por moneda
-- Salidas  = vuelto entregado al cliente por moneda
-- El saldo de dólares en caja = SUM(rec_ef_usd + rec_on_usd) - SUM(vuelto_usd)
-- ══════════════════════════════════════════════════════════════════════════════

IF NOT EXISTS (
    SELECT 1 FROM sys.tables t
    JOIN sys.schemas s ON s.schema_id = t.schema_id
    WHERE s.name = 'Custom' AND t.name = 'CajaTransaccionesDolares'
)
BEGIN
    CREATE TABLE Custom.CajaTransaccionesDolares (
        -- Identificación
        id              INT           NOT NULL IDENTITY(1,1) PRIMARY KEY,
        fecha           DATETIME      NOT NULL DEFAULT GETDATE(),
        vendedor_codigo VARCHAR(20)   NULL,         -- Vendedor que procesó (si aplica)
        observacion     NVARCHAR(255) NULL,          -- Nota libre

        -- Tasa del día
        tasa_bcv        DECIMAL(18,4) NOT NULL DEFAULT 0,

        -- Factura cobrada
        factura_bs      DECIMAL(18,2) NOT NULL DEFAULT 0,   -- Monto total de la factura en Bs
        factura_usd     DECIMAL(18,4) NOT NULL DEFAULT 0,   -- Equivalente en USD (factura_bs / tasa)

        -- ── ENTRADAS (Pagos recibidos del cliente) ─────────────────────────
        -- En Dólares
        rec_ef_usd      DECIMAL(18,2) NOT NULL DEFAULT 0,   -- Efectivo dólares recibidos
        rec_on_usd      DECIMAL(18,2) NOT NULL DEFAULT 0,   -- Zelle / transferencia USD

        -- En Bolívares (siempre se convierte a USD para el saldo)
        rec_ef_bs       DECIMAL(18,2) NOT NULL DEFAULT 0,   -- Efectivo Bs recibidos
        rec_pm_bs       DECIMAL(18,2) NOT NULL DEFAULT 0,   -- Pago Móvil recibido
        rec_bio_bs      DECIMAL(18,2) NOT NULL DEFAULT 0,   -- Biopago / Punto recibido

        -- Totales calculados de las entradas
        total_rec_usd   DECIMAL(18,4) NOT NULL DEFAULT 0,   -- Total recibido equivalente en USD
        total_rec_bs    DECIMAL(18,2) NOT NULL DEFAULT 0,   -- Total recibido equivalente en Bs

        -- ── SALIDAS (Vuelto entregado al cliente) ──────────────────────────
        vuelto_usd      DECIMAL(18,2) NOT NULL DEFAULT 0,   -- Vuelto en dólares efectivo
        vuelto_bs       DECIMAL(18,2) NOT NULL DEFAULT 0,   -- Vuelto en bolívares efectivo
        vuelto_pm_bs    DECIMAL(18,2) NOT NULL DEFAULT 0,   -- Vuelto por pago móvil

        -- Total vuelto en USD equivalente
        total_vuelto_usd DECIMAL(18,4) NOT NULL DEFAULT 0,

        -- ── RESULTADO ──────────────────────────────────────────────────────
        resultado       VARCHAR(10)   NOT NULL DEFAULT 'EXACTO',  -- 'VUELTO' | 'FALTA' | 'EXACTO'
        diff_usd        DECIMAL(18,4) NOT NULL DEFAULT 0,         -- positivo = vuelto, negativo = falta
        diff_bs         DECIMAL(18,2) NOT NULL DEFAULT 0,

        -- Auditoría
        created_at      DATETIME      NOT NULL DEFAULT GETDATE()
    );

    PRINT 'Tabla Custom.CajaTransaccionesDolares creada exitosamente.';
END
ELSE
BEGIN
    PRINT 'La tabla Custom.CajaTransaccionesDolares ya existe.';
END
GO

-- ── Índices para el reporte ──────────────────────────────────────────────────
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_CajaTrans_Fecha')
    CREATE NONCLUSTERED INDEX IX_CajaTrans_Fecha
        ON Custom.CajaTransaccionesDolares (fecha DESC);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_CajaTrans_Vendedor')
    CREATE NONCLUSTERED INDEX IX_CajaTrans_Vendedor
        ON Custom.CajaTransaccionesDolares (vendedor_codigo, fecha DESC);
GO

-- ── Vista de resumen diario (opcional, útil para el reporte) ─────────────────
IF OBJECT_ID('Custom.v_CajaDolaresDiario', 'V') IS NOT NULL
    DROP VIEW Custom.v_CajaDolaresDiario;
GO

CREATE VIEW Custom.v_CajaDolaresDiario AS
SELECT
    CAST(fecha AS DATE)         AS dia,
    vendedor_codigo,
    COUNT(*)                    AS nro_transacciones,

    -- Entradas
    SUM(rec_ef_usd)             AS total_efectivo_usd_entrada,
    SUM(rec_on_usd)             AS total_zelle_entrada,
    SUM(rec_ef_usd + rec_on_usd) AS total_usd_entrada,

    -- Bolívares recibidos
    SUM(rec_ef_bs)              AS total_bs_efectivo,
    SUM(rec_pm_bs)              AS total_bs_pagomovil,
    SUM(rec_bio_bs)             AS total_bs_biopago,

    -- Salidas de dólares (vuelto)
    SUM(vuelto_usd)             AS total_usd_salida,

    -- Saldo neto de dólares en caja
    SUM(rec_ef_usd + rec_on_usd) - SUM(vuelto_usd) AS saldo_usd_caja,

    -- Totales equivalentes
    SUM(total_rec_usd)          AS total_recibido_usd_equiv,
    SUM(total_vuelto_usd)       AS total_vuelto_usd_equiv
FROM Custom.CajaTransaccionesDolares
GROUP BY CAST(fecha AS DATE), vendedor_codigo;
GO

PRINT 'Vista Custom.v_CajaDolaresDiario creada.';
GO
