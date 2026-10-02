import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timezone, timedelta
import urllib.parse
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Treino",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- FUSO HORÁRIO E DATA ---
FUSO = timezone(timedelta(hours=-3))
agora_br = datetime.now(FUSO)

DIAS_SEMANA_MAP = {
    0: "Treino - Segunda-feira",
    1: "Treino - Terça-feira",
    2: "Treino - Quarta-feira",
    3: "Treino - Quinta-feira",
    4: "Treino - Sexta-feira",
    5: "Treino - Sábado",
    6: "Treino - Domingo"
}

dia_semana_nome = DIAS_SEMANA_MAP.get(agora_br.weekday(), "Treino - Segunda-feira")

# --- CSS CLEAN LIGHT THEME ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        background-color: #f8fafc !important;
        color: #0f172a !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    #MainMenu, footer {visibility: hidden;}
    header {background: transparent !important;}

    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 5rem !important;
        max-width: 620px !important;
    }

    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p {
        color: #0f172a !important;
    }

    .hevy-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 14px;
        margin-bottom: 18px;
        border-bottom: 1px solid #e2e8f0;
    }
    .hevy-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .hevy-subtitle {
        font-size: 0.84rem;
        color: #64748b;
        font-weight: 500;
        margin-top: 2px;
    }

    .exercise-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }
    .exercise-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0f172a;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 4px;
    }
    .video-link {
        font-size: 0.76rem;
        color: #2563eb;
        text-decoration: none;
        background: #eff6ff;
        padding: 4px 10px;
        border-radius: 8px;
        border: 1px solid #bfdbfe;
        font-weight: 600;
        transition: all 0.15s ease;
    }
    .video-link:hover {
        background: #dbeafe;
        color: #1d4ed8;
    }

    .table-header {
        display: grid;
        grid-template-columns: 36px 1fr 65px 65px 38px;
        gap: 6px;
        font-size: 0.72rem;
        font-weight: 700;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 8px 0;
        text-align: center;
        border-bottom: 1px solid #f1f5f9;
        margin-bottom: 8px;
    }

    .set-badge {
        background: #f1f5f9;
        color: #475569;
        font-size: 0.82rem;
        font-weight: 700;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 38px;
    }

    div[data-testid="column"] input {
        background-color: #f8fafc !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        color: #0f172a !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        text-align: center !important;
        height: 38px !important;
        padding: 0 !important;
    }
    div[data-testid="column"] input:focus {
        background-color: #ffffff !important;
        border-color: #10b981 !important;
        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2) !important;
    }
    div[data-testid="column"] label {
        display: none !important;
    }

    /* Botão de descanso na linha */
    div[data-testid="column"] button {
        background-color: #f1f5f9 !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        color: #334155 !important;
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        height: 38px !important;
        padding: 0 4px !important;
        width: 100% !important;
    }
    div[data-testid="column"] button:hover {
        background-color: #e2e8f0 !important;
        border-color: #94a3b8 !important;
        color: #0f172a !important;
    }

    div[data-testid="stCheckbox"] {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 38px;
    }

    button[kind="primary"] {
        background: #10b981 !important;
        border: none !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        min-height: 48px !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
        cursor: pointer !important;
    }
    button[kind="primary"]:hover {
        background: #059669 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- BANCO DE DADOS ---
DB_PATH = "/home/ubuntu/treino/treino.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS registro_treino (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            data TEXT,
            ficha TEXT,
            exercicio TEXT,
            serie_num INTEGER,
            carga REAL,
            repeticoes INTEGER,
            concluido INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

USUARIO = "andre"

# --- FICHAS ---
FICHAS = {
    "Treino - Segunda-feira": [
        ("Agachamento Livre", 4, "8-10"),
        ("Leg Press 45", 3, "10-12"),
        ("Cadeira Extensora", 3, "12-15"),
        ("Puxada Frontal", 4, "10-12"),
        ("Remada Curvada", 3, "8-10"),
        ("Rosca Direta", 3, "10-12"),
        ("Panturrilha em Pé", 4, "15-20"),
    ],
    "Treino - Terça-feira": [
        ("Supino Reto Barra", 4, "8-10"),
        ("Supino Inclinado Halteres", 3, "10-12"),
        ("Crucifixo Máquina", 3, "12-15"),
        ("Desenvolvimento Halteres", 3, "10-12"),
        ("Elevação Lateral", 4, "12-15"),
        ("Tríceps Corda", 3, "12-15"),
        ("Tríceps Testa", 3, "10-12"),
    ],
    "Treino - Quinta-feira": [
        ("Stiff / RDL", 4, "8-10"),
        ("Mesa Flexora", 3, "10-12"),
        ("Elevação Pélvica", 3, "10-12"),
        ("Remada Baixa", 4, "10-12"),
        ("Crucifixo Invertido", 3, "12-15"),
        ("Rosca Martelo", 3, "10-12"),
        ("Abdominal Supra", 4, "15-20"),
    ],
    "Treino - Sexta-feira": [
        ("Desenvolvimento Militar", 4, "8-10"),
        ("Elevação Lateral Cabo", 4, "12-15"),
        ("Supino Fechado", 3, "10-12"),
        ("Paralelas / Máquina", 3, "10-12"),
        ("Rosca Scott", 3, "10-12"),
        ("Rosca Alternada", 3, "10-12"),
        ("Prancha", 3, "45-60s"),
    ]
}

lista_fichas = list(FICHAS.keys())
idx_padrao = lista_fichas.index(dia_semana_nome) if dia_semana_nome in lista_fichas else 0

# --- BARRA LATERAL ---
ficha_sel = st.sidebar.selectbox("Ficha Ativa", lista_fichas, index=idx_padrao)
data_sel = st.sidebar.date_input("Data", value=agora_br.date()).strftime("%Y-%m-%d")

# --- CONTADOR DE DESCANSO ATIVO ---
if "rest_target" in st.session_state:
    restante = int(st.session_state["rest_target"] - time.time())
    if restante > 0:
        st.info(f"⏳ **Descanso em curso:** `{restante}s` restantes...")
        time.sleep(1)
        st.rerun()
    else:
        st.success("🔔 **Descanso concluído!** Próxima série!")
        del st.session_state["rest_target"]

# --- CABEÇALHO ---
dia_semana_abrev = agora_br.strftime('%A')
DIAS_PT = {
    'Monday': 'Segunda-feira', 'Tuesday': 'Terça-feira', 'Wednesday': 'Quarta-feira',
    'Thursday': 'Quinta-feira', 'Friday': 'Sexta-feira', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
}
dia_nome_pt = DIAS_PT.get(dia_semana_abrev, dia_semana_abrev)

st.markdown(f"""
<div class="hevy-header">
    <div>
        <h1 class="hevy-title">{ficha_sel}</h1>
        <p class="hevy-subtitle">{dia_nome_pt} &bull; {agora_br.strftime('%d/%m/%Y')}</p>
    </div>
    <span style="background: #dcfce7; color: #15803d; font-weight: 700; font-size: 0.8rem; padding: 4px 12px; border-radius: 9999px; border: 1px solid #bbf7d0;">
        HOJE
    </span>
</div>
""", unsafe_allow_html=True)

# Buscar registros anteriores
conn = get_connection()
c = conn.cursor()

dados_sessao = []

for nome_ex, num_series, alvo_reps in FICHAS[ficha_sel]:
    yt_query = urllib.parse.quote(f"execucao {nome_ex}")
    yt_url = f"https://www.youtube.com/results?search_query={yt_query}"
    
    c.execute("""
        SELECT carga, repeticoes FROM registro_treino
        WHERE usuario = ? AND exercicio = ?
        ORDER BY id DESC LIMIT 1
    """, (USUARIO, nome_ex))
    ultimo = c.fetchone()

    st.markdown(f"""
    <div class="exercise-card">
        <div class="exercise-title">
            <span>{nome_ex}</span>
            <a href="{yt_url}" target="_blank" class="video-link">▶ Vídeo</a>
        </div>
        <div style="font-size: 0.8rem; color: #64748b; margin-bottom: 8px;">Meta: {num_series} séries &bull; {alvo_reps} reps</div>
        <div class="table-header">
            <div>SET</div>
            <div>DESCANSO</div>
            <div>KG</div>
            <div>REPS</div>
            <div>✓</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    for s in range(1, num_series + 1):
        col_set, col_desc, col_kg, col_reps, col_chk = st.columns([1, 2.4, 1.8, 1.8, 1.2])
        
        with col_set:
            st.markdown(f"<div class='set-badge'>{s}</div>", unsafe_allow_html=True)
            
        with col_desc:
            if st.button("⏱️ 60s", key=f"t_{nome_ex}_{s}"):
                st.session_state["rest_target"] = time.time() + 60
                st.rerun()
            
        with col_kg:
            carga_padrao = float(ultimo[0]) if ultimo else 20.0
            carga_val = st.number_input("kg", min_value=0.0, max_value=500.0, value=carga_padrao, step=1.0, key=f"kg_{nome_ex}_{s}")
            
        with col_reps:
            reps_padrao = int(ultimo[1]) if ultimo else 10
            reps_val = st.number_input("reps", min_value=1, max_value=100, value=reps_padrao, step=1, key=f"rep_{nome_ex}_{s}")
            
        with col_chk:
            feito = st.checkbox("", key=f"chk_{nome_ex}_{s}")
            
        dados_sessao.append((USUARIO, data_sel, ficha_sel, nome_ex, s, carga_val, reps_val, 1 if feito else 0))

conn.close()

# Botão Finalizar Treino
st.markdown("<br>", unsafe_allow_html=True)
if st.button("✓ FINALIZAR TREINO", type="primary", use_container_width=True):
    conn = get_connection()
    c = conn.cursor()
    salvos = 0
    for d in dados_sessao:
        if d[7] == 1:
            c.execute("""
                INSERT INTO registro_treino (usuario, data, ficha, exercicio, serie_num, carga, repeticoes, concluido)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, d)
            salvos += 1
    conn.commit()
    conn.close()
    if salvos > 0:
        st.balloons()
        st.success(f"🔥 Treino salvo! {salvos} séries concluídas.")
    else:
        st.warning("Marque ao menos uma série como concluída (✓) antes de finalizar.")
