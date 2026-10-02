# -*- coding: utf-8 -*-
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timezone, timedelta
import urllib.parse
import time

# --- CONFIGURACAO DA PAGINA ---
st.set_page_config(
    page_title="Treino",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- FUSO HORARIO E DATA ---
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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700;800&display=swap');

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

    /* Banner Digital do Timer */
    .timer-active-banner {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border: 2px solid #3b82f6;
        border-radius: 16px;
        padding: 16px;
        text-align: center;
        margin-bottom: 18px;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.16);
    }
    .timer-title {
        font-size: 0.85rem;
        font-weight: 700;
        color: #1d4ed8;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    .timer-countdown {
        font-size: 3rem;
        font-weight: 800;
        color: #1e3a8a;
        font-family: 'JetBrains Mono', monospace;
        line-height: 1.1;
        margin: 6px 0 4px 0;
        letter-spacing: -1px;
    }
    .timer-footer {
        font-size: 0.78rem;
        color: #3b82f6;
        font-weight: 600;
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
        grid-template-columns: 36px 1fr 65px 65px 44px;
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
        *ustify-content: center;
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

    /* Botães padrão (Descanso e Feito Inativo) */
    div[data-testid="column"] button[kind="secondary"] {
        background-color: #f1f5f9!important;
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

    /* Botão FEITO ATIVO (Verde Vibrante) */
    div[data-testid="column"] button[kind="primary"] {
        background: #10b981 !important;
        border: 1px solid #059669 !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        font-size: 0.95rem !important;
        font-weight: 800 !important;
        height: 38px !important;
        padding: 0 !important;
        width: 100% !important;
        box-shadow: 0 2px 6px rgba(16, 185, 129, 0.35) !important;
    }
    div[data-testid="column"] button[kind="primary"]:hover {
        background: #059669 !important;
    }

    /* Botão Finalizar Treino (Grande no final) */
    .finish-btn button {
        background: #10b981 !important;
        border: none !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        min-height: 48px !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
        cursor: pointer !important;
        width: 100% !important;
    }
    .finish-btn button:hover {
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

# --- FICHAS ATUALIZADAS (DESCANSO 90s ALTERADO PARA 60s) ---
FICHAS = {
    "Treino - Segunda-feira": [
        ("Agachamento (Livre ou Smith)", 4, "8-10", 120),
        ("Mesa Flexora", 4, "10-12", 60),
        ("Supino Reto (Barra ou Halteres)", 4, "8-10", 60),
        ("Puxada Alta no Pulley", 4, "8-10", 60),
        ("Elevação Lateral com Halteres", 4, "12-15", 60),
        ("Tríceps Pulley (Barra reta ou V)", 4, "10-12", 60),
        ("Rosca Direta com Barra", 4, "10-12", 60),
        ("Panturrilha em Pé (Máquina ou Smith)", 4, "12-15", 60),
        ("Rosca Punho (Antebraço)", 3, "12-15", 60),
    ],
    "Treino - Terça-feira": [
        ("RDL ou Stiff", 4, "8-10", 120),
        ("Leg Press 45°", 4, "10-12", 60),
        ("Remada Curvada ou Remada Baixa", 4, "8-10", 60),
        ("Crucifixo (Halteres ou Máquina)", 4, "10-12", 60),
        ("Elevação Lateral na Polia (Cabo)", 4, "12-15", 60),
        ("Rosca Direta com Halteres", 4, "10-12", 60),
        ("Tríceps Corda na Polia", 4, "10-12", 60),
        ("Panturrilha Sentada (Gêmeos)", 4, "12-15", 60),
        ("Rosca Inversa (Barra ou Polia)", 3, "12-15", 60),
    ],
    "Treino - Quarta-feira": [
        ("Descanso Ativo / Caminhada / Mobilidade", 1, "30-45 min", 60),
    ],
    "Treino - Quinta-feira": [
        ("Agachamento Hack ou Búlgaro", 4, "10-12", 60),
        ("Cadeira Flexora", 4, "10-12", 60),
        ("Supino Inclinado (Halteres ou Barra)", 4, "8-10", 60),
        ("Remada Serrote com Halter", 4, "10-12", 60),
        ("Elevação Lateral na Máquina", 4, "12-15", 60),
        ("Tríceps Pulley (Invertida ou V)", 4, "10-12", 60),
        ("Rosca Direta com Barra W", 4, "10-12", 60),
        ("Panturrilha em Pé", 4, "12-15", 60),
        ("Rosca Punho (Antebraço)", 3, "12-15", 60),
    ],
    "Treino - Sexta-feira": [
        ("Mesa Flexora ou Flexora em Pé", 4, "10-12", 60),
        ("Cadeira Extensora ou Agachamento Frontal", 4, "12-15", 60),
        ("Puxada Pulley (Neutra ou Triângulo)", 4, "8-10", 60),
        ("Supino Reto Halteres ou Crossover", 4, "10-12", 60),
        ("Elevação Lateral com Pausa", 4, "12-15", 60),
        ("Rosca Direta no Cabo (Polia Baixa)", 4, "10-12", 60),
        ("Tríceps Corda com Abertura", 4, "10-12", 60),
        ("Panturrilha Sentada", 4, "12-15", 60),
        ("Rosca Inversa (Antebraço)", 3, "12-15", 60),
    ]
}

lista_fichas = list(FICHAS.keys())
idx_padrao = lista_fichas.index(dia_semana_nome) if dia_semana_nome in lista_fichas else 0

# --- BARRA LATERAL ---
ficha_sel = st.sidebar.selectbox("Ficha Ativa", lista_fichas, index=idx_padrao)
data_sel = st.sidebar.date_input("Data", value=agora_br.date()).strftime("%Y-%m-%d")

# --- CONTADOR DE DESCANSO ATIVO COM FONTE GIGANTE ---
if "rest_target" in st.session_state:
    restante = int(st.session_state["rest_target"] - time.time())
    if restante > 0:
        st.markdown(f"""
        <div class="timer-active-banner">
            <div class="timer-title">⏱️ Descanso em Curso</div>
            <div class="timer-countdown">{restante}s</div>
            <div class="timer-footer">Respire fundo e recupere o fôlego para a próxima série!</div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(1)
        st.rerun()
    else:
        st.markdown("""
        <div style="background: #ecfdf5; border: 2px solid #10b981; border-radius: 14px; padding: 14px; text-align: center; margin-bottom: 18px;">
            <span style="font-size: 1.15rem; font-weight: 800; color: #065f46;">🔔 Descanso Concluído! Próxima série!</span>
        </div>
        """, unsafe_allow_html=True)
        del st.session_state["rest_target"]

# --- CABECALHO ---
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

for item in FICHAS[ficha_sel]:
    nome_ex = item[0]
    num_series = item[1]
    alvo_reps = item[2]
    descanso_seg = item[3] if len(item) > 3 else 60

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
        <div style="font-size: 0.8rem; color: #64748b; margin-bottom: 8px;">Meta: {num_series} séries &bull; {alvo_reps} reps &bull; ⏱️ {descanso_seg}s</div>
        <div class="table-header">
            <div>SET</div>
            <div>DESCANSO</div>
            <div>KG</div>
            <div>REPS</div>
            <div>STATUS</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    for s in range(1, num_series + 1):
        col_set, col_desc, col_kg, col_reps, col_done = st.columns([1, 2.4, 1.8, 1.8, 1.3])
        
        with col_set:
            st.markdown(f"<div class='set-badge'>{s}</div>", unsafe_allow_html=True)
            
        with col_desc:
            label_desc = f"⏱️ {descanso_seg}s"
            if st.button(label_desc, key=f"t_{nome_ex}_{s}"):
                st.session_state["rest_target"] = time.time() + descanso_seg
                st.rerun()
            
        with col_kg:
            carga_padrao = float(ultimo[0]) if ultimo else 20.0
            carga_val = st.number_input("kg", min_value=0.0, max_value=500.0, value=carga_padrao, step=1.0, key=f"kg_{nome_ex}_{s}")
            
        with col_reps:
            reps_padrao = int(ultimo[1]) if ultimo else 10
            reps_val = st.number_input("reps", min_value=1, max_value=100, value=reps_padrao, step=1, key=f"rep_{nome_ex}_{s}")
            
        with col_done:
            done_key = f"done_{nome_ex}_{s}"
            is_done = st.session_state.get(done_key, False)
            btn_label = "✓" if is_done else "—"
            btn_type = "primary" if is_done else "secondary"
            
            if st.button(btn_label, key=f"btn_done_{nome_ex}_{s}", type=btn_type):
                novo_estado = not is_done
                st.session_state[done_key] = novo_estado
                if novo_estado:
                    # Inicia automaticamente o descanso da série ao concluir!
                    st.session_state["rest_target"] = time.time() + descanso_seg
                st.rerun()
            
        dados_sessao.append((USUARIO, data_sel, ficha_sel, nome_ex, s, carga_val, reps_val, 1 if is_done else 0))

conn.close()

# Botao Finalizar Treino
st.markdown('<div class="finish-btn">', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
if st.button("✓ FINALIZAR TREINO", key="finish_all"):
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
st.markdown('</div>', unsafe_allow_html=True)
