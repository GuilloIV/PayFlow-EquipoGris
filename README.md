# PayFlow — Equipo Gris

**Universidad Veracruzana | Facultad de Estadistica e Informatica**
**Licenciatura en Ingenieria de Software | EE: Taller de Pruebas | 2026**

Repositorio unificado del MVP de PayFlow. Implementado con arquitectura
Sandwich Testing (TDD por capas) cubriendo el modulo de inversiones (R1-R9)
y el modulo de pagos de servicios fijos, con interfaz de consola interactiva.

---

## Integrantes

| Nombre | Matricula |
|---|---|
| Jorge Manuel Cobos Castro | S23014045 |
| Marcos Zenon Sanchez Mendizabal | S23014093 |
| Guillermo Velazquez Rosiles | S23014116 |

---

## Estructura del proyecto

```
PayFlow-EquipoGris/
├── main.py                   # MVP consola interactivo — punto de entrada
├── src/
│   ├── __init__.py
│   ├── inversiones.py        # Modulo de inversiones R1-R9 (PRY01/PRA05/TAR04)
│   └── payflow_pago.py       # Modulo de pagos fijos (PRA08/PRA10)
├── tests/
│   ├── __init__.py
│   ├── test_inversiones.py   # 48 tests — cobertura 100%
│   └── test_pago_e2e.py      # 31 tests — cobertura 100%
├── docs/
│   ├── PRA08-EquipoGris.pdf  # Pruebas E2E al MVP
│   ├── PRA10-EquipoGris.pdf  # Pruebas de regresion
│   ├── TAR04-EquipoGris.pdf  # Integracion final
│   └── ValidadorInversiones_PayFlow.csv
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Requisitos previos

- Python 3.10 o superior
- Git 2.x o superior

```bash
python3 --version   # debe ser >= 3.10
git --version
```

---

## Configuracion del entorno

### Ubuntu / macOS

```bash
# 1. Clonar el repositorio
git clone https://github.com/GuilloIV/PayFlow-EquipoGris.git
cd PayFlow-EquipoGris

# 2. Crear entorno virtual
python3 -m venv .venv

# 3. Activar
source .venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Verificar
pytest --version
radon --version
```

### Windows

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## Ejecutar el MVP (consola interactiva)

```bash
source .venv/bin/activate   # si no esta activo
python3 main.py
```

El menu principal ofrece dos modulos:

```
MENU PRINCIPAL
  1.  Pago de Servicio Fijo    (Renta / Internet / Luz)
  2.  Inversion de Capital     (Bajo riesgo / Alto riesgo)
  3.  Salir
```

### Modulo 1 — Pago de Servicio Fijo
Ingresa concepto, monto y saldo. El sistema valida disponibilidad,
aplica la comision correspondiente (Internet: $0, Renta/Luz: $15)
y emite el folio de transaccion.

### Modulo 2 — Inversion de Capital
Ingresa capital, saldo, antiguedad de cuenta, perfil de riesgo y plazo.
El sistema calcula el rendimiento con interes compuesto A = P*(1+r)^n,
determina el estado de cuenta y genera el folio de aprobacion.

---

## Ejecucion de pruebas

```bash
# Suite completa (79 tests)
pytest

# Solo inversiones
pytest tests/test_inversiones.py

# Solo pagos
pytest tests/test_pago_e2e.py

# Con cobertura en terminal
pytest --cov=inversiones --cov=payflow_pago --cov-report=term-missing tests/

# Con reporte HTML (abre htmlcov/index.html)
pytest --cov=inversiones --cov=payflow_pago --cov-report=html tests/
```

---

## Complejidad ciclomatica (Radon)

```bash
radon cc src/inversiones.py src/payflow_pago.py -s
```

Todas las funciones muestran calificacion **A** (complejidad 1-5).

Para el indice de mantenibilidad:

```bash
radon mi src/inversiones.py src/payflow_pago.py
```

---

## Metricas del proyecto

| Modulo | Funciones | Tests | Cobertura | Radon |
|---|---|---|---|---|
| inversiones.py | 8 | 48 | 100% | A |
| payflow_pago.py | 5 | 31 | 100% | A |
| **Total** | **13** | **79** | **100%** | **A** |

---

## Historial de practicas

| Practica | Descripcion | Estado |
|---|---|---|
| PRY01 | TDD Sandwich Testing — Modulo de Inversiones | Completo |
| PRA05 | Validador de Inversiones PayFlow | Completo |
| PRA08 | Pruebas E2E al MVP — Pagos de servicios fijos | Completo |
| PRA09 | Gestion de defectos con tablero Kanban | Completo |
| PRA10 | Pruebas de regresion — exencion comision Internet | Completo |
| TAR04 | Integracion final — 79 tests, cobertura 100%, Radon A | Completo |
