import psycopg2
import pymysql
from sqlalchemy import create_engine
from config import (
    LP_HOST, LP_PORT, LP_USER, LP_PASS, LP_DB,
    CBBA_HOST, CBBA_PORT, CBBA_USER, CBBA_PASS, CBBA_DB,
    SC_HOST, SC_PORT, SC_USER, SC_PASS, SC_DB,
)


def get_conn_lapaz():
    return psycopg2.connect(
        host=LP_HOST, port=LP_PORT, database=LP_DB,
        user=LP_USER, password=LP_PASS,
    )


def get_conn_cochabamba():
    return pymysql.connect(
        host=CBBA_HOST, port=CBBA_PORT, database=CBBA_DB,
        user=CBBA_USER, password=CBBA_PASS,
        cursorclass=pymysql.cursors.DictCursor,
    )


def get_conn_santacruz():
    return psycopg2.connect(
        host=SC_HOST, port=SC_PORT, database=SC_DB,
        user=SC_USER, password=SC_PASS,
    )


def get_engine_lapaz():
    url = f"postgresql://{LP_USER}:{LP_PASS}@{LP_HOST}:{LP_PORT}/{LP_DB}"
    return create_engine(url)


def get_engine_cochabamba():
    url = f"mysql+pymysql://{CBBA_USER}:{CBBA_PASS}@{CBBA_HOST}:{CBBA_PORT}/{CBBA_DB}"
    return create_engine(url)


def get_engine_santacruz():
    url = f"postgresql://{SC_USER}:{SC_PASS}@{SC_HOST}:{SC_PORT}/{SC_DB}"
    return create_engine(url)


def test_conexion(get_conn_func):
    conn = None
    try:
        conn = get_conn_func()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        return True
    except Exception:
        return False
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def get_conn_by_sede(sede):
    if sede == "La Paz":
        return get_conn_lapaz()
    elif sede == "Cochabamba":
        return get_conn_cochabamba()
    elif sede == "Santa Cruz":
        return get_conn_santacruz()
    raise ValueError(f"Sede desconocida: {sede}")


def get_engine_by_sede(sede):
    if sede == "La Paz":
        return get_engine_lapaz()
    elif sede == "Cochabamba":
        return get_engine_cochabamba()
    elif sede == "Santa Cruz":
        return get_engine_santacruz()
    raise ValueError(f"Sede desconocida: {sede}")


def estado_nodos():
    return {
        "La Paz": test_conexion(get_conn_lapaz),
        "Cochabamba": test_conexion(get_conn_cochabamba),
        "Santa Cruz": test_conexion(get_conn_santacruz),
    }