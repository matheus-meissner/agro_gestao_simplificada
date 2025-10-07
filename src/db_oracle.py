"""
Conexão com Oracle (oracledb). Cria tabela, insere e consulta.
Config por ambiente: ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN
"""
import os
from typing import List, Dict
from dotenv import load_dotenv
load_dotenv()

try:
    import oracledb as cx_Oracle
except Exception:  # fallback para cx_Oracle clássico (se instalado)
    import cx_Oracle  # type: ignore

DDL = """
CREATE TABLE COLHEITAS (
    ID            VARCHAR2(36) PRIMARY KEY,
    DATA_COLHEITA DATE,
    TALHAO        VARCHAR2(100),
    AREA_HA       NUMBER(10,2),
    PROD_T_HA     NUMBER(10,2),
    METODO        VARCHAR2(20),
    PRECO_TON     NUMBER(10,2),
    PERDA_PCT     NUMBER(5,2),
    PERDA_TON     NUMBER(12,2),
    PERDA_REAIS   NUMBER(14,2),
    TOTAL_TON     NUMBER(14,2)
)
"""

INSERT_SQL = """
INSERT INTO COLHEITAS
(ID, DATA_COLHEITA, TALHAO, AREA_HA, PROD_T_HA, METODO, PRECO_TON, PERDA_PCT, PERDA_TON, PERDA_REAIS, TOTAL_TON)
VALUES (:1, TO_DATE(:2, 'YYYY-MM-DD'), :3, :4, :5, :6, :7, :8, :9, :10, :11)
"""

SELECT_SQL = "SELECT ID, TO_CHAR(DATA_COLHEITA, 'YYYY-MM-DD'), TALHAO, AREA_HA, PROD_T_HA, METODO, PRECO_TON, PERDA_PCT, PERDA_TON, PERDA_REAIS, TOTAL_TON FROM COLHEITAS"

def conectar():
    user = os.getenv("ORACLE_USER")
    pwd = os.getenv("ORACLE_PASSWORD")
    dsn = os.getenv("ORACLE_DSN")
    if not all([user, pwd, dsn]):
        raise RuntimeError("Variáveis de ambiente ORACLE_USER, ORACLE_PASSWORD e ORACLE_DSN não configuradas.")
    conn = cx_Oracle.connect(user=user, password=pwd, dsn=dsn)
    return conn

def criar_tabela(conn):
    try:
        with conn.cursor() as cur:
            cur.execute(DDL)
        conn.commit()
        return "Tabela COLHEITAS criada."
    except Exception as e:
        # ORA-00955: name is already used by an existing object (já existe)
        return f"Tabela já existente ou erro ao criar: {e}"

def exportar(colheitas: List[Dict], conn):
    if not colheitas:
        return "Sem dados para exportar."
    with conn.cursor() as cur:
        for r in colheitas:
            cur.execute(INSERT_SQL, (
                r["id"], r["data"], r["talhao"], r["area_ha"], r["produtividade_t_ha"],
                r["metodo"], r["preco_ton"], r["perda_pct"], r["perda_ton"], r["perda_reais"],
                r["total_ton"]
            ))
    conn.commit()
    return f"{len(colheitas)} registro(s) exportado(s) para Oracle."

def consultar(conn):
    with conn.cursor() as cur:
        cur.execute(SELECT_SQL)
        return cur.fetchall()
