import os
import sys
from supabase import create_client, Client

# === 1. CONEXIÓN SEGURA CON EL SERVIDOR ===
# FutsalMarket Catalunya - Servidor Oficial
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
    print("      💼 FUTSALMARKET CATALUNYA - DEPARTAMENTO DE TRANSFERENCIAS  ")
    print("=================================================================")

def procesar_transferencia_licencia():
    limpiar_pantalla()
    mostrar_cabecera()
    print("📝 INICIANDO TRÁMITE DE TRANSFERENCIA DE LICENCIA FEDERATIVA\n")
    
    try:
        # 1. Recuperar los clubes para el selector
        clubes = supabase.table("clubes").select("id, nombre, FcFCoin_saldo, PlayerCoin_saldo").execute().data
        if not clubes:
            print("[!] No hay clubes registrados en el sistema.")
            input("\nPresiona Enter para volver...")
            return

        # 2. Seleccionar Club Origen (Vendedor)
        print("Selecciona el CLUB ORIGEN (Poseedor de la licencia actual):")
        for idx, club in enumerate(clubes, 1):
            print(f"  {idx:2d}. {club['nombre']}")
        
        origen_idx = int(input("\nIntroduce el número del club de origen: ")) - 1
        if not (0 <= origen_idx < len(clubes)):
            print("[!] Selección incorrecta.")
            input("\nPresiona Enter para cancelar...")
            return
        club_origen = clubes[origen_idx]

        # 3. Buscar los jugadores con licencia en ese club
        jugadores = supabase.table("jugadores").select("id, nombre, posicion").eq("club_id", club_origen["id"]).execute().data
        if not jugadores:
            print(f"\n[!] El {club_origen['nombre']} no tiene licencias de jugadores activas para transferir.")
            input("\nPresiona Enter para cancelar...")
            return

        print(f"\nSelecciona el JUGADOR que se transferirá:")
        for idx, jug in enumerate(jugadores, 1):
            pos = jug.get('posicion', 'Sin asignar')
            print(f"  {idx:2d}. {jug['nombre']:<25} | Demarcación: {pos}")
            
        jug_idx = int(input("\nIntroduce el número del jugador: ")) - 1
        if not (0 <= jug_idx < len(jugadores)):
            print("[!] Selección incorrecta.")
            input("\nPresiona Enter para cancelar...")
            return
        jugador_a_transferir = jugadores[jug_idx]

        # 4. Seleccionar Club Destino (Comprador)
        print(f"\n¿A qué CLUB DESTINO se transferirá la licencia de {jugador_a_transferir['nombre']}?")
        clubes_compradores = [c for c in clubes if c["id"] != club_origen["id"]]
        for idx, club in enumerate(clubes_compradores, 1):
            print(f"  {idx:2d}. {club['nombre']} (Saldo CIF: {club.get('FcFCoin_saldo', 0):,} | FGS: {club.get('PlayerCoin_saldo', 0):,})")
            
        destino_idx = int(input("\nIntroduce el número del club destino: ")) - 1
        if not (0 <= destino_idx < len(clubes_compradores)):
            print("[!] Selección incorrecta.")
            input("\nPresiona Enter para cancelar...")
            return
        club_destino = clubes_compradores[destino_idx]

        # 5. Fijar importes de la operación
        print(f"\nEstablece los costes de la transferencia para {jugador_a_transferir['nombre']}:")
        coste_cif = int(input("  • Tasa de Transferencia de Derechos en CIF (🪙): "))
        coste_fgs = int(input("  • Fondo de Garantía Salarial para el Jugador en FGS (💎): "))

        # 6. Auditoría de Viabilidad Financiera (Control de Reglas Reales)
        saldo_cif_comprador = club_destino.get("FcFCoin_saldo", 0)
        saldo_fgs_comprador = club_destino.get("PlayerCoin_saldo", 0)

        if saldo_cif_comprador < coste_cif:
            print("\n❌ TRANSFERENCIA RECHAZADA POR LA FEDERACIÓN:")
            print(f"El club {club_destino['nombre']} no tiene suficientes Créditos de Inscripción (CIF).")
            print(f"  • Saldo actual: {saldo_cif_comprador:,} CIF | Requerido: {coste_cif:,} CIF")
            input("\nPresiona Enter para continuar...")
            return

        if saldo_fgs_comprador < coste_fgs:
            print("\n❌ TRANSFERENCIA RECHAZADA POR LA FEDERACIÓN:")
            print(f"El club {club_destino['nombre']} no dispone de suficiente aval en el Fondo de Garantía Salarial (FGS).")
            print(f"  • Saldo actual: {saldo_fgs_comprador:,} FGS | Requerido: {coste_fgs:,} FGS")
            input("\nPresiona Enter para continuar...")
            return

        print("\nTramitando la licencia en los servidores de FutsalMarket Catalunya...")

        # A) Descontar CIF y FGS al comprador
        nuevo_saldo_cif_comprador = saldo_cif_comprador - coste_cif
        nuevo_saldo_fgs_comprador = saldo_fgs_comprador - coste_fgs
        supabase.table("clubes").update({
            "FcFCoin_saldo": nuevo_saldo_cif_comprador,
            "PlayerCoin_saldo": nuevo_saldo_fgs_comprador
        }).eq("id", club_destino["id"]).execute()

        # B) Abonar CIF al vendedor (La tasa de transferencia de derechos)
        nuevo_saldo_cif_vendedor = club_origen.get("FcFCoin_saldo", 0) + coste_cif
        # (El FGS no se le da al club vendedor porque es el sueldo que se le avala al jugador en su nuevo club)
        supabase.table("clubes").update({
            "FcFCoin_saldo": nuevo_saldo_cif_vendedor
        }).eq("id", club_origen["id"]).execute()

        # C) Modificar la licencia del jugador (Cambiar club_id)
        supabase.table("jugadores").update({
            "club_id": club_destino["id"]
        }).eq("id", jugador_a_transferir["id"]).execute()

        print("\n=======================================================")
        print("🎉 ¡TRANSFERENCIA DE LICENCIA COMPLETADA CON ÉXITO!")
        print(f"  • Jugador: {jugador_a_transferir['nombre']} se une a {club_destino['nombre']}.")
        print(f"  • Derechos de formación (CIF) transferidos: {coste_cif:,} CIF.")
        print(f"  • Aval de nómina (FGS) garantizado: {coste_fgs:,} FGS.")
        print(f"  👉 Nuevo saldo {club_destino['nombre']}: {nuevo_saldo_cif_comprador:,} CIF | {nuevo_saldo_fgs_comprador:,} FGS")
        print(f"  👉 Nuevo saldo {club_origen['nombre']}: {nuevo_saldo_cif_vendedor:,} CIF")
        print("=======================================================\n")

    except ValueError:
        print("\n[!] Entrada incorrecta. Debes introducir valores numéricos enteros.")
    except Exception as e:
        print(f"\n[!] Error administrativo durante el trámite de la licencia: {e}")
        
    input("Presiona Enter para finalizar el trámite...")

if __name__ == "__main__":
    procesar_transferencia_licencia()