# payflow_pago.py
# PRA10 - Pruebas de Regresion - PayFlow
# Equipo: Gris | Taller de Pruebas
#
# CAMBIO PRA10: El concepto "Internet" queda exento de la comision fija.
# Comision por concepto:
#   Renta   -> $15.00
#   Luz     -> $15.00
#   Internet -> $0.00  (nuevo - solicitud de cambio urgente)

from datetime import datetime

# ---------------------------------------------------------------------------
# Constantes de negocio
# ---------------------------------------------------------------------------
COMISION_FIJA = 15.00
CONCEPTOS_VALIDOS = {"Renta", "Internet", "Luz"}


def _obtener_comision(concepto: str) -> float:
    """
    [PRA10] Retorna la comision aplicable segun el concepto.
    Internet queda exento; Renta y Luz mantienen $15.00.
    Unico lugar donde vive la regla — si cambia otra vez, solo se toca aqui.
    """
    if concepto == "Internet":
        return 0.00
    return COMISION_FIJA


# ---------------------------------------------------------------------------
# CAPA SUPERIOR — Validacion
# Responsabilidad: decidir SI o NO segun reglas de negocio.
# NO realiza operaciones matematicas ni genera folios.
# ---------------------------------------------------------------------------
def validar_pago(saldo: float, monto: float, concepto: str) -> dict:
    """
    Verifica si el saldo cubre (monto + comision del concepto) y si el concepto es valido.
    [PRA10] La comision se calcula con _obtener_comision() para respetar la exencion de Internet.

    Retorna:
        {"autorizado": True/False, "motivo": str}
    """
    if concepto not in CONCEPTOS_VALIDOS:
        return {"autorizado": False, "motivo": f"Concepto '{concepto}' no valido. Use: {CONCEPTOS_VALIDOS}"}

    if monto <= 0:
        return {"autorizado": False, "motivo": "El monto debe ser mayor a cero."}

    # [PRA10] comision depende del concepto, no siempre es COMISION_FIJA
    comision = _obtener_comision(concepto)
    total_requerido = monto + comision
    if saldo < total_requerido:
        return {
            "autorizado": False,
            "motivo": f"Fondos Insuficientes. Requerido: ${total_requerido:.2f}, Disponible: ${saldo:.2f}",
        }

    return {"autorizado": True, "motivo": "Saldo suficiente."}


# ---------------------------------------------------------------------------
# CAPA INFERIOR — Calculo / Balance
# Responsabilidad: aritmetica pura. No sabe que es renta o internet.
# SIN CAMBIOS en PRA10 — recibe la comision como parametro, no la decide.
# ---------------------------------------------------------------------------
def calcular_nuevo_saldo(saldo: float, monto: float, comision: float) -> float:
    """
    Aplica la resta: nuevo_saldo = saldo - monto - comision.
    No valida reglas de negocio; solo opera con numeros.
    """
    return round(saldo - monto - comision, 2)


# ---------------------------------------------------------------------------
# CAPA MEDIA — Comprobante / Folio
# Responsabilidad: formatear y empaquetar el resultado confirmado.
# SIN CAMBIOS en PRA10.
# ---------------------------------------------------------------------------
def generar_folio(concepto: str, timestamp: str = None) -> str:
    """
    Genera un folio con formato: PAGO-<CONCEPTO><TIMESTAMP>
    Si no se proporciona timestamp se usa el momento actual (YYYYMMDDHHmmss).
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"PAGO-{concepto.upper()}{timestamp}"


# ---------------------------------------------------------------------------
# ORQUESTADOR — Funcion principal del flujo de negocio
# Recibe todos los datos, coordina las tres capas y devuelve el resultado.
# [PRA10] Pasa la comision correcta a calcular_nuevo_saldo via _obtener_comision().
# ---------------------------------------------------------------------------
def procesar_pago(id_usuario: str, concepto: str, monto: float, saldo: float) -> dict:
    """
    Orquesta el flujo completo de pago de servicio fijo:
      1. Valida disponibilidad (Capa Superior).
      2. Ejecuta el descuento (Capa Inferior).
      3. Emite el comprobante (Capa Media).

    Retorna un dict con:
        - estado:        "APROBADO" | "RECHAZADO"
        - nuevo_saldo:   float (sin cambio si rechazado)
        - folio:         str | None
        - motivo:        str (descripcion del resultado)
    """
    # Paso 1 — Validacion (Capa Superior)
    validacion = validar_pago(saldo, monto, concepto)

    if not validacion["autorizado"]:
        return {
            "estado": "RECHAZADO",
            "nuevo_saldo": saldo,
            "folio": None,
            "motivo": validacion["motivo"],
        }

    # [PRA10] Obtener la comision correcta antes de calcular
    comision = _obtener_comision(concepto)

    # Paso 2 — Calculo del nuevo saldo (Capa Inferior)
    nuevo_saldo = calcular_nuevo_saldo(saldo, monto, comision)

    # Paso 3 — Generacion del folio (Capa Media)
    folio = generar_folio(concepto)

    return {
        "estado": "APROBADO",
        "nuevo_saldo": nuevo_saldo,
        "folio": folio,
        "motivo": f"Pago de {concepto} realizado con exito. Comision aplicada: ${comision:.2f}",
    }
