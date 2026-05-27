# PLAN AVANZADO - SISTEMA DISTRIBUIDO YPFB BOLIVIA
## INF-262 Base de Datos III - UMSA 2026

---

## 1. MAPEO DE RED RADMIN VPN (IPS REALES)

```
┌─────────────────────────────────────────────────────────────────┐
│                    RED VPN: BASEDEDATOSIIII1                     │
├──────────┬──────────────┬──────────────────┬───────────────────┤
│ MIEMBRO  │    ROL       │   IP RADMIN      │   MOTOR BD        │
├──────────┼──────────────┼───────────────────┼───────────────────┤
│ Ronald   │ La Paz (LP)  │ 26.57.92.125     │ PostgreSQL 17     │
│          │ (localhost)  │ (equipo local)    │ puerto 5432       │
├──────────┼──────────────┼───────────────────┼───────────────────┤
│ Maya     │ Cochabamba   │ 26.157.52.238     │ MySQL Server 8    │
│ (PALTOP) │ (CBBA)      │                   │ puerto 3306       │
├──────────┼──────────────┼───────────────────┼───────────────────┤
│ Luis     │ Santa Cruz   │ 26.82.89.70       │ PostgreSQL 15+    │
│ (BETO)   │ (SC - Central)│                  │ puerto 5432       │
└──────────┴──────────────┴───────────────────┴───────────────────┘
```

**DETALLE CRÍTICO:** Ronald ejecuta Streamlit en localhost, por lo que
LP_HOST = "localhost" (conexion local al propio PostgreSQL).
CBBA_HOST = "26.157.52.238" (VPN hacia laptop de Maya).
SC_HOST = "26.82.89.70" (VPN hacia laptop de Luis/Beto).

---

## 2. PLAN DE PROVISIONAMIENTO DE BASES DE DATOS

### 2.1 Nodo La Paz (Ronald - localhost)

- [ ] Verificar PostgreSQL 17 instalado y corriendo en puerto 5432
- [ ] Crear base de datos: `CREATE DATABASE ypfb_la_paz;`
- [ ] Ejecutar script SQL: `lapaz PostgreSQL.txt`
- [ ] Verificar tablas creadas: plantas, carburantes, surtidores, stock_plantas, pedidos_web, despachos_lp
- [ ] Verificar datos insertados (2 despachos, 2 pedidos, 3 stocks)
- [ ] Configurar pg_hba.conf para permitir conexiones locales con password "1234"

### 2.2 Nodo Cochabamba (Maya - 26.157.52.238)

- [ ] Maya debe tener MySQL Server 8 instalado y corriendo en puerto 3306
- [ ] Crear base de datos: `CREATE DATABASE cochabamba;` (ya en script)
- [ ] Ejecutar script SQL: `cochabamba MySQL.txt`
- [ ] Verificar tablas: plantas, carburantes, surtidores, stock_plantas, pedidos_web, despachos_cbba
- [ ] Verificar AUTO_INCREMENT en 25001 para despachos_cbba
- [ ] Verificar AUTO_INCREMENT en 20001 para pedidos_web
- [ ] Configurar MySQL para aceptar conexiones remotas desde la VPN
- [ ] En MySQL: `GRANT ALL PRIVILEGES ON cochabamba.* TO 'root'@'26.57.92.125' IDENTIFIED BY 'root';`
- [ ] En MySQL: `GRANT ALL PRIVILEGES ON cochabamba.* TO 'root'@'%' IDENTIFIED BY 'root';`
- [ ] Abrir puerto 3306 en firewall de Windows de Maya

### 2.3 Nodo Santa Cruz (Luis/Beto - 26.82.89.70)

- [ ] Luis debe tener PostgreSQL 15+ instalado y corriendo en puerto 5432
- [ ] Crear base de datos: `CREATE DATABASE ypfb_santa_cruz;`
- [ ] Ejecutar script SQL: `santacruz PostgreSQL - copia.txt`
- [ ] Verificar tablas: plantas, carburantes, surtidores, stock_plantas, pedidos_web, despachos_sc, despachos_finanzas
- [ ] Verificar secuencias: seq_despachos_sc (START 35001), seq_pedidos_web (START 30001)
- [ ] Verificar datos en despachos_finanzas (5 registros con IDs 15XXX, 25XXX, 35XXX)
- [ ] Configurar pg_hba.conf para permitir conexiones desde VPN (host all all 26.0.0.0/8 md5)
- [ ] Configurar postgresql.conf: `listen_addresses = '*'`
- [ ] Abrir puerto 5432 en firewall de Windows de Luis

### 2.4 Script de Verificacion de Conectividad

Antes de programar nada, Ronald debe ejecutar desde Python:

```python
# test_conexiones.py - EJECUTAR PRIMERO
import psycopg2
import pymysql

# Test La Paz (localhost)
try:
    conn = psycopg2.connect(host="localhost", port=5432, 
                             database="ypfb_la_paz", user="postgres", password="1234")
    cur = conn.cursor(); cur.execute("SELECT 1"); conn.close()
    print("✅ La Paz (PostgreSQL) - CONECTADO")
except Exception as e:
    print(f"❌ La Paz - ERROR: {e}")

# Test Cochabamba (VPN Maya)
try:
    conn = pymysql.connect(host="26.157.52.238", port=3306,
                           database="cochabamba", user="root", password="root",
                           connect_timeout=10)
    cur = conn.cursor(); cur.execute("SELECT 1"); conn.close()
    print("✅ Cochabamba (MySQL) - CONECTADO via Radmin VPN")
except Exception as e:
    print(f"❌ Cochabamba - ERROR: {e}")

# Test Santa Cruz (VPN Luis)
try:
    conn = psycopg2.connect(host="26.82.89.70", port=5432,
                            database="ypfb_santa_cruz", user="postgres",
                            password="RosmerY06011996", connect_timeout=10)
    cur = conn.cursor(); cur.execute("SELECT 1"); conn.close()
    print("✅ Santa Cruz (PostgreSQL) - CONECTADO via Radmin VPN")
except Exception as e:
    print(f"❌ Santa Cruz - ERROR: {e}")
```

---

## 3. ARQUITECTURA DEL SISTEMA STREAMLIT

```
                ┌──────────────────────────────────────┐
                │         STREAMLIT APP (app.py)        │
                │         Puerto 8501 (localhost)        │
                │                                       │
                │  ┌─────────────┐  ┌───────────────┐  │
                │  │.session_state│  │  CSS Global   │  │
                │  │ sede_activa  │  │  Paleta YPFB  │  │
                │  │ log_2pc      │  │  #003366      │  │
                │  │ df_reconstr.  │  │  #CC0000      │  │
                │  └─────────────┘  └───────────────┘  │
                └──────────────┬───────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
   ┌────▼─────┐          ┌─────▼──────┐        ┌──────▼─────┐
   │bienvenida│          │modelo_datos│        │panel_control│
   │   .py    │          │    .py     │        │    .py     │
   └──────────┘          └────────────┘        └──────┬─────┘
                                                      │
                              ┌────────────────────────┤
                              │                        │
                     ┌────────▼────────┐      ┌────────▼────────┐
                     │ protocolo_2pc.py │      │ reconstruccion.py│
                     │  (2PC Emulado)   │      │  (Pandas concat  │
                     │                  │      │   + merge)       │
                     └────────┬────────┘      └────────┬────────┘
                              │                        │
                     ┌────────▼────────────────────────▼────┐
                     │          conexiones.py                │
                     │  get_conn_lapaz()  → localhost:5432   │
                     │  get_conn_cochabamba() → 26.157.52.238 │
                     │  get_conn_santacruz() → 26.82.89.70    │
                     └────────────────────────────────────────┘
```

---

## 4. FLUJO DE DATOS DEL PROTOCOLO 2PC

```
OPERADOR PRESIONA "APROBAR DESPACHO"
                │
                ▼
    ┌───────────────────────┐
    │  FASE 1: PREPARE     │
    │                       │
    │  Paso 1: test_conexion│──→ NODO LOCAL (LP o CBBA)
    │  Paso 2: test_conexion│──→ NODO SANTA CRUZ (finanzas)
    │  Paso 3: SELECT stock │──→ stock_plantas local
    │  Paso 4: litros <=   │──→ Validar stock suficiente
    │           stock?      │
    └───────────┬───────────┘
                │
        ┌───────┴───────┐
        │ ¿Todo OK?     │
        ├─── NO ────────┤ → ROLLBACK → st.error()
        │               │
        SI              │
        │               │
    ┌───▼─────────────────┐
    │  FASE 2: COMMIT    │
    │                     │
    │  Paso 1: INSERT    │──→ pedidos_web (local)
    │  Paso 2: INSERT    │──→ despachos_lp/cbba/sc (local)
    │  Paso 3: UPDATE    │──→ stock_plantas (local) DESCONTAR
    │  Paso 4: CALCULAR  │──→ costo = litros * 8.50
    │        finanzas    │──→ subvencion = (8.50 - precio) * litros
    │  Paso 5: INSERT    │──→ despachos_finanzas (SANTA CRUZ)
    └───────────┬────────┘
                │
        ┌───────┴───────┐
        │ ¿Todo OK?     │
        ├─── NO ────────┤ → ROLLBACK MANUAL (DELETE inserciones)
        │               │
        SI              │
        │               │
    ┌───▼─────────────────┐
    │  ✅ TRANSACCIÓN     │
    │     COMPLETADA      │
    └─────────────────────┘
```

---

## 5. FLUJO DE RECONSTRUCCIÓN HÍBRIDA (SOLO SANTA CRUZ)

```
GERENTE PRESIONA "EJECUTAR RECONSTRUCCIÓN DISTRIBUIDA"
                │
                ▼
    ┌───────────────────────────────────┐
    │  FASE 1: EXTRACCIÓN               │
    │                                    │
    │  df_LP   = pd.read_sql(           │
    │    'SELECT * FROM despachos_lp',  │
    │    conn_LP)                        │  ← PostgreSQL localhost o VPN
    │                                    │
    │  df_CBBA = pd.read_sql(           │
    │    'SELECT * FROM despachos_cbba',│
    │    conn_CBBA)                      │  ← MySQL via VPN
    │                                    │
    │  df_SC   = pd.read_sql(           │
    │    'SELECT * FROM despachos_sc',  │
    │    conn_SC)                        │  ← PostgreSQL VPN/localhost
    └───────────┬───────────────────────┘
                │
                ▼
    ┌───────────────────────────────────┐
    │  FASE 2: UNIÓN HORIZONTAL (∪)    │
    │                                    │
    │  Homologar timestamps con          │
    │  pd.to_datetime()                 │
    │                                    │
    │  Cast PKs/FKs a int64             │
    │                                    │
    │  df_operativos = pd.concat(       │
    │    [df_LP, df_CBBA, df_SC],       │
    │    ignore_index=True)             │
    └───────────┬───────────────────────┘
                │
                ▼
    ┌───────────────────────────────────┐
    │  FASE 3: JUNTA VERTICAL (⋈)      │
    │                                    │
    │  df_finanzas = pd.read_sql(       │
    │    'SELECT * FROM despachos_finanzas',│
    │    conn_SC)                        │
    │                                    │
    │  df_final = pd.merge(             │
    │    df_operativos, df_finanzas,     │
    │    on='id_despacho',               │
    │    how='inner')                    │
    └───────────┬───────────────────────┘
                │
                ▼
    ┌───────────────────────────────────┐
    │  RESULTADO: DESPACHOS_Global      │
    │                                    │
    │  id_despacho | id_pedido | id_    │
    │  plantas | litros_despachados |   │
    │  fecha_despacho | placa_cisterna │
    │  | costo_importacion_real |       │
    │  subvencion_asumida_bs            │
    │                                    │
    │  + Gráfico Barras (x depto)       │
    │  + Gráfico Donut (x carburante)   │
    └───────────────────────────────────┘
```

---

## 6. MAPEO DE SEDIDORES POR NODO

```
La Paz (id_plantas = 10):
  - Surtidor 101: Volcán - Av. Montes
  - Surtidor 102: San Pedro

Cochabamba (id_plantas = 20):
  - Surtidor 201: Cala Cala
  - Surtidor 202: Muyurina

Santa Cruz (id_plantas = 30):
  - Surtidor 301: El Cristo
```

---

## 7. SECUENCIA DE IDs POR NODO

```
La Paz:
  id_pedido:     secuencia desde 10001
  id_despacho:   secuencia desde 15001
  id_stock:      1001, 1002, 1003

Cochabamba:
  id_pedido:     AUTO_INCREMENT desde 20001
  id_despacho:  AUTO_INCREMENT desde 25001
  id_stock:      2001, 2002

Santa Cruz:
  id_pedido:     secuencia desde 30001
  id_despacho:   secuencia desde 35001
  id_stock:      3001, 3002
```

---

## 8. MODOS DE FUNCIONAMIENTO

### MODO COMPLETO (VPN activa, 3 nodos conectados)
- Todas las funciones disponibles
- 2PC con commit remoto a Santa Cruz
- Reconstrucción global con datos de los 3 nodos
- Gráficos con datos nacionales completos

### MODO DEGRADADO (algunos nodos caídos)
- Si Cochabamba cae: Label operativa La Paz + Santa Cruz
  - 2PC funcionará solo para La Paz y Santa Cruz
  - st.warning("Nodo Cochabamba no disponible")
- Si Santa Cruz cae: Sin finanzas, sin reconstrucción global
  - 2PC FALLARÁ en Fase 2 (no se puede insertar finanzas)
  - Solo operaciones locales disponibles
- Si La Paz cae: Solo administrador desde otro nodo
  - La app corre local, usa localhost para La Paz

### MODO OFFLINE LOCAL (solo La Paz)
- Despachos locales funcionan
- Sin reconstrucción global
- Sin finanzas remotas
- st.warning en cada intento de operación remota

---

## 9. RESPONSABILIDADES DEL EQUIPO

### Ronald (La Paz - Desarrollador Principal)
- Desarrolla el sistema Streamlit completo
- Ejecuta PostgreSQL 17 localmente
- Ejecuta `streamlit run app.py` en su máquina
- Comparte pantalla durante la defensa
- Coordina pruebas de conectividad VPN

### Maya (Cochabamba - Nodo MySQL)
- Instalar MySQL Server 8
- Ejecutar script `cochabamba MySQL.txt`
- Configurar acceso remoto MySQL
- Abrir puerto 3306 en firewall
- Verificar conexion desde la VPN

### Luis/Beto (Santa Cruz - Nodo Central)
- Instalar PostgreSQL 15+
- Ejecutar script `santacruz PostgreSQL - copia.txt`
- Configurar pg_hba.conf y postgresql.conf para acceso remoto
- Abrir puerto 5432 en firewall
- Verificar que despachos_finanzas tenga los 5 registros

---

## 10. CRONOGRAMA DE DESARROLLO

### Fase 1: Infraestructura (Día previo)
- [ ] Ronald: Instalar PostgreSQL 17, crear BD ypfb_la_paz, ejecutar script
- [ ] Maya: Instalar MySQL 8, crear BD cochabamba, ejecutar script, abrir puertos
- [ ] Luis: Instalar PostgreSQL 15+, crear BD ypfb_santa_cruz, ejecutar script, abrir puertos
- [ ] Todos: Activar Radmin VPN y verificar conectividad con test_conexiones.py

### Fase 2: Desarrollo del Sistema (Ronald)
- [ ] config.py - Constantes e IPs
- [ ] conexiones.py - Funciones de conexión a 3 nodos
- [ ] protocolo_2pc.py - Lógica del Two-Phase Commit
- [ ] reconstruccion.py - Pipeline Pandas (concat + merge)
- [ ] app.py - Entrada principal Streamlit con sidebar y CSS
- [ ] pages/bienvenida.py - Portal Nacional con cards interactivas
- [ ] pages/modelo_datos.py - Diagrama ER + Fragmentación
- [ ] pages/panel_control.py - Panel distribuido (3 vistas)

### Fase 3: Pruebas (Día de la defensa)
- [ ] Verificar 3 nodos conectados
- [ ] Simular despacho desde La Paz
- [ ] Simular despacho desde Cochabamba
- [ ] Ejecutar reconstrucción global desde Santa Cruz
- [ ] Verificar gráficos generados
- [ ] Simular caída de nodo (desconectar VPN)
- [ ] Verificar modo degradado

---

## 11. LISTA DE VERIFICACIÓN PRE-DEFENSA

```
☐ PostgreSQL 17 corriendo en Ronald (localhost:5432)
☐ MySQL 8 corriendo en Maya (26.157.52.238:3306)
☐ PostgreSQL 15+ corriendo en Luis (26.82.89.70:5432)
☐ Radmin VPN conectada los 3 miembros
☐ test_conexiones.py ejecutado → 3 ✅
☐ Streamlit instalado (pip install -r requirements.txt)
☐ app.py ejecuta sin errores
☐ Despacho La Paz funciona
☐ Despacho Cochabamba funciona  
☐ Despacho Santa Cruz funciona
☐ Reconstrucción global produce tabla completa
☐ Gráfico de barras por departamento funciona
☐ Gráfico donut de subvención funciona
☐ Modo degradado no crashea la app
☐ Acceso denegado funciona (LP/CBBA no ven finanzas)
```