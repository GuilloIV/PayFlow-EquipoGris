# usuarios.py
# PayFlow MVP — Modulo de gestion de usuarios
# Equipo: Gris | Taller de Pruebas | UV FEI LIS 2026
#
# Responsabilidades:
#   - Login: buscar usuario en usuarios.csv y validar contrasena
#   - Actualizar saldo y estado despues de cada operacion
#   - Registrar cada operacion en historial.csv

import csv
import os
from datetime import datetime

# ---------------------------------------------------------------------------
# Rutas de archivos (relativas a la raiz del proyecto)
# ---------------------------------------------------------------------------
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USUARIOS_CSV  = os.path.join(BASE_DIR, "data", "usuarios.csv")
HISTORIAL_CSV = os.path.join(BASE_DIR, "data", "historial.csv")

CAMPOS_USUARIO = ["id_usuario", "password", "nombre",
                  "saldo", "meses_cuenta", "estado_cuenta"]
CAMPOS_HISTORIAL = ["id_usuario", "tipo", "fecha",
                    "concepto", "monto", "folio", "resultado"]


# ===========================================================================
# Lectura y escritura de CSV
# ===========================================================================

def _leer_usuarios() -> list[dict]:
    """Lee todos los usuarios del CSV y los retorna como lista de dicts."""
    if not os.path.exists(USUARIOS_CSV):
        return []
    with open(USUARIOS_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _escribir_usuarios(usuarios: list[dict]) -> None:
    """Sobreescribe el CSV con la lista de usuarios actualizada."""
    with open(USUARIOS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS_USUARIO)
        writer.writeheader()
        writer.writerows(usuarios)


def _agregar_historial(fila: dict) -> None:
    """Agrega una fila al historial.csv."""
    archivo_existe = os.path.exists(HISTORIAL_CSV)
    with open(HISTORIAL_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS_HISTORIAL)
        if not archivo_existe:
            writer.writeheader()
        writer.writerow(fila)


# ===========================================================================
# API publica del modulo
# ===========================================================================

def login(id_usuario: str, password: str) -> dict | None:
    """
    Busca el usuario en usuarios.csv y valida la contrasena.
    Retorna el dict del usuario si las credenciales son correctas,
    o None si no existe o la contrasena es incorrecta.
    """
    for usuario in _leer_usuarios():
        if (usuario["id_usuario"] == id_usuario and
                usuario["password"] == password):
            return {
                "id_usuario":   usuario["id_usuario"],
                "nombre":       usuario["nombre"],
                "saldo":        float(usuario["saldo"]),
                "meses_cuenta": int(usuario["meses_cuenta"]),
                "estado_cuenta":usuario["estado_cuenta"],
            }
    return None


def actualizar_usuario(id_usuario: str, nuevo_saldo: float,
                       nuevo_estado: str) -> None:
    """
    Actualiza el saldo y el estado de cuenta del usuario en usuarios.csv.
    Se llama despues de cada operacion aprobada.
    """
    usuarios = _leer_usuarios()
    for u in usuarios:
        if u["id_usuario"] == id_usuario:
            u["saldo"]         = f"{nuevo_saldo:.2f}"
            u["estado_cuenta"] = nuevo_estado
            break
    _escribir_usuarios(usuarios)


def registrar_operacion(id_usuario: str, tipo: str, concepto: str,
                        monto: float, folio: str | None,
                        resultado: str) -> None:
    """
    Agrega una fila al historial.csv con los datos de la operacion.
    tipo: 'PAGO' o 'INVERSION'
    """
    _agregar_historial({
        "id_usuario": id_usuario,
        "tipo":       tipo,
        "fecha":      datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "concepto":   concepto,
        "monto":      f"{monto:.2f}",
        "folio":      folio or "None",
        "resultado":  resultado,
    })


def obtener_historial(id_usuario: str) -> list[dict]:
    """
    Retorna todas las operaciones del usuario desde historial.csv.
    """
    if not os.path.exists(HISTORIAL_CSV):
        return []
    with open(HISTORIAL_CSV, newline="", encoding="utf-8") as f:
        todas = list(csv.DictReader(f))
    return [op for op in todas if op["id_usuario"] == id_usuario]
