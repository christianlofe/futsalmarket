import os
from supabase import create_client, Client

# === 1. TU CONEXIÓN SEGURA ===
SUPABASE_URL = "https://yahkhkpaiprvmvxjjqxl.supabase.co"
# Pega aquí abajo tu clave larga anon de Supabase
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlhaGtoa3BhaXBydm12eGpqcXhsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA1NzE1OTIsImV4cCI6MjA5NjE0NzU5Mn0.hxs1wz-O4MuvJt1Hxan8Dm-hYeRm2i6v-q8Jra9NM2U"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================================
# === 2. PANEL DE CONTROL DEL JUGADOR ===
# ==========================================================
NOMBRE_JUGADOR = "Pol Ros"
# ==========================================================

print(f"Enviando la ficha de {NOMBRE_JUGADOR} a la tabla 'jugadores' de Supabase...")

try:
    # Preparación de la ficha simplificada libre de errores de caché de columnas
    ficha_jugador = {
        "nombre": NOMBRE_JUGADOR
    }
    
    # Insertamos el registro en la tabla 'jugadores'
    respuesta = supabase.table("jugadores").insert(ficha_jugador).execute()
    
    print("\n=======================================================")
    print("¡FICHAJE COMPLETADO CON ÉXITO EN PARQUET!")
    print(f"Jugador: {NOMBRE_JUGADOR}")
    print("=======================================================\n")

except Exception as e:
    print("\n[!] Hubo un error al tramitar la ficha del jugador.")
    print("Detalle del error:", e)