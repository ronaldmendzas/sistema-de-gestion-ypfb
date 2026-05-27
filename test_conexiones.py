import psycopg2
import pymysql
from config import (
    LP_HOST, LP_PORT, LP_USER, LP_PASS, LP_DB,
    CBBA_HOST, CBBA_PORT, CBBA_USER, CBBA_PASS, CBBA_DB,
    SC_HOST, SC_PORT, SC_USER, SC_PASS, SC_DB,
)

print("=" * 60)
print("VERIFICACION DE CONEXIONES - SISTEMA DISTRIBUIDO YPFB")
print("=" * 60)

print(f"\n[1/3] La Paz (PostgreSQL) - {LP_HOST}:{LP_PORT}/{LP_DB}")
try:
    conn = psycopg2.connect(host=LP_HOST, port=LP_PORT, database=LP_DB, user=LP_USER, password=LP_PASS, connect_timeout=5)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM plantas")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    print(f"      \u2705 CONECTADO - {count} plantas registradas")
except Exception as e:
    print(f"      \u274c ERROR: {e}")

print(f"\n[2/3] Cochabamba (MySQL) - {CBBA_HOST}:{CBBA_PORT}/{CBBA_DB}")
try:
    conn = pymysql.connect(host=CBBA_HOST, port=CBBA_PORT, database=CBBA_DB, user=CBBA_USER, password=CBBA_PASS, connect_timeout=10)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM plantas")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    print(f"      \u2705 CONECTADO via Radmin VPN - {count} plantas registradas")
except Exception as e:
    print(f"      \u274c ERROR: {e}")

print(f"\n[3/3] Santa Cruz (PostgreSQL) - {SC_HOST}:{SC_PORT}/{SC_DB}")
try:
    conn = psycopg2.connect(host=SC_HOST, port=SC_PORT, database=SC_DB, user=SC_USER, password=SC_PASS, connect_timeout=10)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM plantas")
    count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM despachos_finanzas")
    count_fin = cur.fetchone()[0]
    cur.close()
    conn.close()
    print(f"      \u2705 CONECTADO via Radmin VPN - {count} plantas, {count_fin} registros financieros")
except Exception as e:
    print(f"      \u274c ERROR: {e}")

print("\n" + "=" * 60)
print("Verificacion completada. Ejecuta: streamlit run app.py")
print("=" * 60)