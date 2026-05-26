# PayFlow — Equipo Gris

**Universidad Veracruzana | Facultad de Estadistica e Informatica**
**Licenciatura en Ingenieria de Software | EE: Taller de Pruebas | 2026**

Repositorio unificado del MVP de PayFlow. Implementado con arquitectura
Sandwich Testing (TDD por capas) cubriendo el modulo de inversiones (R1-R9)
y el modulo de pagos de servicios fijos.

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
├── src/
│   ├── __init__.py
│   ├── inversiones.py        # Modulo de inversiones — R1 a R9 (PRY01/PRA05/TAR04)
│   └── payflow_pago.py       # Modulo de pagos fijos (PRA08/PRA10)
├── tests/
│   ├── __init__.py
│   ├── test_inversiones.py   # 48 tests — cobertura 100%
│   └── test_pago_e2e.py      # 31 tests — cobertura 100%
├── docs/
│   ├── PRA08-EquipoGris.pdf
│   ├── PRA10-EquipoGris.pdf
│   ├── TAR04-EquipoGris.pdf
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
git clone https://github.com/TU_USUARIO/PayFlow-EquipoGris.git
cd PayFlow-EquipoGris

# 2. Crear entorno virtual
python3 -m venv .venv

# 3. Activar
source .venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt
```

### Windows

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

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

# Con reporte HTML
pytest --cov=inversiones --cov=payflow_pago --cov-report=html tests/
open htmlcov/index.html
```

---

## Complejidad ciclomatica (Radon)

```bash
radon cc src/inversiones.py src/payflow_pago.py -s
```

Todas las funciones deben mostrar calificacion **A** (complejidad 1-5).

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
