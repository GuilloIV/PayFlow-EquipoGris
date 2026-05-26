# test_pago_e2e.py
# PRA08 - Pruebas End to End al MPV - PayFlow
# Equipo: Gris | Taller de Pruebas
#
# Ejecución:
#   pytest -v test_pago_e2e.py
#   pytest --cov=payflow_pago test_pago_e2e.py          (cobertura básica)
#   pytest --cov=payflow_pago --cov-report=html test_pago_e2e.py  (reporte HTML)

import pytest
from payflow_pago import (
    COMISION_FIJA,
    CONCEPTOS_VALIDOS,
    calcular_nuevo_saldo,
    generar_folio,
    procesar_pago,
    validar_pago,
)


# ===========================================================================
# FIXTURES — cuenta de usuario reutilizable en varios tests
# ===========================================================================
@pytest.fixture
def cuenta_rica():
    """Usuario con saldo amplio para pagos exitosos."""
    return {"id": "USR-001", "saldo": 5000.00}


@pytest.fixture
def cuenta_justa():
    """Usuario con saldo apenas por encima del límite con comisión."""
    return {"id": "USR-002", "saldo": 1010.00}


# ===========================================================================
# CAPA SUPERIOR — Pruebas unitarias de validar_pago()
# ===========================================================================
class TestValidarPago:

    def test_saldo_suficiente_retorna_autorizado(self):
        """R: Saldo cubre monto + comisión → autorizado."""
        resultado = validar_pago(saldo=5000.00, monto=3500.00, concepto="Renta")
        assert resultado["autorizado"] is True

    def test_saldo_insuficiente_retorna_no_autorizado(self):
        """R: Saldo no cubre monto + comision -> rechazado.
        [PRA10] Cambiado concepto de Internet a Renta — Internet ya no cobra comision.
        """
        resultado = validar_pago(saldo=1010.00, monto=1000.00, concepto="Renta")
        assert resultado["autorizado"] is False
        assert "Fondos Insuficientes" in resultado["motivo"]

    def test_concepto_invalido_retorna_no_autorizado(self):
        """R: Concepto fuera del catálogo → rechazado sin tocar saldo."""
        resultado = validar_pago(saldo=9000.00, monto=500.00, concepto="Netflix")
        assert resultado["autorizado"] is False
        assert "no valido" in resultado["motivo"]

    def test_monto_cero_retorna_no_autorizado(self):
        """Error Guessing: monto=0 no tiene sentido en un pago."""
        resultado = validar_pago(saldo=5000.00, monto=0, concepto="Luz")
        assert resultado["autorizado"] is False

    def test_saldo_exactamente_igual_a_monto_mas_comision(self):
        """Valor límite: saldo == monto + comisión → debe ser autorizado."""
        monto = 1000.00
        saldo_exacto = monto + COMISION_FIJA  # 1015.00
        resultado = validar_pago(saldo=saldo_exacto, monto=monto, concepto="Internet")
        assert resultado["autorizado"] is True

    def test_saldo_un_centavo_menos_del_requerido(self):
        """Valor limite: saldo = monto + comision - 0.01 -> rechazado.
        [PRA10] Cambiado concepto de Internet a Renta — Internet ya no cobra comision.
        """
        monto = 1000.00
        saldo_insuficiente = monto + COMISION_FIJA - 0.01  # 1014.99
        resultado = validar_pago(saldo=saldo_insuficiente, monto=monto, concepto="Renta")
        assert resultado["autorizado"] is False

    @pytest.mark.parametrize("concepto", list(CONCEPTOS_VALIDOS))
    def test_todos_los_conceptos_validos_son_aceptados(self, concepto):
        """Partición de equivalencias: cada concepto del catálogo debe pasar."""
        resultado = validar_pago(saldo=9999.00, monto=100.00, concepto=concepto)
        assert resultado["autorizado"] is True


# ===========================================================================
# CAPA INFERIOR — Pruebas unitarias de calcular_nuevo_saldo()
# ===========================================================================
class TestCalcularNuevoSaldo:

    def test_resta_correcta(self):
        """R: 5000 - 3500 - 15 = 1485."""
        assert calcular_nuevo_saldo(5000.00, 3500.00, 15.00) == 1485.00

    def test_resultado_redondeado_a_dos_decimales(self):
        """R: El resultado siempre tiene 2 decimales."""
        resultado = calcular_nuevo_saldo(1000.00, 333.33, 15.00)
        assert resultado == round(1000.00 - 333.33 - 15.00, 2)

    def test_comision_es_independiente_del_concepto(self):
        """
        Bitácora de Slicing: la Capa Inferior recibe la comisión como parámetro;
        no conoce el concepto ni la regla de negocio que la origina.
        """
        # Mismo cálculo independientemente del contexto
        assert calcular_nuevo_saldo(2000.00, 500.00, 15.00) == 1485.00


# ===========================================================================
# CAPA MEDIA — Pruebas unitarias de generar_folio()
# ===========================================================================
class TestGenerarFolio:

    def test_folio_empieza_con_prefijo_pago(self):
        folio = generar_folio("Renta")
        assert folio.startswith("PAGO-RENTA")

    def test_folio_concepto_en_mayusculas(self):
        folio = generar_folio("internet")
        assert "INTERNET" in folio

    def test_folio_con_timestamp_fijo(self):
        """Stub de timestamp: permite asserts deterministas en CI."""
        folio = generar_folio("Luz", timestamp="20260517120000")
        assert folio == "PAGO-LUZ20260517120000"

    def test_folio_sin_timestamp_usa_hora_actual(self):
        """Sin stub: el folio debe tener al menos 10 caracteres tras 'PAGO-'."""
        folio = generar_folio("Renta")
        assert len(folio) > len("PAGO-RENTA")


# ===========================================================================
# PRUEBAS E2E — procesar_pago() (flujo completo end-to-end)
# ===========================================================================
class TestProcesarPagoE2E:

    # -----------------------------------------------------------------------
    # Escenario 1 — Pago exitoso (SL-01 análogo de PRA08)
    # -----------------------------------------------------------------------
    def test_pago_exitoso_renta(self, cuenta_rica):
        """
        DADO saldo=$5,000 | CUANDO paga Renta $3,500 + $15 comisión
        ENTONCES estado=APROBADO, nuevo_saldo=$1,485, folio generado.
        """
        resultado = procesar_pago(
            id_usuario=cuenta_rica["id"],
            concepto="Renta",
            monto=3500.00,
            saldo=cuenta_rica["saldo"],
        )
        assert resultado["estado"] == "APROBADO"
        assert resultado["nuevo_saldo"] == 1485.00
        assert resultado["folio"] is not None
        assert resultado["folio"].startswith("PAGO-RENTA")

    # -----------------------------------------------------------------------
    # Escenario 2 — Saldo insuficiente por comisión (SL-02 análogo)
    # -----------------------------------------------------------------------
    def test_pago_rechazado_por_comision(self, cuenta_justa):
        """
        DADO saldo=$1,010 | CUANDO paga Renta $1,000 + $15 comision ($1,015 total)
        ENTONCES estado=RECHAZADO, saldo original intacto, folio=None.
        [PRA10] Cambiado concepto de Internet a Renta: Internet ya no cobra comision,
        por lo que con saldo $1,010 y monto $1,000 ahora se APROBARIA.
        Renta sigue cobrando $15 — es el guardian correcto para este escenario.
        """
        saldo_original = cuenta_justa["saldo"]
        resultado = procesar_pago(
            id_usuario=cuenta_justa["id"],
            concepto="Renta",
            monto=1000.00,
            saldo=saldo_original,
        )
        assert resultado["estado"] == "RECHAZADO"
        assert resultado["nuevo_saldo"] == saldo_original  # saldo inmutable
        assert resultado["folio"] is None
        assert "Fondos Insuficientes" in resultado["motivo"]

    # -----------------------------------------------------------------------
    # Escenario 3 — Concepto inválido (SL-03 análogo)
    # -----------------------------------------------------------------------
    def test_pago_rechazado_concepto_invalido(self, cuenta_rica):
        """
        DADO concepto='Spotify' | CUANDO se intenta procesar
        ENTONCES estado=RECHAZADO antes de afectar el saldo.
        """
        saldo_original = cuenta_rica["saldo"]
        resultado = procesar_pago(
            id_usuario=cuenta_rica["id"],
            concepto="Spotify",
            monto=200.00,
            saldo=saldo_original,
        )
        assert resultado["estado"] == "RECHAZADO"
        assert resultado["nuevo_saldo"] == saldo_original  # saldo no modificado
        assert resultado["folio"] is None

    # -----------------------------------------------------------------------
    # Escenario 4 — Valor límite: saldo exactamente suficiente
    # -----------------------------------------------------------------------
    def test_pago_aprobado_saldo_exacto(self):
        """
        Valor límite: saldo == monto + comisión → debe aprobarse.
        """
        monto = 800.00
        saldo_exacto = monto + COMISION_FIJA  # 815.00
        resultado = procesar_pago(
            id_usuario="USR-LIM",
            concepto="Luz",
            monto=monto,
            saldo=saldo_exacto,
        )
        assert resultado["estado"] == "APROBADO"
        assert resultado["nuevo_saldo"] == 0.00

    # -----------------------------------------------------------------------
    # Escenario 5 — Valor límite: un centavo menos → rechazado
    # -----------------------------------------------------------------------
    def test_pago_rechazado_un_centavo_menos(self):
        """
        Valor límite: saldo = monto + comisión - 0.01 → rechazado.
        """
        monto = 800.00
        saldo_insuficiente = monto + COMISION_FIJA - 0.01  # 814.99
        resultado = procesar_pago(
            id_usuario="USR-LIM2",
            concepto="Luz",
            monto=monto,
            saldo=saldo_insuficiente,
        )
        assert resultado["estado"] == "RECHAZADO"
        assert resultado["nuevo_saldo"] == saldo_insuficiente

    # -----------------------------------------------------------------------
    # Escenario 6 — Error Guessing: monto negativo
    # -----------------------------------------------------------------------
    def test_pago_rechazado_monto_negativo(self, cuenta_rica):
        """
        Error Guessing: monto negativo no tiene sentido financiero → rechazado.
        """
        resultado = procesar_pago(
            id_usuario=cuenta_rica["id"],
            concepto="Renta",
            monto=-100.00,
            saldo=cuenta_rica["saldo"],
        )
        assert resultado["estado"] == "RECHAZADO"
        assert resultado["folio"] is None

    # -----------------------------------------------------------------------
    # Escenario 7 — Inmutabilidad del saldo ante cualquier rechazo
    # -----------------------------------------------------------------------
    @pytest.mark.parametrize("concepto,monto,saldo", [
        ("Netflix", 200.00, 5000.00),   # concepto inválido
        ("Renta",   200.00,  210.00),   # saldo insuficiente (200+15=215 > 210)
        ("Luz",      -50.00, 5000.00),  # monto negativo
    ])
    def test_saldo_inmutable_en_rechazos(self, concepto, monto, saldo):
        """
        Garantía E2E: ante cualquier tipo de rechazo el saldo no cambia.
        """
        resultado = procesar_pago("USR-X", concepto, monto, saldo)
        assert resultado["nuevo_saldo"] == saldo
        assert resultado["folio"] is None

    # -----------------------------------------------------------------------
    # Escenario 8 — Error Guessing: id_usuario vacío
    # Documenta que el sistema actual NO valida el ID (decisión de diseño).
    # Si en el futuro se agrega validación, este test debe actualizarse.
    # -----------------------------------------------------------------------
    def test_id_usuario_vacio_no_bloquea_pago_valido(self):
        """
        Error Guessing: id_usuario vacío string.
        El orquestador actual no valida el ID — el pago procede si
        saldo y concepto son válidos. Este test documenta ese comportamiento.
        """
        resultado = procesar_pago(
            id_usuario="",
            concepto="Luz",
            monto=100.00,
            saldo=500.00,
        )
        # El sistema no rechaza por ID vacío (no es responsabilidad del MVP)
        assert resultado["estado"] == "APROBADO"
        assert resultado["folio"] is not None


# ===========================================================================
# PRA10 — Pruebas de Regresion
# Nueva regla: Internet queda exento de la comision fija de $15.00
# ===========================================================================
class TestRegresionPRA10:

    # -----------------------------------------------------------------------
    # [NUEVO] Test de la nueva regla de negocio
    # TDD Fase Roja: este test falla con el codigo original de PRA08
    # TDD Fase Verde: pasa tras implementar _obtener_comision() en PRA10
    # -----------------------------------------------------------------------
    def test_pago_internet_sin_comision(self):
        """
        DADO saldo=$1,000 | CUANDO paga Internet $1,000 con comision=$0
        ENTONCES estado=APROBADO, nuevo_saldo=$0.00, folio generado.
        Regresion PRA10: Internet ya no paga comision fija.
        """
        resultado = procesar_pago(
            id_usuario="USR-REG",
            concepto="Internet",
            monto=1000.00,
            saldo=1000.00,
        )
        assert resultado["estado"] == "APROBADO"
        assert resultado["nuevo_saldo"] == 0.00
        assert resultado["folio"] is not None
        assert resultado["folio"].startswith("PAGO-INTERNET")

    # -----------------------------------------------------------------------
    # Guardianes de regresion — Renta y Luz deben seguir pagando $15.00
    # Estos tests documentan que el cambio NO afecto otros conceptos.
    # -----------------------------------------------------------------------
    def test_renta_mantiene_comision_fija(self):
        """
        Regresion: Renta sigue cobrando $15.00 de comision tras el cambio de PRA10.
        DADO saldo=$1,000, monto=$985 → total requerido $1,000 → APROBADO, saldo=$0.
        """
        resultado = procesar_pago(
            id_usuario="USR-REG2",
            concepto="Renta",
            monto=985.00,
            saldo=1000.00,
        )
        assert resultado["estado"] == "APROBADO"
        assert resultado["nuevo_saldo"] == 0.00

    def test_luz_mantiene_comision_fija(self):
        """
        Regresion: Luz sigue cobrando $15.00 de comision tras el cambio de PRA10.
        DADO saldo=$1,000, monto=$985 → total requerido $1,000 → APROBADO, saldo=$0.
        """
        resultado = procesar_pago(
            id_usuario="USR-REG3",
            concepto="Luz",
            monto=985.00,
            saldo=1000.00,
        )
        assert resultado["estado"] == "APROBADO"
        assert resultado["nuevo_saldo"] == 0.00

    def test_renta_rechazada_si_saldo_no_cubre_comision(self):
        """
        Regresion: Renta sigue siendo rechazada cuando el saldo cubre el monto
        pero NO la comision de $15.00. Confirma que la exencion de Internet
        no contamino la logica de Renta.
        """
        resultado = procesar_pago(
            id_usuario="USR-REG4",
            concepto="Renta",
            monto=1000.00,
            saldo=1000.00,   # alcanza el monto pero no el monto+$15
        )
        assert resultado["estado"] == "RECHAZADO"
        assert resultado["nuevo_saldo"] == 1000.00
        assert resultado["folio"] is None

    def test_internet_saldo_exactamente_igual_al_monto(self):
        """
        Valor limite PRA10: Internet con saldo == monto (sin margen para comision).
        Con la nueva regla debe APROBARSE porque comision=0.
        Con la regla vieja seria RECHAZADO (faltarian $15).
        """
        resultado = procesar_pago(
            id_usuario="USR-REG5",
            concepto="Internet",
            monto=500.00,
            saldo=500.00,
        )
        assert resultado["estado"] == "APROBADO"
        assert resultado["nuevo_saldo"] == 0.00
