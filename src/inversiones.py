# inversiones.py
# TAR04 - Modulo de Inversiones PayFlow
# Equipo: Gris | Taller de Pruebas
#
# Arquitectura Sandwich Testing (PRY01 / PRA05):
#   Capa Inferior  — calculos matematicos (R1-R3)
#   Capa Superior  — gestion de estados   (R4-R6)
#   Capa Media     — integracion          (R7-R9)

# ---------------------------------------------------------------------------
# Constantes de negocio
# ---------------------------------------------------------------------------
TASA_BAJO_RIESGO  = 0.05   # 5% anual
TASA_ALTO_RIESGO  = 0.12   # 12% anual
PLAZO_MINIMO      = 12     # meses (1 anio)
UMBRAL_RIESGOSA   = 0.50   # mas del 50% del saldo
MESES_CUENTA_NUEVA = 3     # menos de 3 meses = CUENTA_NUEVA

# Estados de cuenta
ESTADO_DISPONIBLE       = "DISPONIBLE"
ESTADO_ESTABLE          = "INVERSION_ESTABLE"
ESTADO_RIESGOSA         = "INVERSION_RIESGOSA"
ESTADO_RECHAZADA        = "RECHAZADA"

# Perfiles de inversion
PERFIL_BAJO  = "bajo_riesgo"
PERFIL_ALTO  = "alto_riesgo"


# ===========================================================================
# CAPA INFERIOR — Logica matematica
# Responsabilidad: calculos puros. No conoce estados ni perfiles de usuario.
# ===========================================================================

def obtener_tasa(perfil: str) -> float:
    """
    R2 — Retorna la tasa de interes segun el perfil de inversion.
    bajo_riesgo -> 0.05 | alto_riesgo -> 0.12
    """
    if perfil == PERFIL_ALTO:
        return TASA_ALTO_RIESGO
    return TASA_BAJO_RIESGO


def validar_parametros(capital: float, n: int) -> None:
    """
    R3 — Valida que el capital sea positivo y el plazo >= 12 meses.
    Lanza ValueError si alguna condicion no se cumple.
    """
    if capital <= 0:
        raise ValueError(f"El capital debe ser mayor a cero. Recibido: {capital}")
    if n < PLAZO_MINIMO:
        raise ValueError(
            f"El plazo minimo es {PLAZO_MINIMO} meses. Recibido: {n}"
        )


def calcular_interes(capital: float, perfil: str, n: int) -> float:
    """
    R1 — Calcula el monto final con la formula de interes compuesto:
         A = P * (1 + r)^n
    Valida los parametros antes de calcular (R3).
    Retorna el monto final redondeado a 2 decimales.
    """
    validar_parametros(capital, n)
    r = obtener_tasa(perfil)
    return round(capital * (1 + r) ** n, 2)


# ===========================================================================
# CAPA SUPERIOR — Gestion de estados
# Responsabilidad: transiciones de estado y restricciones de perfil.
# No realiza calculos matematicos.
# ===========================================================================

def estado_inicial() -> str:
    """
    R4 — Retorna el estado inicial de cualquier cuenta: DISPONIBLE.
    """
    return ESTADO_DISPONIBLE


def determinar_estado(capital: float, saldo: float) -> str:
    """
    R5 — Determina el nuevo estado segun la proporcion invertida:
         capital > 50% del saldo -> INVERSION_RIESGOSA
         capital <= 50% del saldo -> INVERSION_ESTABLE
    """
    if capital / saldo > UMBRAL_RIESGOSA:
        return ESTADO_RIESGOSA
    return ESTADO_ESTABLE


def validar_perfil_cuenta(perfil: str, meses_cuenta: int) -> bool:
    """
    R6 — Retorna True si el perfil es compatible con la antiguedad de la cuenta.
    Una cuenta con menos de 3 meses NO puede elegir alto_riesgo.
    Con exactamente 3 meses o mas, SI puede.
    """
    if perfil == PERFIL_ALTO and meses_cuenta < MESES_CUENTA_NUEVA:
        return False
    return True


# ===========================================================================
# CAPA MEDIA — Integracion
# Responsabilidad: orquestar ambas capas y empaquetar el resultado.
# ===========================================================================

def generar_folio_inversion(perfil: str, estado: str, monto_final: float) -> str:
    """
    R9 — Genera el folio de aprobacion con formato:
         <PERFIL>-<ESTADO>-<MONTO_FINAL_REDONDEADO>
    Codificacion:
         perfil: B = bajo_riesgo | A = alto_riesgo
         estado: E = INVERSION_ESTABLE | R = INVERSION_RIESGOSA
    Ejemplo: bajo_riesgo + ESTABLE + 1250.75 -> "B-E-1251"
    """
    codigo_perfil = "B" if perfil == PERFIL_BAJO else "A"
    codigo_estado = "E" if estado == ESTADO_ESTABLE else "R"
    monto_redondeado = round(monto_final)
    return f"{codigo_perfil}-{codigo_estado}-{monto_redondeado}"


def autorizar_inversion(
    capital: float,
    saldo: float,
    perfil: str,
    meses_cuenta: int,
    n: int,
) -> dict:
    """
    R7 / R8 — Orquestador principal. Verifica simultaneamente:
      1. Saldo suficiente para cubrir el capital (R7a).
      2. Perfil compatible con la antiguedad de la cuenta (R7b).
    Si ambos se cumplen:
      - Calcula monto_final (Capa Inferior)
      - Determina nuevo_estado (Capa Superior)
      - Genera folio_aprobacion (R9)
    Si alguno falla: estado=RECHAZADA, folio=None.

    Retorna dict con:
        estado            : str
        monto_final       : float | None
        nuevo_estado      : str  | None
        folio_aprobacion  : str  | None
    """
    # Condicion 1 — saldo suficiente
    saldo_suficiente = saldo >= capital

    # Condicion 2 — perfil compatible con antiguedad
    perfil_compatible = validar_perfil_cuenta(perfil, meses_cuenta)

    if not saldo_suficiente or not perfil_compatible:
        return {
            "estado": ESTADO_RECHAZADA,
            "monto_final": None,
            "nuevo_estado": None,
            "folio_aprobacion": None,
        }

    # Ambas condiciones OK — procesar inversion
    monto_final  = calcular_interes(capital, perfil, n)
    nuevo_estado = determinar_estado(capital, saldo)
    folio        = generar_folio_inversion(perfil, nuevo_estado, monto_final)

    return {
        "estado": "AUTORIZADA",
        "monto_final": monto_final,
        "nuevo_estado": nuevo_estado,
        "folio_aprobacion": folio,
    }
