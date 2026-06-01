# main.py
# PayFlow MVP — Interfaz de consola
# Equipo: Gris | Taller de Pruebas | UV FEI LIS 2026

import sys
import os

# Asegurar que src/ este en el path cuando se ejecuta desde la raiz
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from payflow_pago import procesar_pago, CONCEPTOS_VALIDOS, COMISION_FIJA
from inversiones import (
    autorizar_inversion,
    PERFIL_BAJO, PERFIL_ALTO,
    ESTADO_RECHAZADA,
)

# ── Colores ANSI ─────────────────────────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    PURPLE  = "\033[95m"
    CYAN    = "\033[96m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    GRAY    = "\033[90m"
    WHITE   = "\033[97m"

def clr(text, color):
    return f"{color}{text}{C.RESET}"

# ── Utilidades de pantalla ────────────────────────────────────────────────────
def limpiar():
    os.system("clear" if os.name != "nt" else "cls")

def linea(char="─", ancho=60, color=C.GRAY):
    print(clr(char * ancho, color))

def titulo(texto, color=C.PURPLE):
    limpiar()
    linea("═", 60, color)
    print(clr(f"  {texto}", C.BOLD + color))
    linea("═", 60, color)
    print()

def pausar():
    print()
    input(clr("  Presiona Enter para continuar...", C.GRAY))

def pedir_float(prompt, minimo=0.01):
    while True:
        try:
            valor = float(input(clr(f"  {prompt}: ", C.CYAN)))
            if valor < minimo:
                print(clr(f"  El valor debe ser mayor a {minimo}.", C.RED))
            else:
                return valor
        except ValueError:
            print(clr("  Ingresa un numero valido.", C.RED))

def pedir_int(prompt, minimo=1):
    while True:
        try:
            valor = int(input(clr(f"  {prompt}: ", C.CYAN)))
            if valor < minimo:
                print(clr(f"  El valor debe ser al menos {minimo}.", C.RED))
            else:
                return valor
        except ValueError:
            print(clr("  Ingresa un numero entero valido.", C.RED))

def pedir_opcion(prompt, opciones):
    while True:
        resp = input(clr(f"  {prompt}: ", C.CYAN)).strip()
        if resp in opciones:
            return resp
        print(clr(f"  Opcion no valida. Elige entre: {', '.join(opciones)}", C.RED))

# ── Banner principal ──────────────────────────────────────────────────────────
def banner():
    limpiar()
    print()
    print(clr("  ██████╗  █████╗ ██╗   ██╗███████╗██╗      ██████╗ ██╗    ██╗", C.PURPLE))
    print(clr("  ██╔══██╗██╔══██╗╚██╗ ██╔╝██╔════╝██║     ██╔═══██╗██║    ██║", C.PURPLE))
    print(clr("  ██████╔╝███████║ ╚████╔╝ █████╗  ██║     ██║   ██║██║ █╗ ██║", C.PURPLE))
    print(clr("  ██╔═══╝ ██╔══██║  ╚██╔╝  ██╔══╝  ██║     ██║   ██║██║███╗██║", C.PURPLE))
    print(clr("  ██║     ██║  ██║   ██║   ██║     ███████╗╚██████╔╝╚███╔███╔╝", C.PURPLE))
    print(clr("  ╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝ ", C.PURPLE))
    print()
    print(clr("         Sistema de Gestion Financiera Personal — MVP v1.0", C.WHITE))
    print(clr("         Equipo Gris | Taller de Pruebas | UV FEI LIS 2026", C.GRAY))
    print()
    linea("─", 60, C.GRAY)
    print()

# ── Menu principal ────────────────────────────────────────────────────────────
def menu_principal():
    banner()
    print(clr("  MENU PRINCIPAL", C.BOLD + C.WHITE))
    print()
    print(clr("  1.", C.YELLOW) + "  Pago de Servicio Fijo")
    print(clr("     ", C.GRAY) + clr("Renta / Internet / Luz", C.GRAY))
    print()
    print(clr("  2.", C.YELLOW) + "  Inversion de Capital")
    print(clr("     ", C.GRAY) + clr("Bajo riesgo / Alto riesgo", C.GRAY))
    print()
    print(clr("  3.", C.RED) + "  Salir")
    print()
    linea("─", 60, C.GRAY)
    return pedir_opcion("Selecciona una opcion (1/2/3)", ["1", "2", "3"])

# ════════════════════════════════════════════════════════════════════════════════
# MODULO 1 — PAGO DE SERVICIOS
# ════════════════════════════════════════════════════════════════════════════════
def flujo_pago():
    titulo("PAGO DE SERVICIO FIJO", C.CYAN)

    print(clr("  Conceptos disponibles:", C.WHITE))
    for c in sorted(CONCEPTOS_VALIDOS):
        comision = 0.00 if c == "Internet" else COMISION_FIJA
        tag = clr("(sin comision)", C.GREEN) if comision == 0 else clr(f"(+ ${comision:.2f} comision)", C.YELLOW)
        print(f"    {clr('•', C.CYAN)} {c} {tag}")
    print()

    id_usuario = input(clr("  ID de usuario: ", C.CYAN)).strip() or "USR-001"

    concepto = input(clr("  Concepto (Renta / Internet / Luz): ", C.CYAN)).strip().capitalize()
    if concepto not in CONCEPTOS_VALIDOS:
        print(clr(f"\n  Concepto '{concepto}' no valido.", C.RED))
        pausar()
        return

    monto = pedir_float("Monto a pagar ($)")
    saldo = pedir_float("Saldo disponible ($)")

    print()
    linea("─", 60, C.GRAY)
    print(clr("  Procesando pago...", C.YELLOW))
    linea("─", 60, C.GRAY)

    resultado = procesar_pago(id_usuario, concepto, monto, saldo)

    print()
    if resultado["estado"] == "APROBADO":
        print(clr("  ✓ PAGO APROBADO", C.BOLD + C.GREEN))
        print()
        print(f"  {'Concepto':<20} {concepto}")
        print(f"  {'Monto pagado':<20} ${monto:,.2f}")
        comision_aplicada = saldo - resultado["nuevo_saldo"] - monto
        print(f"  {'Comision':<20} ${comision_aplicada:,.2f}")
        print(f"  {'Saldo anterior':<20} ${saldo:,.2f}")
        saldo_nuevo_fmt = clr(f'${resultado["nuevo_saldo"]:,.2f}', C.GREEN)
        print(f"  {'Saldo nuevo':<20} {saldo_nuevo_fmt}")
        print(f"  {'Folio':<20} {clr(resultado['folio'], C.CYAN)}")
    else:
        print(clr("  ✗ PAGO RECHAZADO", C.BOLD + C.RED))
        print()
        print(f"  {clr('Motivo:', C.YELLOW)} {resultado['motivo']}")
        print(f"  {clr('Saldo actual:', C.WHITE)} ${resultado['nuevo_saldo']:,.2f}")
        print(f"  {clr('Folio:', C.WHITE)} {resultado['folio'] or 'No generado'}")

    print()
    linea("─", 60, C.GRAY)
    pausar()

# ════════════════════════════════════════════════════════════════════════════════
# MODULO 2 — INVERSION DE CAPITAL
# ════════════════════════════════════════════════════════════════════════════════
def flujo_inversion():
    titulo("INVERSION DE CAPITAL", C.PURPLE)

    print(clr("  Perfiles disponibles:", C.WHITE))
    print(f"    {clr('•', C.CYAN)} bajo_riesgo  {clr('(tasa 5% anual)', C.GRAY)}")
    print(f"    {clr('•', C.CYAN)} alto_riesgo  {clr('(tasa 12% anual — requiere cuenta >= 3 meses)', C.GRAY)}")
    print()

    id_usuario   = input(clr("  ID de usuario: ", C.CYAN)).strip() or "USR-001"
    capital      = pedir_float("Capital a invertir ($)")
    saldo        = pedir_float("Saldo actual en cuenta ($)")
    meses_cuenta = pedir_int("Antiguedad de la cuenta (meses)", minimo=1)

    print()
    perfil = pedir_opcion("Perfil de inversion (bajo_riesgo / alto_riesgo)",
                          [PERFIL_BAJO, PERFIL_ALTO])

    plazo = pedir_int("Plazo de inversion (meses, minimo 12)", minimo=12)

    print()
    linea("─", 60, C.GRAY)
    print(clr("  Procesando inversion...", C.YELLOW))
    linea("─", 60, C.GRAY)

    try:
        resultado = autorizar_inversion(capital, saldo, perfil, meses_cuenta, plazo)
    except ValueError as e:
        print()
        print(clr(f"  ✗ PARAMETROS INVALIDOS: {e}", C.BOLD + C.RED))
        pausar()
        return

    print()
    if resultado["estado"] == "AUTORIZADA":
        tasa = 0.12 if perfil == PERFIL_ALTO else 0.05
        rendimiento = resultado["monto_final"] - capital
        print(clr("  ✓ INVERSION AUTORIZADA", C.BOLD + C.GREEN))
        print()
        print(f"  {'Capital invertido':<25} ${capital:,.2f}")
        print(f"  {'Perfil':<25} {perfil}  {clr(f'(tasa {tasa*100:.0f}%)', C.GRAY)}")
        print(f"  {'Plazo':<25} {plazo} meses")
        monto_fmt = clr(f'${resultado["monto_final"]:,.2f}', C.GREEN)
        print(f"  {'Monto final':<25} {monto_fmt}")
        print(f"  {'Rendimiento estimado':<25} {clr(f'+${rendimiento:,.2f}', C.GREEN)}")
        print(f"  {'Estado de cuenta':<25} {clr(resultado['nuevo_estado'], C.YELLOW)}")
        print(f"  {'Folio de aprobacion':<25} {clr(resultado['folio_aprobacion'], C.CYAN)}")

        print()
        porcentaje = (capital / saldo) * 100
        barra_llena  = int(porcentaje / 5)
        barra_vacia  = 20 - barra_llena
        color_barra  = C.RED if porcentaje > 50 else C.GREEN
        barra = clr("█" * barra_llena, color_barra) + clr("░" * barra_vacia, C.GRAY)
        print(f"  Proporcion invertida: [{barra}] {clr(f'{porcentaje:.1f}%', color_barra)}")

    else:
        print(clr("  ✗ INVERSION RECHAZADA", C.BOLD + C.RED))
        print()
        if saldo < capital:
            print(f"  {clr('•', C.RED)} Saldo insuficiente: ${saldo:,.2f} < ${capital:,.2f}")
        if perfil == PERFIL_ALTO and meses_cuenta < 3:
            print(f"  {clr('•', C.RED)} Cuenta nueva ({meses_cuenta} mes(es)): no puede elegir alto riesgo")
        print(f"  {clr('Folio:', C.WHITE)} No generado")

    print()
    linea("─", 60, C.GRAY)
    pausar()

# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    while True:
        opcion = menu_principal()
        if opcion == "1":
            flujo_pago()
        elif opcion == "2":
            flujo_inversion()
        else:
            limpiar()
            print()
            print(clr("  Gracias por usar PayFlow. Hasta pronto.", C.PURPLE))
            print()
            break

if __name__ == "__main__":
    main()
