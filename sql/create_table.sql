IF OBJECT_ID('dbo.Stores', 'U') IS NOT NULL
    DROP TABLE dbo.Stores;
GO

CREATE TABLE dbo.Stores (
    id           INT IDENTITY(1,1)   NOT NULL,   
    branch_id    NVARCHAR(12)        NOT NULL,   
    store_name   NVARCHAR(255)       NOT NULL,
    address_line NVARCHAR(500)       NULL,
    city         NVARCHAR(100)       NULL,
    province     NVARCHAR(100)       NULL,
    postal_code  NVARCHAR(10)        NULL,
    latitude     DECIMAL(10, 7)      NULL,
    longitude    DECIMAL(10, 7)      NULL,
    loaded_at    DATETIME            NOT NULL DEFAULT GETDATE(),  

    CONSTRAINT PK_Stores       PRIMARY KEY CLUSTERED (id),
    CONSTRAINT UQ_Stores_BranchId UNIQUE (branch_id)
);
GO

CREATE NONCLUSTERED INDEX IX_Stores_Province
    ON dbo.Stores (province, city);
GO

PRINT 'dbo.Stores created successfully.';
GO