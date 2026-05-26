# test_inversiones.py
# TAR04 - Suite de Pruebas - Modulo de Inversiones PayFlow
# Equipo: Gris | Taller de Pruebas
#
# Ejecucion:
#   pytest -v tests/test_inversiones.py
#   pytest --cov=inversiones tests/

import pytest
from inversiones import (
    PERFIL_BAJO, PERFIL_ALTO,
    ESTADO_DISPONIBLE, ESTADO_ESTABLE, ESTADO_RIESGOSA, ESTADO_RECHAZADA,
    TASA_BAJO_RIESGO, TASA_ALTO_RIESGO, PLAZO_MINIMO,
    obtener_tasa,
    validar_parametros,
    calcular_interes,
    estado_inicial,
    determinar_estado,
    validar_perfil_cuenta,
    generar_folio_inversion,
    autorizar_inversion,
)


# ===========================================================================
# CAPA INFERIOR — R1, R2, R3
# ===========================================================================
class TestObtenerTasa:
    """R2 — La tasa se determina por el perfil de inversion."""

    def test_bajo_riesgo_retorna_005(self):
        assert obtener_tasa(PERFIL_BAJO) == 0.05

    def test_alto_riesgo_retorna_012(self):
        assert obtener_tasa(PERFIL_ALTO) == 0.12

    def test_perfil_desconocido_retorna_tasa_bajo(self):
        """Error Guessing: perfil no reconocido cae en bajo riesgo por defecto."""
        assert obtener_tasa("otro") == TASA_BAJO_RIESGO


class TestValidarParametros:
    """R3 — No se permiten plazos < 12 meses ni montos negativos o cero."""

    def test_parametros_validos_no_lanza_excepcion(self):
        validar_parametros(1000.00, 12)  # no debe lanzar

    def test_capital_negativo_lanza_value_error(self):
        with pytest.raises(ValueError):
            validar_parametros(-500.00, 12)

    def test_capital_cero_lanza_value_error(self):
        with pytest.raises(ValueError):
            validar_parametros(0, 12)

    def test_plazo_menor_a_12_lanza_value_error(self):
        with pytest.raises(ValueError):
            validar_parametros(1000.00, 11)

    def test_plazo_exactamente_12_es_valido(self):
        """Valor limite: n=12 es el minimo aceptado."""
        validar_parametros(1000.00, 12)  # no debe lanzar

    def test_plazo_cero_lanza_value_error(self):
        with pytest.raises(ValueError):
            validar_parametros(1000.00, 0)

    def test_mensaje_error_capital_contiene_valor(self):
        with pytest.raises(ValueError, match="-500"):
            validar_parametros(-500.00, 12)

    def test_mensaje_error_plazo_contiene_minimo(self):
        with pytest.raises(ValueError, match="12"):
            validar_parametros(1000.00, 6)


class TestCalcularInteres:
    """R1 — Formula A = P*(1+r)^n con validacion de parametros."""

    def test_interes_bajo_riesgo_12_meses(self):
        """
        P=1000, r=0.05, n=12 -> A = 1000*(1.05)^12 = 1795.86
        Valor calculado manualmente como referencia.
        """
        resultado = calcular_interes(1000.00, PERFIL_BAJO, 12)
        assert resultado == pytest.approx(1795.86, abs=0.01)

    def test_interes_alto_riesgo_12_meses(self):
        """P=1000, r=0.12, n=12 -> A = 1000*(1.12)^12 = 3895.98"""
        resultado = calcular_interes(1000.00, PERFIL_ALTO, 12)
        assert resultado == pytest.approx(3895.98, abs=0.01)

    def test_interes_bajo_riesgo_24_meses(self):
        """P=4000, r=0.05, n=12 -> A = 4000*(1.05)^12 = 7183.43"""
        resultado = calcular_interes(4000.00, PERFIL_BAJO, 12)
        assert resultado == pytest.approx(7183.43, abs=0.01)

    def test_resultado_redondeado_a_2_decimales(self):
        resultado = calcular_interes(1000.00, PERFIL_BAJO, 12)
        assert resultado == round(resultado, 2)

    def test_lanza_error_con_capital_negativo(self):
        with pytest.raises(ValueError):
            calcular_interes(-100.00, PERFIL_BAJO, 12)

    def test_lanza_error_con_plazo_menor_a_12(self):
        with pytest.raises(ValueError):
            calcular_interes(1000.00, PERFIL_BAJO, 6)

    def test_capital_grande_no_causa_overflow(self):
        """Error Guessing: capital muy grande debe operar sin error."""
        resultado = calcular_interes(1_000_000.00, PERFIL_BAJO, 12)
        assert resultado > 1_000_000.00


# ===========================================================================
# CAPA SUPERIOR — R4, R5, R6
# ===========================================================================
class TestEstadoInicial:
    """R4 — El sistema inicia en DISPONIBLE."""

    def test_estado_inicial_es_disponible(self):
        assert estado_inicial() == ESTADO_DISPONIBLE

    def test_estado_inicial_es_string(self):
        assert isinstance(estado_inicial(), str)


class TestDeterminarEstado:
    """R5 — Transicion de estado segun el umbral del 50%."""

    def test_mas_del_50_porciento_es_riesgosa(self):
        """capital=6000, saldo=10000 -> 60% -> RIESGOSA"""
        assert determinar_estado(6000.00, 10000.00) == ESTADO_RIESGOSA

    def test_menos_del_50_porciento_es_estable(self):
        """capital=4000, saldo=10000 -> 40% -> ESTABLE"""
        assert determinar_estado(4000.00, 10000.00) == ESTADO_ESTABLE

    def test_exactamente_50_porciento_es_estable(self):
        """
        Valor limite: capital = saldo * 0.5 exactamente.
        La regla dice 'mas del 50%' -> 50% exacto es ESTABLE.
        """
        assert determinar_estado(5000.00, 10000.00) == ESTADO_ESTABLE

    def test_un_peso_sobre_mitad_es_riesgosa(self):
        """Valor limite: capital = saldo/2 + 0.01 -> RIESGOSA."""
        assert determinar_estado(5000.01, 10000.00) == ESTADO_RIESGOSA

    def test_capital_igual_al_saldo_es_riesgosa(self):
        """Error Guessing: invertir el 100% del saldo."""
        assert determinar_estado(10000.00, 10000.00) == ESTADO_RIESGOSA


class TestValidarPerfilCuenta:
    """R6 — Cuenta nueva (<3 meses) no puede elegir alto riesgo."""

    def test_cuenta_nueva_bajo_riesgo_es_valido(self):
        assert validar_perfil_cuenta(PERFIL_BAJO, 1) is True

    def test_cuenta_nueva_alto_riesgo_es_invalido(self):
        assert validar_perfil_cuenta(PERFIL_ALTO, 1) is False

    def test_cuenta_nueva_alto_riesgo_2_meses_invalido(self):
        assert validar_perfil_cuenta(PERFIL_ALTO, 2) is False

    def test_cuenta_3_meses_alto_riesgo_es_valido(self):
        """Valor limite: exactamente 3 meses -> puede elegir alto riesgo."""
        assert validar_perfil_cuenta(PERFIL_ALTO, 3) is True

    def test_cuenta_antigua_alto_riesgo_es_valido(self):
        assert validar_perfil_cuenta(PERFIL_ALTO, 12) is True

    def test_cuenta_antigua_bajo_riesgo_es_valido(self):
        assert validar_perfil_cuenta(PERFIL_BAJO, 12) is True


# ===========================================================================
# CAPA MEDIA — R7, R8, R9
# ===========================================================================
class TestGenerarFolioInversion:
    """R9 — Formato <PERFIL>-<ESTADO>-<MONTO_REDONDEADO>"""

    def test_folio_bajo_estable(self):
        assert generar_folio_inversion(PERFIL_BAJO, ESTADO_ESTABLE, 1250.75) == "B-E-1251"

    def test_folio_bajo_riesgosa(self):
        assert generar_folio_inversion(PERFIL_BAJO, ESTADO_RIESGOSA, 1250.75) == "B-R-1251"

    def test_folio_alto_estable(self):
        assert generar_folio_inversion(PERFIL_ALTO, ESTADO_ESTABLE, 3895.98) == "A-E-3896"

    def test_folio_alto_riesgosa(self):
        assert generar_folio_inversion(PERFIL_ALTO, ESTADO_RIESGOSA, 3895.98) == "A-R-3896"

    def test_folio_redondea_correctamente(self):
        """R9: el monto se redondea al entero mas proximo.
        Nota: Python usa banker rounding (round half to even):
        round(1250.50) = 1250 (par), round(1251.50) = 1252 (par).
        """
        assert generar_folio_inversion(PERFIL_BAJO, ESTADO_ESTABLE, 1250.49) == "B-E-1250"
        assert generar_folio_inversion(PERFIL_BAJO, ESTADO_ESTABLE, 1250.51) == "B-E-1251"

    def test_folio_ejemplo_del_enunciado(self):
        """Caso exacto del enunciado PRY01: B-E-1251 para monto=1250.75"""
        folio = generar_folio_inversion(PERFIL_BAJO, ESTADO_ESTABLE, 1250.75)
        assert folio == "B-E-1251"


class TestAutorizarInversion:
    """R7/R8 — Orquestador: autoriza o rechaza la inversion."""

    # -----------------------------------------------------------------------
    # SL-01 — Camino feliz end-to-end
    # -----------------------------------------------------------------------
    def test_inversion_autorizada_completa(self):
        """
        DADO saldo=10000, capital=4000, perfil=bajo, meses=6, n=12
        CUANDO se autoriza
        ENTONCES estado=AUTORIZADA, monto_final calculado, folio generado.
        """
        resultado = autorizar_inversion(
            capital=4000.00, saldo=10000.00,
            perfil=PERFIL_BAJO, meses_cuenta=6, n=12
        )
        assert resultado["estado"] == "AUTORIZADA"
        assert resultado["monto_final"] == pytest.approx(7183.43, abs=0.01)
        assert resultado["nuevo_estado"] == ESTADO_ESTABLE
        assert resultado["folio_aprobacion"] == "B-E-7183"

    # -----------------------------------------------------------------------
    # SL-03 — Saldo insuficiente
    # -----------------------------------------------------------------------
    def test_rechazada_por_saldo_insuficiente(self):
        """DADO saldo=3000 < capital=5000 -> RECHAZADA."""
        resultado = autorizar_inversion(
            capital=5000.00, saldo=3000.00,
            perfil=PERFIL_BAJO, meses_cuenta=6, n=12
        )
        assert resultado["estado"] == ESTADO_RECHAZADA
        assert resultado["folio_aprobacion"] is None
        assert resultado["monto_final"] is None

    # -----------------------------------------------------------------------
    # SL-04 — Cuenta nueva + alto riesgo
    # -----------------------------------------------------------------------
    def test_rechazada_cuenta_nueva_alto_riesgo(self):
        """DADO meses=1, perfil=alto -> RECHAZADA por restriccion R6."""
        resultado = autorizar_inversion(
            capital=1000.00, saldo=10000.00,
            perfil=PERFIL_ALTO, meses_cuenta=1, n=12
        )
        assert resultado["estado"] == ESTADO_RECHAZADA
        assert resultado["folio_aprobacion"] is None

    # -----------------------------------------------------------------------
    # SL-05 — Inversion riesgosa (>50% del saldo)
    # -----------------------------------------------------------------------
    def test_autorizada_con_estado_riesgosa(self):
        """DADO capital=5000 > 50% de saldo=8000 -> INVERSION_RIESGOSA."""
        resultado = autorizar_inversion(
            capital=5000.00, saldo=8000.00,
            perfil=PERFIL_ALTO, meses_cuenta=12, n=12
        )
        assert resultado["estado"] == "AUTORIZADA"
        assert resultado["nuevo_estado"] == ESTADO_RIESGOSA
        assert resultado["folio_aprobacion"].startswith("A-R-")

    # -----------------------------------------------------------------------
    # SL-06 — Exactamente el 50% del saldo
    # -----------------------------------------------------------------------
    def test_exactamente_50_porciento_es_estable(self):
        """Valor limite: capital = saldo * 0.5 exacto -> ESTABLE."""
        resultado = autorizar_inversion(
            capital=5000.00, saldo=10000.00,
            perfil=PERFIL_BAJO, meses_cuenta=6, n=12
        )
        assert resultado["nuevo_estado"] == ESTADO_ESTABLE

    # -----------------------------------------------------------------------
    # SL-07 — Exactamente 3 meses de antiguedad
    # -----------------------------------------------------------------------
    def test_3_meses_exactos_puede_elegir_alto_riesgo(self):
        """Valor limite: meses=3 -> no debe ser rechazada por perfil."""
        resultado = autorizar_inversion(
            capital=1000.00, saldo=10000.00,
            perfil=PERFIL_ALTO, meses_cuenta=3, n=12
        )
        assert resultado["estado"] == "AUTORIZADA"

    # -----------------------------------------------------------------------
    # Folio None en cualquier rechazo
    # -----------------------------------------------------------------------
    @pytest.mark.parametrize("capital,saldo,perfil,meses,n", [
        (5000.00, 3000.00, PERFIL_BAJO, 6,  12),   # saldo insuficiente
        (1000.00, 10000.00, PERFIL_ALTO, 1, 12),   # cuenta nueva alto riesgo
        (5000.00, 3000.00, PERFIL_ALTO, 1, 12),    # ambos criterios fallan
    ])
    def test_folio_es_none_en_todo_rechazo(self, capital, saldo, perfil, meses, n):
        """R9 — Condicion de disparo: rechazo siempre produce folio=None."""
        resultado = autorizar_inversion(capital, saldo, perfil, meses, n)
        assert resultado["folio_aprobacion"] is None
        assert resultado["estado"] == ESTADO_RECHAZADA

    # -----------------------------------------------------------------------
    # Error Guessing — plazo invalido propaga ValueError
    # -----------------------------------------------------------------------
    def test_plazo_invalido_lanza_excepcion(self):
        """
        Error Guessing: plazo < 12 debe lanzar ValueError
        antes de llegar al calculo.
        """
        with pytest.raises(ValueError):
            autorizar_inversion(
                capital=1000.00, saldo=10000.00,
                perfil=PERFIL_BAJO, meses_cuenta=6, n=6
            )

    # -----------------------------------------------------------------------
    # E2E adicional — flujo alto riesgo autorizado completo
    # -----------------------------------------------------------------------
    def test_e2e_alto_riesgo_autorizado(self):
        """
        E2E: cuenta madura, alto riesgo, capital < 50% saldo.
        Verifica integracion completa de las 3 capas.
        """
        resultado = autorizar_inversion(
            capital=3000.00, saldo=10000.00,
            perfil=PERFIL_ALTO, meses_cuenta=12, n=12
        )
        assert resultado["estado"] == "AUTORIZADA"
        assert resultado["nuevo_estado"] == ESTADO_ESTABLE
        assert resultado["monto_final"] == pytest.approx(11687.93, abs=0.01)
        assert resultado["folio_aprobacion"] == "A-E-11688"
