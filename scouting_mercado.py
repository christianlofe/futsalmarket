import os
import sys
from supabase import create_client, Client

# === 1. CONEXIÓN SEGURA CON EL SERVIDOR ===
SUPABASE_URL = "https://yahkhkpaiprvmvxjjqxl.supabase.co"
# Pega aquí abajo tu clave larga anon de Supabase
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlhaGtoa3BhaXBydm12eGpqcXhsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA1NzE1OTIsImV4cCI6MjA5NjE0NzU5Mn0.hxs1wz-O4MuvJt1Hxan8Dm-hYeRm2i6v-q8Jra9NM2U"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"[!] Error al establecer conexión con el servidor: {e}")
    sys.exit()

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_cabecera():
    print("=================================================================")
    print("    🔍 FUTSALMARKET CATALUNYA - MOTOR DE SCOUTING DE MERCADO     ")
    print("=================================================================")

def buscar_por_demarcacion():
    limpiar_pantalla()
    mostrar_cabecera()
    print("Selecciona la demarcación que necesita reforzar tu club:\n")
    print("  1. Portero")
    print("  2. Cierre")
    print("  3. Ala")
    print("  4. Pívot")
    print("-----------------------------------------------------------------")
    
    opciones = {"1": "Portero", "2": "Cierre", "3": "Ala", "4": "Pívot"}
    seleccion = input("Introduce una opción (1-4): ")
    
    posicion_buscada = opciones.get(seleccion)
    if not posicion_buscada:
        input("\n[!] Opción no válida. Presiona Enter para volver...")
        return

    limpiar_pantalla()
    mostrar_cabecera()
    print(f"📋 JUGADORES REGISTRADOS COMO '{posicion_buscada.upper()}' EN LA CATEGORÍA:\n")
    
    try:
        # Recuperamos jugadores de esa posición y los datos de sus clubes mediante una consulta combinada
        jugadores = supabase.table("jugadores").select("nombre, posicion, clubes(nombre)").eq("posicion", posicion_buscada).execute().data
        
        if not jugadores:
            print(f"No hay licencias activas en la posición de {posicion_buscada}.")
        else:
            print(f"  {'JUGADOR':<28} | {'POSICIÓN':<10} | {'CLUB ACTUAL':<25}")
            print("-" * 65)
            for j in jugadores:
                # Extraemos el nombre del club asociado de forma segura
                club_info = j.get("clubes", {})
                nombre_club = club_info.get("nombre", "Sin club asignado") if club_info else "Sin club"
                print(f"  {j['nombre']:<28} | {j['posicion']:<10} | {nombre_club:<25}")
                
    except Exception as e:
        print(f"[!] Error de consulta en el servidor de licencias: {e}")
        
    input("\nPresiona Enter para volver al panel de scouting...")

def buscar_por_nombre():
    limpiar_pantalla()
    mostrar_cabecera()
    print("🔍 BUSCADOR DE LICENCIAS POR NOMBRE")
    nombre_buscado = input("\nIntroduce el nombre (o apellido) del jugador: ").strip()
    
    if len(nombre_buscado) < 2:
        input("\n[!] Debes introducir al menos 2 caracteres para realizar la búsqueda. Enter para volver...")
        return
        
    limpiar_pantalla()
    mostrar_cabecera()
    print(f"🔎 RESULTADOS PARA: '{nombre_buscado.upper()}'\n")
    
    try:
        # Buscamos en Supabase usando un filtro 'ilike' (búsqueda parcial sin distinguir mayúsculas)
        jugadores = supabase.table("jugadores").select("nombre, posicion, clubes(nombre)").ilike("nombre", f"%{nombre_buscado}%").execute().data
        
        if not jugadores:
            print(f"No se ha encontrado ninguna licencia activa con el nombre '{nombre_buscado}'.")
        else:
            print(f"  {'JUGADOR':<28} | {'POSICIÓN':<10} | {'CLUB ACTUAL':<25}")
            print("-" * 65)
            for j in jugadores:
                club_info = j.get("clubes", {})
                nombre_club = club_info.get("nombre", "Sin club") if club_info else "Sin club"
                print(f"  {j['nombre']:<28} | {j['posicion']:<10} | {nombre_club:<25}")
                
    except Exception as e:
        print(f"[!] Error de conexión con el padrón de licencias: {e}")
        
    input("\nPresiona Enter para volver al panel de scouting...")

def ver_ranking_solvencia():
    limpiar_pantalla()
    mostrar_cabecera()
    print("🪙 CLASIFICACIÓN DE SOLVENCIA FINANCIERA (Tercera Nacional)\n")
    print("Ordenados de mayor a menor liquidez en Créditos de Inscripción (CIF).")
    print("Útil para saber qué clubes tienen mayor capacidad de compra de licencias.\n")
    
    try:
        clubes = supabase.table("clubes").select("nombre, pabellon, FcFCoin_saldo, PlayerCoin_saldo").execute().data
        # Ordenamos la lista en memoria por el saldo de CIF
        clubes_ordenados = sorted(clubes, key=lambda x: x.get("FcFCoin_saldo", 0), reverse=True)
        
        print(f"  {'#':<2} | {'CLUB':<25} | {'CRÉDITOS CIF':<15} | {'AVALES FGS':<15}")
        print("-" * 65)
        for idx, club in enumerate(clubes_ordenados, 1):
            print(f"  {idx:2d} | {club['nombre']:<25} | {club.get('FcFCoin_saldo', 0):,d} CIF     | {club.get('PlayerCoin_saldo', 0):,d} FGS")
            
    except Exception as e:
        print(f"[!] Error al cargar el balance de auditoría: {e}")
        
    input("\nPresiona Enter para volver...")

def menu_scouting():
    while True:
        limpiar_pantalla()
        mostrar_cabecera()
        print(" 1. Buscar Jugadores por Posición (Filtro Técnico)")
        print(" 2. Buscar Jugador por Nombre (Filtro Directo)")
        print(" 3. Ver Clasificación de Solvencia (Auditoría CIF/FGS)")
        print(" 4. Volver al Sistema Central")
        print("=================================================================")
        
        opcion = input("Introduce una opción (1-4): ").strip()
        if opcion == "1":
            buscar_por_demarcacion()
        elif opcion == "2":
            buscar_por_nombre()
        elif opcion == "3":
            ver_ranking_solvencia()
        elif opcion == "4":
            print("\nCerrando el motor de scouting. Conexión segura finalizada.")
            break
        else:
            input("\n[!] Opción incorrecta. Presiona Enter para reintentar...")

if __name__ == "__main__":
    menu_scouting()