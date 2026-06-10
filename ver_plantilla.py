import os
import sys
from supabase import create_client, Client

# === 1. CONEXIÓN SEGURA ===
SUPABASE_URL = "https://yahkhkpaiprvmvxjjqxl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlhaGtoa3BhaXBydm12eGpqcXhsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA1NzE1OTIsImV4cCI6MjA5NjE0NzU5Mn0.hxs1wz-O4MuvJt1Hxan8Dm-hYeRm2i6v-q8Jra9NM2U" # <--- ¡Asegúrate de poner tu clave aquí!

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"[!] Error de conexión: {e}")

def mostrar_interfaz_auditoria():
    """Esta es la función que llama el Hub Central"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=================================================================")
    print("    ⚽ FUTSALMARKET CATALUNYA - AUDITORÍA Y CONTROL OFICIAL      ")
    print("=================================================================")
    
    try:
        # Recuperamos clubes
        respuesta = supabase.table("clubes").select("id, nombre, pabellon, FcFCoin_saldo, PlayerCoin_saldo").execute()
        clubes = respuesta.data
        
        if not clubes:
            print("\n[!] No hay clubes registrados.")
            input("Pulsa Enter para volver...")
            return

        print("\nSelecciona el club que deseas auditar:")
        for idx, club in enumerate(clubes, 1):
            print(f"  {idx:2d}. {club['nombre']}")
        print("  0. Volver al Menú Principal")
        
        opcion = int(input("\nSelecciona una opción: "))
        
        if opcion == 0:
            return
        
        if 1 <= opcion <= len(clubes):
            club = clubes[opcion - 1]
            # Recuperamos jugadores
            jugadores_res = supabase.table("jugadores").select("nombre, posicion").eq("club_id", club['id']).execute()
            plantilla = jugadores_res.data
            
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"FICHA DE: {club['nombre'].upper()}")
            print(f"Sede: {club['pabellon']}")
            print(f"Fondos: {club['FcFCoin_saldo']:,} CIF | {club['PlayerCoin_saldo']:,} FGS")
            print("-" * 40)
            for j in plantilla:
                print(f" - {j['nombre']} ({j['posicion']})")
            input("\nPulsa Enter para volver...")
            mostrar_interfaz_auditoria() # Llamada recursiva para no salir del módulo
            
    except Exception as e:
        print(f"\n[!] Error en el módulo de auditoría: {e}")
        input("Pulsa Enter para volver...")

if __name__ == "__main__":
    mostrar_interfaz_auditoria()