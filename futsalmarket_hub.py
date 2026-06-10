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
    print(f"[!] Error al establecer conexión con el servidor central: {e}")
    sys.exit()

# Importamos los archivos del proyecto de forma limpia
try:
    import ver_plantilla
    import procesar_transferencia
    import scouting_mercado
except ImportError as e:
    print(f"[!] Error de estructura: Asegúrate de tener todos los archivos en la misma carpeta.")
    print(f"Falta el archivo: {e.name}.py")
    sys.exit()

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_cabecera():
    print("=================================================================")
    print("    💼    FUTSALMARKET CATALUNYA - PANEL DE CONTROL CENTRAL      ")
    print("              SISTEMA OFICIAL DE GESTIÓN Y AUDITORÍA             ")
    print("=================================================================")

def menu_principal():
    while True:
        limpiar_pantalla()
        mostrar_cabecera()
        print("  1. 📋 AUDITORÍA: Consultar Clubes, Pistas y Plantillas Activas")
        print("  2. 🔍 SCOUTING: Motor de Búsqueda y Filtro de Fichajes")
        print("  3. 📝 TRASPASOS: Ventanilla Oficial de Transferencia de Licencias")
        print("  4. 🚪 SALIR: Cerrar sesión segura de FutsalMarket")
        print("=================================================================")
        
        opcion = input("Selecciona un departamento (1-4): ").strip()
        
        if opcion == "1":
            try:
                # Ejecutamos de forma directa la interfaz que creamos en ver_plantilla.py
                ver_plantilla.mostrar_interfaz_auditoria()
            except Exception as e:
                print(f"[!] Error al cargar el departamento de auditoría: {e}")
                input("\nPresiona Enter para continuar...")
                
        elif opcion == "2":
            try:
                # Ejecutamos de forma directa el menú que creamos en scouting_mercado.py
                scouting_mercado.menu_scouting()
            except Exception as e:
                print(f"[!] Error al cargar el motor de scouting: {e}")
                input("\nPresiona Enter para continuar...")
                
        elif opcion == "3":
            try:
                # Ejecutamos de forma directa el flujo de procesar_transferencia.py
                procesar_transferencia.procesar_transferencia_licencia()
            except Exception as e:
                print(f"[!] Error al abrir la ventanilla de transferencias: {e}")
                input("\nPresiona Enter para continuar...")
                
        elif opcion == "4":
            limpiar_pantalla()
            print("=================================================================")
            print("         🔒 CONEXIÓN CERRADA CON ÉXITO Y CON SEGURIDAD")
            print("         Muchas gracias por utilizar FutsalMarket Catalunya.")
            print("=================================================================")
            break
        else:
            input("\n[!] Opción incorrecta. Presiona Enter para reintentar...")

if __name__ == "__main__":
    menu_principal()