# main.py
# PayFlow MVP — Interfaz de consola con login
# Equipo: Gris | Taller de Pruebas | UV FEI LIS 2026

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from payflow_pago import procesar_pago, CONCEPTOS_VALIDOS, COMISION_FIJA
from inversiones import autorizar_inversion, PERFIL_BAJO, PERFIL_ALTO, ESTADO_RECHAZADA
from usuarios import login, actualizar_usuario, registrar_operacion, obtener_historial

class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    PURPLE = "\033[95m"
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    GRAY   = "\033[90m"
    WHITE  = "\033[97m"

def clr(text, color):
    return f"{color}{text}{C.RESET}"

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

def pantalla_login():
    banner()
    print(clr("  INICIAR SESION", C.BOLD + C.WHITE))
    print()
    print(clr("  Usuarios demo disponibles:", C.GRAY))
    print(clr("    USR-001 / payflow123   (saldo $10,000 | 12 meses)", C.GRAY))
    print(clr("    USR-002 / gris2026     (saldo $5,000  |  2 meses — cuenta nueva)", C.GRAY))
    print(clr("    USR-003 / taller99     (saldo $25,000 | 24 meses)", C.GRAY))
    print()
    linea("─", 60, C.GRAY)
    intentos = 3
    while intentos > 0:
        print()
        id_usuario = input(clr("  ID de usuario: ", C.CYAN)).strip()
        password   = input(clr("  Contrasena:    ", C.CYAN)).strip()
        usuario    = login(id_usuario, password)
        if usuario:
            print()
            print(clr(f"  Bienvenido, {usuario['nombre']}!", C.BOLD + C.GREEN))
            pausar()
            return usuario
        intentos -= 1
        if intentos > 0:
            print(clr(f"  Credenciales incorrectas. Intentos restantes: {intentos}", C.RED))
        else:
            print(clr("  Demasiados intentos fallidos. Cerrando...", C.RED))
    return None

def menu_principal(usuario):
    limpiar()
    linea("═", 60, C.PURPLE)
    print(clr("  PAYFLOW — MENU PRINCIPAL", C.BOLD + C.PURPLE))
    linea("═", 60, C.PURPLE)
    print()
    estado_color = C.GREEN if usuario["estado_cuenta"] == "DISPONIBLE" else C.YELLOW
    print(clr("  CUENTA", C.BOLD + C.WHITE))
    print(f"  {'Usuario':<18} {usuario['id_usuario']}  —  {usuario['nombre']}")
    saldo_fmt = clr(f'${usuario["saldo"]:,.2f}', C.GREEN)
    print(f"  {'Saldo disponible':<18} {saldo_fmt}")
    print(f"  {'Antiguedad':<18} {usuario['meses_cuenta']} meses")
    print(f"  {'Estado':<18} {clr(usuario['estado_cuenta'], estado_color)}")
    print()
    linea("─", 60, C.GRAY)
    print()
    print(clr("  1.", C.YELLOW) + "  Pago de Servicio Fijo")
    print(clr("     ", C.GRAY) + clr("Renta / Internet / Luz", C.GRAY))
    print()
    print(clr("  2.", C.YELLOW) + "  Inversion de Capital")
    print(clr("     ", C.GRAY) + clr("Bajo riesgo / Alto riesgo", C.GRAY))
    print()
    print(clr("  3.", C.CYAN) + "  Ver historial de operaciones")
    print()
    print(clr("  4.", C.RED) + "  Cerrar sesion")
    print()
    linea("─", 60, C.GRAY)
    return pedir_opcion("Selecciona una opcion (1/2/3/4)", ["1", "2", "3", "4"])

def flujo_pago(usuario):
    titulo("PAGO DE SERVICIO FIJO", C.CYAN)
    print(clr("  Conceptos disponibles:", C.WHITE))
    for c in sorted(CONCEPTOS_VALIDOS):
        comision = 0.00 if c == "Internet" else COMISION_FIJA
        tag = clr("(sin comision)", C.GREEN) if comision == 0 else clr(f"(+ ${comision:.2f} comision)", C.YELLOW)
        print(f"    {clr('•', C.CYAN)} {c} {tag}")
    print()
    saldo_fmt = clr(f'${usuario["saldo"]:,.2f}', C.GREEN)
    print(f"  {clr('Saldo disponible:', C.WHITE)} {saldo_fmt}")
    print()
    concepto = input(clr("  Concepto (Renta / Internet / Luz): ", C.CYAN)).strip().capitalize()
    if concepto not in CONCEPTOS_VALIDOS:
        print(clr(f"  Concepto '{concepto}' no valido.", C.RED))
        pausar()
        return
    monto = pedir_float("Monto a pagar ($)")
    print()
    linea("─", 60, C.GRAY)
    print(clr("  Procesando pago...", C.YELLOW))
    linea("─", 60, C.GRAY)
    resultado = procesar_pago(usuario["id_usuario"], concepto, monto, usuario["saldo"])
    print()
    if resultado["estado"] == "APROBADO":
        print(clr("  PAGO APROBADO", C.BOLD + C.GREEN))
        print()
        comision_aplicada = usuario["saldo"] - resultado["nuevo_saldo"] - monto
        print(f"  {'Concepto':<22} {concepto}")
        print(f"  {'Monto pagado':<22} ${monto:,.2f}")
        print(f"  {'Comision aplicada':<22} ${comision_aplicada:,.2f}")
        print(f"  {'Saldo anterior':<22} ${usuario['saldo']:,.2f}")
        saldo_nuevo_fmt = clr(f'${resultado["nuevo_saldo"]:,.2f}', C.GREEN)
        print(f"  {'Saldo nuevo':<22} {saldo_nuevo_fmt}")
        print(f"  {'Folio':<22} {clr(resultado['folio'], C.CYAN)}")
        actualizar_usuario(usuario["id_usuario"], resultado["nuevo_saldo"], usuario["estado_cuenta"])
        registrar_operacion(usuario["id_usuario"], "PAGO", concepto, monto, resultado["folio"], "APROBADO")
        usuario["saldo"] = resultado["nuevo_saldo"]
    else:
        print(clr("  PAGO RECHAZADO", C.BOLD + C.RED))
        print()
        print(f"  {clr('Motivo:', C.YELLOW)} {resultado['motivo']}")
        registrar_operacion(usuario["id_usuario"], "PAGO", concepto, monto, None, "RECHAZADO")
    print()
    linea("─", 60, C.GRAY)
    pausar()

def flujo_inversion(usuario):
    titulo("INVERSION DE CAPITAL", C.PURPLE)
    print(clr("  Perfiles disponibles:", C.WHITE))
    print(f"    {clr('•', C.CYAN)} bajo_riesgo  {clr('(tasa 5% anual)', C.GRAY)}")
    print(f"    {clr('•', C.CYAN)} alto_riesgo  {clr('(tasa 12% anual — requiere cuenta >= 3 meses)', C.GRAY)}")
    print()
    saldo_fmt = clr(f'${usuario["saldo"]:,.2f}', C.GREEN)
    print(f"  {clr('Saldo disponible:', C.WHITE)} {saldo_fmt}")
    print(f"  {clr('Antiguedad de cuenta:', C.WHITE)} {usuario['meses_cuenta']} meses")
    print()
    capital = pedir_float("Capital a invertir ($)")
    perfil  = pedir_opcion("Perfil de inversion (bajo_riesgo / alto_riesgo)", [PERFIL_BAJO, PERFIL_ALTO])
    plazo   = pedir_int("Plazo de inversion (meses, minimo 12)", minimo=12)
    print()
    linea("─", 60, C.GRAY)
    print(clr("  Procesando inversion...", C.YELLOW))
    linea("─", 60, C.GRAY)
    try:
        resultado = autorizar_inversion(capital, usuario["saldo"], perfil, usuario["meses_cuenta"], plazo)
    except ValueError as e:
        print()
        print(clr(f"  PARAMETROS INVALIDOS: {e}", C.BOLD + C.RED))
        pausar()
        return
    print()
    if resultado["estado"] == "AUTORIZADA":
        tasa        = 0.12 if perfil == PERFIL_BAJO.__class__ and perfil == "alto_riesgo" else (0.12 if perfil == "alto_riesgo" else 0.05)
        rendimiento = resultado["monto_final"] - capital
        print(clr("  INVERSION AUTORIZADA", C.BOLD + C.GREEN))
        print()
        print(f"  {'Capital invertido':<25} ${capital:,.2f}")
        print(f"  {'Perfil':<25} {perfil}  {clr(f'(tasa {tasa*100:.0f}%)', C.GRAY)}")
        print(f"  {'Plazo':<25} {plazo} meses")
        monto_fmt = clr(f'${resultado["monto_final"]:,.2f}', C.GREEN)
        print(f"  {'Monto final estimado':<25} {monto_fmt}")
        rend_fmt  = clr(f'+${rendimiento:,.2f}', C.GREEN)
        print(f"  {'Rendimiento estimado':<25} {rend_fmt}")
        print(f"  {'Nuevo estado cuenta':<25} {clr(resultado['nuevo_estado'], C.YELLOW)}")
        print(f"  {'Folio de aprobacion':<25} {clr(resultado['folio_aprobacion'], C.CYAN)}")
        print()
        porcentaje  = (capital / usuario["saldo"]) * 100
        barra_llena = min(int(porcentaje / 5), 20)
        barra_vacia = 20 - barra_llena
        color_barra = C.RED if porcentaje > 50 else C.GREEN
        barra = clr("█" * barra_llena, color_barra) + clr("░" * barra_vacia, C.GRAY)
        print(f"  Proporcion invertida: [{barra}] {clr(f'{porcentaje:.1f}%', color_barra)}")
        actualizar_usuario(usuario["id_usuario"], usuario["saldo"], resultado["nuevo_estado"])
        registrar_operacion(usuario["id_usuario"], "INVERSION", perfil, capital, resultado["folio_aprobacion"], "AUTORIZADA")
        usuario["estado_cuenta"] = resultado["nuevo_estado"]
    else:
        print(clr("  INVERSION RECHAZADA", C.BOLD + C.RED))
        print()
        if usuario["saldo"] < capital:
            print(f"  {clr('•', C.RED)} Saldo insuficiente: ${usuario['saldo']:,.2f} < ${capital:,.2f}")
        if perfil == "alto_riesgo" and usuario["meses_cuenta"] < 3:
            print(f"  {clr('•', C.RED)} Cuenta nueva ({usuario['meses_cuenta']} mes(es)): no puede elegir alto riesgo")
        registrar_operacion(usuario["id_usuario"], "INVERSION", perfil, capital, None, "RECHAZADA")
    print()
    linea("─", 60, C.GRAY)
    pausar()

def flujo_historial(usuario):
    titulo("HISTORIAL DE OPERACIONES", C.CYAN)
    operaciones = obtener_historial(usuario["id_usuario"])
    if not operaciones:
        print(clr("  No hay operaciones registradas aun.", C.GRAY))
        pausar()
        return
    print(f"  {clr('Usuario:', C.WHITE)} {usuario['nombre']}  ({len(operaciones)} operacion(es))")
    print()
    print(clr(f"  {'#':<4} {'Fecha':<20} {'Tipo':<12} {'Concepto':<15} {'Monto':>10}  {'Resultado'}", C.BOLD + C.WHITE))
    linea("─", 75, C.GRAY)
    for i, op in enumerate(operaciones, 1):
        color_res = C.GREEN if op["resultado"] in ("APROBADO", "AUTORIZADA") else C.RED
        print(
            f"  {i:<4} {op['fecha']:<20} "
            f"{clr(op['tipo'], C.CYAN):<20} "
            f"{op['concepto']:<15} "
            f"${float(op['monto']):>10,.2f}  "
            f"{clr(op['resultado'], color_res)}"
        )
    print()
    linea("─", 75, C.GRAY)
    pausar()

def main():
    usuario = pantalla_login()
    if not usuario:
        sys.exit(0)
    while True:
        opcion = menu_principal(usuario)
        if opcion == "1":
            flujo_pago(usuario)
        elif opcion == "2":
            flujo_inversion(usuario)
        elif opcion == "3":
            flujo_historial(usuario)
        else:
            limpiar()
            print()
            print(clr(f"  Hasta pronto, {usuario['nombre']}.", C.PURPLE))
            print()
            break

if __name__ == "__main__":
    main()
