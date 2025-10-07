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

MERGE_SQL = """
MERGE INTO COLHEITAS t
USING (
  SELECT
    :id            AS id,
    TO_DATE(:data, 'YYYY-MM-DD') AS data_colheita,
    :talhao        AS talhao,
    :area_ha       AS area_ha,
    :prod_t_ha     AS prod_t_ha,
    :metodo        AS metodo,
    :preco_ton     AS preco_ton,
    :perda_pct     AS perda_pct,
    :perda_ton     AS perda_ton,
    :perda_reais   AS perda_reais,
    :total_ton     AS total_ton
  FROM dual
) s
ON (t.ID = s.id)
WHEN MATCHED THEN
  UPDATE SET
    t.DATA_COLHEITA = s.data_colheita,
    t.TALHAO        = s.talhao,
    t.AREA_HA       = s.area_ha,
    t.PROD_T_HA     = s.prod_t_ha,
    t.METODO        = s.metodo,
    t.PRECO_TON     = s.preco_ton,
    t.PERDA_PCT     = s.perda_pct,
    t.PERDA_TON     = s.perda_ton,
    t.PERDA_REAIS   = s.perda_reais,
    t.TOTAL_TON     = s.total_ton
WHEN NOT MATCHED THEN
  INSERT (ID, DATA_COLHEITA, TALHAO, AREA_HA, PROD_T_HA, METODO, PRECO_TON, PERDA_PCT, PERDA_TON, PERDA_REAIS, TOTAL_TON)
  VALUES (s.id, s.data_colheita, s.talhao, s.area_ha, s.prod_t_ha, s.metodo, s.preco_ton, s.perda_pct, s.perda_ton, s.perda_reais, s.total_ton)
"""


SELECT_SQL = "SELECT ID, TO_CHAR(DATA_COLHEITA, 'YYYY-MM-DD'), TALHAO, AREA_HA, PROD_T_HA, METODO, PRECO_TON, PERDA_PCT, PERDA_TON, PERDA_REAIS, TOTAL_TON FROM COLHEITAS"

DELETE_SQL = "DELETE FROM COLHEITAS WHERE ID = :1"
LISTAR_IDS_SQL = """
SELECT ID, TO_CHAR(DATA_COLHEITA, 'YYYY-MM-DD') AS DATA_COLHEITA, TALHAO
FROM COLHEITAS
ORDER BY DATA_COLHEITA DESC
"""
DELETE_ALL_SQL = "DELETE FROM COLHEITAS"


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
        afetados = 0
        for r in colheitas:
            binds = {
                "id": r["id"],
                "data": r["data"],
                "talhao": r["talhao"],
                "area_ha": r["area_ha"],
                "prod_t_ha": r["produtividade_t_ha"],
                "metodo": r["metodo"],
                "preco_ton": r["preco_ton"],
                "perda_pct": r["perda_pct"],
                "perda_ton": r["perda_ton"],
                "perda_reais": r["perda_reais"],
                "total_ton": r["total_ton"],
            }
            cur.execute(MERGE_SQL, binds)
            afetados += cur.rowcount or 0  # somatório aproximado
    conn.commit()
    return f"{len(colheitas)} registro(s) upsertado(s) no Oracle."


def consultar(conn):
    with conn.cursor() as cur:
        cur.execute(SELECT_SQL)
        return cur.fetchall()

def listar_ids(conn):
    with conn.cursor() as cur:
        cur.execute(LISTAR_IDS_SQL)
        return cur.fetchall()  # [(id, 'YYYY-MM-DD', talhao), ...]

def apagar_por_id(conn, id_str: str):
    with conn.cursor() as cur:
        cur.execute(DELETE_SQL, (id_str,))
        afetados = cur.rowcount
    conn.commit()
    return f"{afetados} registro(s) removido(s) do Oracle."

def apagar_todos(conn):
    with conn.cursor() as cur:
        cur.execute(DELETE_ALL_SQL)
        afetados = cur.rowcount
    conn.commit()
    return f"{afetados} registro(s) removido(s) do Oracle."
