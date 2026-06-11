import streamlit as st
import pandas as pd
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

st.set_page_config(page_title="FutsalMarket Catalunya", layout="wide", page_icon="⚽")

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

# --- LOGIN ---
def login():
    st.title("⚽ FutsalMarket Catalunya")
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.radio("Entrar como:", ["🏢 Club", "👤 Jugador"])
        email = st.text_input("Email")
        password = st.text_input("Contraseña", type="password")
        if st.button("Entrar", use_container_width=True):
            try:
                respuesta = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                usuario = respuesta.user
                perfil = supabase.table("perfiles").select("*").eq("id", usuario.id).execute().data
                if not perfil:
                    st.error("❌ No tienes perfil asignado. Contacta con la FCF.")
                    return
                perfil = perfil[0]
                st.session_state['usuario_id'] = usuario.id
                st.session_state['rol'] = perfil['rol']
                st.session_state['email'] = email
                st.session_state['logueado'] = True
                if perfil['rol'] == 'jugador':
                    jugador = supabase.table("jugadores").select("*").eq("email", email).execute().data
                    if jugador:
                        st.session_state['jugador_id'] = jugador[0]['id']
                        st.session_state['jugador_nombre'] = jugador[0]['nombre']
                        st.session_state['club_id'] = jugador[0]['club_id']
                else:
                    st.session_state['club_id'] = perfil['club_id']
                st.rerun()
            except Exception as e:
                st.error("❌ Email o contraseña incorrectos.")

# --- VERIFICAR SESIÓN ---
if 'logueado' not in st.session_state:
    st.session_state['logueado'] = False

if not st.session_state['logueado']:
    login()
    st.stop()

# --- PORTAL DEL JUGADOR ---
if st.session_state.get('rol') == 'jugador':
    jugador_nombre = st.session_state.get('jugador_nombre', 'Jugador')
    jugador_id = st.session_state.get('jugador_id')

    st.sidebar.title("⚽ FutsalMarket")
    st.sidebar.markdown(f"### 👤 {jugador_nombre}")
    st.sidebar.markdown(f"📧 {st.session_state['email']}")
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.title(f"👤 Portal de {jugador_nombre}")
    st.markdown("---")
    st.subheader("📥 Ofertas de Fichaje Recibidas")

    try:
        ofertas = supabase.table("ofertas_fichaje").select(
            "id, comprador_id, oferta_cif, oferta_fgs, estado"
        ).eq("jugador_id", jugador_id).eq("estado", "pendiente").execute().data

        for o in ofertas:
            club_comp = supabase.table("clubes").select("nombre").eq("id", o['comprador_id']).execute().data
            o['nombre_comprador'] = club_comp[0]['nombre'] if club_comp else "Desconocido"

        if not ofertas:
            st.info("No tienes ofertas de fichaje pendientes en este momento.")
        else:
            for o in ofertas:
                with st.container():
                    col_info, col_acciones = st.columns([3, 1])
                    with col_info:
                        st.subheader(f"Oferta de {o['nombre_comprador']}")
                        st.markdown(f"💰 **Derechos al club:** `{o['oferta_cif']:,} CIF`")
                        st.markdown(f"💎 **Tu salario garantizado:** `{o['oferta_fgs']:,} FGS`")
                    with col_acciones:
                        st.markdown("<br>", unsafe_allow_html=True)
                        col_si, col_no = st.columns(2)
                        if col_si.button("✅", key=f"jug_acp_{o['id']}", use_container_width=True):
                            supabase.table("ofertas_fichaje").update({"estado": "aceptada_jugador"}).eq("id", o['id']).execute()
                            st.success("🎉 ¡Has aceptado la oferta! El club será notificado.")
                            st.balloons()
                            st.rerun()
                        if col_no.button("❌", key=f"jug_rch_{o['id']}", use_container_width=True):
                            supabase.table("ofertas_fichaje").update({"estado": "rechazada"}).eq("id", o['id']).execute()
                            st.warning("Has rechazado la oferta.")
                            st.rerun()
                st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error cargando ofertas: {e}")
    st.stop()

# --- APP PRINCIPAL PARA CLUBS ---
club_id = st.session_state['club_id']
club_data = supabase.table("clubes").select("*").eq("id", club_id).execute().data

if not club_data:
    st.error("No se encontró tu club. Contacta con la FCF.")
    st.stop()

club_activo = club_data[0]
club_activo_nombre = club_activo['nombre']
clubes_lista = supabase.table("clubes").select("id, nombre").execute().data
nombres_clubes = {c['nombre']: c for c in clubes_lista}

# --- BARRA LATERAL ---
st.sidebar.title("⚽ FutsalMarket")
st.sidebar.subheader("Catalunya Edition")
st.sidebar.markdown("---")
st.sidebar.markdown(f"### 🏢 {club_activo_nombre}")
st.sidebar.markdown(f"👤 {st.session_state['email']}")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Menú de Operaciones",
    ["📈 Panel de Control", "🔍 Scouting & Estadísticas", "📝 Ventanilla de Traspasos", "📥 Buzón de Ofertas"]
)

if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
    st.session_state.clear()
    st.rerun()

# --- PANEL DE CONTROL ---
if menu == "📈 Panel de Control":
    st.title("📈 Centro de Mando")
    st.markdown(f"Bienvenido, **{club_activo_nombre}**")
    st.markdown("---")
    try:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Créditos de Fichaje (CIF)", value=f"{club_activo['FcFCoin_saldo']:,} 🪙")
        with col2:
            st.metric(label="Fondo Salarial (FGS)", value=f"{club_activo['PlayerCoin_saldo']:,} 💎")
        with col3:
            jugadores_count = supabase.table("jugadores").select("id").eq("club_id", club_id).execute().data
            st.metric(label="Jugadores en Plantilla", value=len(jugadores_count))
        st.markdown("---")
        st.markdown("### 📋 Tu Plantilla")
        plantilla = supabase.table("jugadores").select("*").eq("club_id", club_id).execute().data
        if plantilla:
            df = pd.DataFrame(plantilla)
            columnas = ['nombre', 'posicion']
            if 'goles' in df.columns:
                columnas.append('goles')
            if 'partidos_jugados' in df.columns:
                columnas.append('partidos_jugados')
            st.dataframe(df[columnas], use_container_width=True)
        else:
            st.info("No tienes jugadores registrados en tu plantilla.")
    except Exception as e:
        st.error(f"Error cargando el panel: {e}")

# --- SCOUTING ---
elif menu == "🔍 Scouting & Estadísticas":
    st.title("🔍 Scouting & Estadísticas")
    st.markdown("---")
    try:
        filtro_club = st.selectbox("Filtrar por Club", ["Todos los Clubes"] + list(nombres_clubes.keys()))
        query = supabase.table("jugadores").select("*")
        if filtro_club != "Todos los Clubes":
            query = query.eq("club_id", nombres_clubes[filtro_club]['id'])
        jugadores = query.execute().data
        if jugadores:
            for j in jugadores:
                posicion = j.get("posicion", "Ala")
                goles = j.get("goles", hash(j['nombre']) % 18 + 2)
                asistencias = j.get("asistencias", hash(j['nombre']) % 12 + 1)
                partidos = j.get("partidos_jugados", hash(j['nombre']) % 10 + 12)
                amarillas = j.get("tarjetas_amarillas", hash(j['nombre']) % 4)
                rojas = j.get("tarjetas_rojas", 1 if (hash(j['nombre']) % 15 == 0) else 0)
                valor = j.get("valor_mercado", (goles * 200) + (asistencias * 150) + 1000)
                with st.container():
                    col_foto, col_info, col_stats = st.columns([1, 2, 4])
                    with col_foto:
                        if posicion.lower() in ["portero", "goalkeeper"]:
                            st.markdown("<h1 style='text-align: center; font-size: 50px;'>🧤</h1>", unsafe_allow_html=True)
                        else:
                            st.markdown("<h1 style='text-align: center; font-size: 50px;'>🏃‍♂️</h1>", unsafe_allow_html=True)
                        st.markdown(f"<p style='text-align: center; font-weight: bold;'>{posicion.upper()}</p>", unsafe_allow_html=True)
                    with col_info:
                        st.subheader(j['nombre'])
                        club_pertenece = next((name for name, c in nombres_clubes.items() if c['id'] == j['club_id']), "Sin Club")
                        st.markdown(f"**Club:** {club_pertenece}")
                        st.markdown(f"💰 **Valor:** `{valor:,} CIF`")
                    with col_stats:
                        st.markdown("**Estadísticas de Temporada:**")
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("Partidos", partidos)
                        c2.metric("Goles ⚽", goles)
                        c3.metric("Asistencias", asistencias)
                        c4.metric("Tarjetas 🟨/🟥", f"{amarillas}/{rojas}")
                st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        else:
            st.info("No hay jugadores registrados.")
    except Exception as e:
        st.error(f"Error cargando scouting: {e}")

# --- VENTANILLA DE TRASPASOS ---
elif menu == "📝 Ventanilla de Traspasos":
    st.title("📝 Ventanilla de Ofertas Oficiales")
    st.markdown(f"Club Comprador: **{club_activo_nombre}**")
    st.markdown("---")
    try:
        otros_clubs = [c for c in nombres_clubes.keys() if c != club_activo_nombre]
        club_vendedor_nombre = st.selectbox("Club Vendedor", otros_clubs)
        vendedor = nombres_clubes[club_vendedor_nombre]
        jugadores = supabase.table("jugadores").select("id, nombre").eq("club_id", vendedor['id']).execute().data
        if jugadores:
            jugador_sel = st.selectbox("Selecciona Jugador", [j['nombre'] for j in jugadores])
            jugador_id = next(j['id'] for j in jugadores if j['nombre'] == jugador_sel)
            col1, col2 = st.columns(2)
            with col1:
                precio_cif = st.number_input("Derechos de Transferencia al Club (CIF 🪙)", min_value=0, value=2000, step=500)
            with col2:
                salario_fgs = st.number_input("Garantía Salarial al Jugador (FGS 💎)", min_value=0, value=800, step=100)
            st.markdown("---")
            st.info(f"**Resumen:** Oferta al **{club_vendedor_nombre}** por **{jugador_sel}** · {precio_cif:,} CIF al club + {salario_fgs:,} FGS al jugador.")
            if st.button("Enviar Propuesta de Fichaje", use_container_width=True):
                club_comprador_full = supabase.table("clubes").select("*").eq("id", club_activo['id']).execute().data[0]
                if club_comprador_full['FcFCoin_saldo'] < precio_cif:
                    st.error("❌ No tienes suficientes CIF para esta oferta.")
                elif club_comprador_full['PlayerCoin_saldo'] < salario_fgs:
                    st.error("❌ No tienes suficiente FGS para avalar el sueldo.")
                else:
                    supabase.table("ofertas_fichaje").insert({
                        "jugador_id": jugador_id,
                        "vendedor_id": vendedor['id'],
                        "comprador_id": club_activo['id'],
                        "oferta_cif": precio_cif,
                        "oferta_fgs": salario_fgs,
                        "estado": "pendiente"
                    }).execute()
                    st.success(f"📩 Propuesta enviada a {club_vendedor_nombre}. Pendiente de respuesta.")
        else:
            st.warning("Este club no tiene jugadores registrados.")
    except Exception as e:
        st.error(f"Error al tramitar la oferta: {e}")

# --- BUZÓN DE OFERTAS ---
elif menu == "📥 Buzón de Ofertas":
    st.title("📥 Buzón de Ofertas Oficiales")
    st.markdown(f"Club Actual: **{club_activo_nombre}**")
    st.markdown("---")
    try:
        ofertas = supabase.table("ofertas_fichaje").select(
            "id, jugador_id, jugadores(nombre), comprador_id, oferta_cif, oferta_fgs, estado"
        ).eq("vendedor_id", club_activo['id']).eq("estado", "aceptada_jugador").execute().data

        for o in ofertas:
            club_comp = supabase.table("clubes").select("nombre").eq("id", o['comprador_id']).execute().data
            o['nombre_comprador'] = club_comp[0]['nombre'] if club_comp else "Desconocido"

        if not ofertas:
            st.info("No tienes propuestas pendientes en este momento.")
        else:
            for o in ofertas:
                jugador_nombre = o['jugadores']['nombre']
                club_comprador = o['nombre_comprador']
                cif_ofrecido = o['oferta_cif']
                fgs_ofrecido = o['oferta_fgs']
                with st.container():
                    col_detalles, col_acciones = st.columns([3, 1])
                    with col_detalles:
                        st.subheader(f"Oferta por {jugador_nombre}")
                        st.markdown(f"🏢 **Club Interesado:** {club_comprador}")
                        st.markdown(f"💰 **Derechos:** `{cif_ofrecido:,} CIF` | 💎 **Sueldo:** `{fgs_ofrecido:,} FGS`")
                        st.success("✅ Jugador ha aceptado — pendiente confirmación del club")
                    with col_acciones:
                        st.markdown("<br>", unsafe_allow_html=True)
                        col_si, col_no = st.columns(2)
                        if col_si.button("✅", key=f"acp_{o['id']}", use_container_width=True):
                            vendedor_full = supabase.table("clubes").select("*").eq("id", club_activo['id']).execute().data[0]
                            comprador_full = supabase.table("clubes").select("*").eq("id", o['comprador_id']).execute().data[0]
                            if comprador_full['FcFCoin_saldo'] >= cif_ofrecido and comprador_full['PlayerCoin_saldo'] >= fgs_ofrecido:
                                supabase.table("clubes").update({
                                    "FcFCoin_saldo": comprador_full['FcFCoin_saldo'] - cif_ofrecido,
                                    "PlayerCoin_saldo": comprador_full['PlayerCoin_saldo'] - fgs_ofrecido
                                }).eq("id", comprador_full['id']).execute()
                                supabase.table("clubes").update({
                                    "FcFCoin_saldo": vendedor_full['FcFCoin_saldo'] + cif_ofrecido
                                }).eq("id", vendedor_full['id']).execute()
                                supabase.table("jugadores").update({"club_id": comprador_full['id']}).eq("id", o['jugador_id']).execute()
                                supabase.table("ofertas_fichaje").update({"estado": "completada"}).eq("id", o['id']).execute()
                                st.success(f"🎉 ¡Fichaje completado! {jugador_nombre} se incorpora a {club_comprador}.")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ El club comprador ya no tiene fondos suficientes.")
                        if col_no.button("❌", key=f"rch_{o['id']}", use_container_width=True):
                            supabase.table("ofertas_fichaje").update({"estado": "rechazada"}).eq("id", o['id']).execute()
                            st.warning("Propuesta declinada.")
                            st.rerun()
                st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error al cargar el buzón: {e}")

st.sidebar.markdown("---")
st.sidebar.caption("FutsalMarket Catalunya v2.0")