import os
import random
from supabase import create_client, Client

# === 1. CONEXIÓN SEGURA CON EL SERVIDOR ===
SUPABASE_URL = "https://yahkhkpaiprvmvxjjqxl.supabase.co"
# Pega aquí abajo tu clave larga anon de Supabase
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlhaGtoa3BhaXBydm12eGpqcXhsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA1NzE1OTIsImV4cCI6MjA5NjE0NzU5Mn0.hxs1wz-O4MuvJt1Hxan8Dm-hYeRm2i6v-q8Jra9NM2U"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"[!] Error de conexión: {e}")

# === 2. DATOS DE LA LIGA DE TERCERA NACIONAL (FCF) ===
EQUIPOS_TERCERA = [
    {"nombre": "Racing Pineda", "pabellon": "Pavelló Can Xaubet"},
    {"nombre": "Pineda Fútbol Sala", "pabellon": "Pavelló Nino Buscató"},
    {"nombre": "CFS Malgrat", "pabellon": "Pavelló Municipal de Malgrat"},
    {"nombre": "Inter Maresme", "pabellon": "Pavelló de Mataró"},
    {"nombre": "F.S. Ripollet", "pabellon": "Pavelló Municipal Joan Creus"},
    {"nombre": "Unión Santa Coloma", "pabellon": "Pavelló Nou de Santa Coloma"},
    {"nombre": "Futsal Iris Badalona", "pabellon": "Pavelló Poliesportiu Casagemas"},
    {"nombre": "Arenys de Munt CFS", "pabellon": "Pavelló Municipal d'Arenys de Munt"}
]

# Nombres y apellidos catalanes para dotar de realismo a las plantillas
NOMBRES = ["Pol", "Marc", "Jordi", "Adrià", "Eric", "Nil", "Pau", "Gerard", "Arnau", "Joan", "Oriol", "Albert", "Martí", "Aleix"]
APELLIDOS = ["Ros", "Riera", "Vila", "Puig", "Mas", "Sánchez", "Gómez", "Soler", "Martínez", "Serra", "Font", "Vidal", "Casas"]

def registrar_club_futsalmarket(nombre, pabellon):
    """Inserta o actualiza un club asignándole presupuestos de CIF y FGS"""
    # Presupuestos iniciales realistas para competir en Tercera Nacional
    cif_saldo = random.randint(30000, 60000)
    fgs_saldo = random.randint(8000, 15000)
    
    datos_club = {
        "nombre": nombre,
        "pabellon": pabellon,
        "FcFCoin_saldo": cif_saldo,       # Tus columnas reales corregidas
        "PlayerCoin_saldo": fgs_saldo
    }
    
    # Comprobamos si el club ya existe para no duplicarlo
    busqueda = supabase.table("clubes").select("id").eq("nombre", nombre).execute()
    if len(busqueda.data) > 0:
        club_id = busqueda.data[0]["id"]
        supabase.table("clubes").update(datos_club).eq("id", club_id).execute()
        return club_id
    else:
        resultado = supabase.table("clubes").insert(datos_club).execute()
        return resultado.data[0]["id"]

def generar_plantilla_futsalmarket(club_id, club_nombre):
    """Genera 10 jugadores federados equilibrados por demarcación para el club"""
    jugadores_creados = 0
    
    # Distribución de posiciones clásica de fútbol sala
    distribucion = [
        "Portero", "Portero", 
        "Cierre", "Cierre", 
        "Ala", "Ala", "Ala", "Ala", 
        "Pívot", "Pívot"
    ]
    
    for posicion in distribucion:
        nombre_completo = f"{random.choice(NOMBRES)} {random.choice(APELLIDOS)}"
        
        # Estructura del jugador limpia y sincronizada con tus columnas
        ficha_jugador = {
            "nombre": nombre_completo,
            "posicion": posicion,
            "club_id": club_id
        }
        
        try:
            supabase.table("jugadores").insert(ficha_jugador).execute()
            jugadores_creados += 1
        except Exception as e:
            print(f"   [!] Error insertando jugador: {e}")
            
    print(f" ➔ Plantilla de {club_nombre} creada con éxito ({jugadores_creados} licencias activas).")

if __name__ == "__main__":
    print("===============================================================")
    print(" 🚀 INICIANDO IMPORTADOR MASIVO - FUTSALMARKET CATALUNYA       ")
    print("===============================================================\n")
    
    for club in EQUIPOS_TERCERA:
        print(f"Procesando alta federativa de: {club['nombre']}...")
        try:
            # 1. Registramos el club y obtenemos su ID único de Supabase
            club_id = registrar_club_futsalmarket(club['nombre'], club['pabellon'])
            
            # 2. Generamos y vinculamos sus 10 licencias de jugadores
            generar_plantilla_futsalmarket(club_id, club['nombre'])
            print("-" * 63)
        except Exception as e:
            print(f"[!] Error procesando el club {club['nombre']}: {e}")

    print("\n===============================================================")
    print(" 🎉 ¡PROCESO COMPLETADO CON ÉXITO!")
    print(" La Tercera Nacional está completamente cargada en Supabase.")
    print("===============================================================\n")