import streamlit.components.v1 as components
# -*- coding: utf-8 -*-
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timezone, timedelta
import urllib.parse
import time
import hashlib

st.set_page_config(
    page_title="Treino",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

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

DB_PATH = "/home/ubuntu/treino/treino.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def hash_pw(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS registro_treino (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        data TEXT,
        ficha TEXT,
        exercicio TEXT,
        serie_num INTEGER,
        carga REAL,
        repeticoes INTEGER,
        concluido INTEGER
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        username TEXT PRIMARY KEY,
        nome TEXT,
        senha_hash TEXT
    )""")
    c.execute("SELECT username FROM usuarios WHERE username = 'andre'")
    if not c.fetchone():
        c.execute("INSERT INTO usuarios (username, nome, senha_hash) VALUES (?, ?, ?)",
                  ("andre", "André", hash_pw("0404")))
    conn.commit()
    conn.close()

init_db()


def carregar_series_concluidas(usuario, data, ficha):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT exercicio, serie_num FROM registro_treino WHERE usuario = ? AND data = ? AND ficha = ? AND concluido = 1', (usuario, data, ficha))
    rows = c.fetchall()
    conn.close()
    return set((r[0], r[1]) for r in rows)

def alternar_status_serie(usuario, data, ficha, exercicio, serie_num, concluido):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM registro_treino WHERE usuario = ? AND data = ? AND ficha = ? AND exercicio = ? AND serie_num = ?', (usuario, data, ficha, exercicio, serie_num))
    if concluido:
        c.execute('INSERT INTO registro_treino (usuario, data, ficha, exercicio, serie_num, carga, repeticoes, concluido) VALUES (?, ?, ?, ?, ?, 0.0, 0, 1)', (usuario, data, ficha, exercicio, serie_num))
    conn.commit()
    conn.close()

css_code = """<style>
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
.sidebar-logout button {
    background-color: #fef2f2 !important;
    border: 1px solid #fecaca !important;
    border-radius: 10px !important;
    color: #dc2626 !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    height: 42px !important;
    transition: all 0.2s ease !important;
}
.sidebar-logout button:hover {
    background-color: #fee2e2 !important;
    border-color: #f87171 !important;
    color: #b91c1c !important;
}
.sidebar-footer {
    text-align: center;
    font-size: 0.72rem;
    color: #334155;
    font-weight: 500;
    margin-top: 25px;
    padding-top: 15px;
    border-top: 1px dashed #e2e8f0;
    line-height: 1.4;
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
    grid-template-columns: 45px 1fr 1fr;
    gap: 8px;
    font-size: 0.72rem;
    font-weight: 700;
    color: #334155;
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
    font-size: 0.85rem;
    font-weight: 700;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 40px;
}
div[data-testid="column"] button[kind="secondary"] {
    background-color: #f1f5f9 !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
    color: #475569 !important;
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    height: 40px;
    padding: 0 4px !important;
    width: 100% !important;
}
div[data-testid="column"] button[kind="secondary"]:hover {
    background-color: #334155 !important;
    border-color: #334155 !important;
    color: #0f172a !important;
}
div[data-testid="column"] button[kind="primary"] {
    background: #10b981 !important;
    bordeer: 1px solid #059669 !important;
    border-radius: 8px !important;
    color: #ffffff !important;
    font-size: 1.05rem !important;
    font-weight: 800 !important;
    height: 40px !important;
    padding: 0 !important;
    width: 100% !important;
    box-shadow: 0 2px 6px rgba(16, 185, 129, 0.35) !important;
}
div[data-testid="column"] button[kind="primary"]:hover {
    background: #059669 !important;
l}
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
    border-color: #059669 !important;
ky
</style>"""
st.markdown(css_code, unsafe_allow_html=True)

if "usuario_logado" not in st.session_state:
    user_param = st.query_params.get("u")
    if user_param:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT username, nome FROM usuarios WHERE username = ?", (user_param,))
        row = c.fetchone()
        conn.close()
        if row:
            st.session_state["usuario_logado"] = {"username": row[0], "nome": row[1]}

if "usuario_logado" not in st.session_state:
    st.markdown("""<div style="text-align: center; margin-top: 20px;">
        <span style="font-size: 2.5rem;">⚡</span>
        <h1 style="font-size: 1.6rem; font-weight: 800; color: #0f172a; margin: 4px 0;">Treino R & A</h1>
        <p style="font-size: 0.85rem; color: #64748b;">Acesse seu perfil de treino personalizado</p>
    </div>""", unsafe_allow_html=True)

    aba_login, aba_cadastro = st.tabs(["🔑 Entrar", "✨ Criar Novo Perfil"])

    with aba_login:
        with st.form("form_login"):
            st.markdown("<p style='font-size:0.85rem; font-weight:600; color:#475569; margin-bottom:4px;'>Identificação do Usuário</p>", unsafe_allow_html=True)
            u_login = st.text_input("Usuário", placeholder="ex: andre ou raissa", autocomplete="username").strip().lower()
            u_senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            btn_entrar = st.form_submit_button("Entrar no Treino", use_container_width=True)

            if btn_entrar:
                if not u_login or not u_senha:
                    st.error("Por favor, preencha o usuário e a senha.")
                else:
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute("SELECT username, nome, senha_hash FROM usuarios WHERE username = ?", (u_login,))
                    user_data = c.fetchone()
                    conn.close()

                    if user_data and user_data[2] == hash_pw(u_senha):
                        st.session_state["usuario_logado"] = {
                            "username": user_data[0],
                            "nome": user_data[1]
                        }
                        st.query_params["u"] = user_data[0]
                        st.success(f"Bem-vindo(a), {user_data[1]}!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos.")

    with aba_cadastro:
        with st.form("form_cadastro"):
            st.markdown("<p style='font-size:0.85rem; font-weight:600; color:#475569; margin-bottom:4px;'>Cadastro de Novo Usuário</p>", unsafe_allow_html=True)
            c_nome = st.text_input("Nome", placeholder="ex: Raíssa").strip()
            c_user = st.text_input("Usuário de Acesso (sem espaços)", placeholder="ex: raissa").strip().lower()
            c_senha = st.text_input("Senha de Acesso", type="password", placeholder="Crie uma senha")
            btn_cadastrar = st.form_submit_button("Criar Perfil e Entrar", use_container_width=True)

            if btn_cadastrar:
                if not c_nome or not c_user or not c_senha:
                    st.error("Preencha todos os campos para cadastrar.")
                else:
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute("SELECT username FROM usuarios WHERE username = ?", (c_user,))
                    if c.fetchone():
                        st.error(f"O usuário '{c_user}' já existe. Escolha outro ou faça login.")
                        conn.close()
                    else:
                        c.execute("INSERT INTO usuarios (username, nome, senha_hash) VALUES (?, ?, ?)",
                                  (c_user, c_nome, hash_pw(c_senha)))
                        conn.commit()
                        conn.close()
                        st.session_state["usuario_logado"] = {
                            "username": c_user,
                            "nome": c_nome
                        }
                        st.query_params["u"] = c_user
                        st.success(f"Perfil de {c_nome} criado com sucesso!")
                        time.sleep(0.5)
                        st.rerun()


    st.markdown("""<div class="sidebar-footer" style="margin-top: 40px;">
        Desenvolvido por <strong>André Dantas</strong><br>
        <span style="font-size: 0.68rem; color: #cbd5e1;">- Sistema Privado -</span>
    </div>""", unsafe_allow_html=True)
    st.stop()

USUARIO_ATUAL = st.session_state["usuario_logado"]["username"]
NOME_ATUAL = st.session_state["usuario_logado"]["nome"]

FICHAS_ANDRE = {
    "Treino - Segunda-feira": [
        ("Agachamento (Livre ou Smith)", 3, "8-10", 60),
        ("Mesa Flexora", 3, "10-12", 60),
        ("Supino Reto (Barra ou Halteres)", 3, "8-10", 60),
        ("Puxada Alta no Pulley", 3, "8-10", 60),
        ("Elevação Lateral com Halteres", 3, "12-15", 60),
        ("Tríceps Pulley (Barra reta ou V)", 3, "10-12", 60),
        ("Rosca Direta com Barra", 3, "10-12", 60),
        ("Panturrilha em Pé (Máquina ou Smith)", 3, "12-15", 60),
        ("Rosca Punho (Antebraço)", 3, "12-15", 60),
    ],
    "Treino - Terça-feira": [
        ("RDL ou Stiff", 3, "8-10", 60),
        ("Leg Press 45°", 3, "10-12", 60),
        ("Remada Curvada ou Remada Baixa", 3, "8-10", 60),
        ("Crucifixo (Halteres ou Máquina)", 3, "10-12", 60),
        ("Elevação Lateral na Polia (Cabo)", 3, "12-15", 60),
        ("Rosca Direta com Halteres", 3, "10-12", 60),
        ("Tríceps Corda na Polia", 3, "10-12", 60),
        ("Panturrilha Sentada (Gêmeos)", 3, "12-15", 60),
        ("Rosca Inversa (Barra ou Polia)", 3, "12-15", 60),
    ],
    "Treino - Quarta-feira": [
        ("Descanso Ativo / Caminhada / Mobilidade", 1, "30-45 min", 60),
    ],
    "Treino - Quinta-feira": [
        ("Agachamento Hack ou Búlgaro", 3, "10-12", 60),
        ("Cadeira Flexora", 3, "10-12", 60),
        ("Supino Inclinado (Halteres ou Barra)", 3, "8-10", 60),
        ("Remada Serrote com Halter", 3, "10-12", 60),
        ("Elevação Lateral na Máquina", 3, "12-15", 60),
        ("Tríceps Pulley (Invertida ou V)", 3, "10-12", 60),
        ("Rosca Direta com Barra W", 3, "10-12", 60),
        ("Panturrilha em Pé", 3, "12-15", 60),
        ("Rosca Punho (Antebraço)", 3, "12-15", 60),
    ],
    "Treino - Sexta-feira": [
        ("Mesa Flexora ou Flexora em Pé", 3, "10-12", 60),
        ("Cadeira Extensora ou Agachamento Frontal", 3, "12-15", 60),
        ("Puxada Pulley (Neutra ou Triângulo)", 3, "8-10", 60),
        ("Supino Reto Halteres ou Crossover", 3, "10-12", 60),
        ("Elevação Lateral com Pausa", 3, "12-15", 60),
        ("Rosca Direta no Cabo (Polia Baixa)", 3, "10-12", 60),
        ("Tríceps Corda com Abertura", 3, "10-12", 60),
        ("Panturrilha Sentada", 3, "12-15", 60),
        ("Rosca Inversa (Antebraço)", 3, "12-15", 60),
    ]
}

FICHAS_RAISSA = {
    "Treino A (Quadríceps & Empurrar)": [
        ("Agachamento Livre ou no Smith", 3, "8-10", 60),
        ("Leg Press 45°", 3, "10-12", 60),
        ("Cadeira Extensora (pausa 1s)", 3, "12-15", 60),
        ("Cadeira Abdutora", 3, "15-20", 60),
        ("Desenvolvimento com Halteres", 3, "10-12", 60),
        ("Puxada Alta Aberta no Pulley", 3, "10-12", 60),
    ],
    "Treino B (Posterior, Glúteo & Puxar)": [
        ("RDL ou Stiff", 3, "8-10", 60),
        ("Mesa Flexora ou Cadeira Flexora", 3, "10-12", 60),
        ("Agachamento Búlgaro", 3, "10-12 cada", 60),
        ("Panturrilha em Pé", 3, "12-15", 60),
        ("Remada Baixa (Triângulo) ou Curvada", 3, "10-12", 60),
        ("Supino Inclinado com Halteres", 3, "10-12", 60),
    ],
    "Treino C (Glúteo Máximo, Unilaterais & Braços)": [
        ("Elevação Pélvica (pausa 2s)", 3, "8-10", 60),
        ("Passada / Afundo Caminhando", 3, "12 passos cada", 60),
        ("Cadeira Flexora", 3, "12-15", 60),
        ("Glúteo na Polia (Cabo ou Coice)", 3, "12-15 cada", 60),
        ("Elevação Lateral (Halteres ou Cabo)", 3, "12-15", 60),
        ("Tríceps Corda + Rosca Martelo", 3, "12-15 cada", 60),
    ]
}

if USUARIO_ATUAL == "andre":
    FICHAS = FICHAS_ANDRE
else:
    FICHAS = FICHAS_RAISSA

lista_fichas = list(FICHAS.keys())
idx_padrao = lista_fichas.index(dia_semana_nome) if dia_semana_nome in lista_fichas else 0

st.sidebar.markdown(f"### 👤 {NOME_ATUAL}")
st.sidebar.caption(f"Perfil: `@{USUARIO_ATUAL}`")
st.sidebar.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

data_objeto = st.sidebar.date_input("Data", value=agora_br.date())
data_sel = data_objeto.strftime("%Y-%m-%d")

# Detecta se ja existe treino gravado nessa data para selecionar a ficha certa
try:
    _conn = get_connection()
    _c = _conn.cursor()
    _c.execute("SELECT ficha FROM registro_treino WHERE usuario = ? AND data = ? LIMIT 1", (USUARIO_ATUAL, data_sel))
    _res = _c.fetchone()
    _conn.close()
    ficha_banco = _res[0] if _res else None
except Exception:
    ficha_banco = None

if ficha_banco and ficha_banco in lista_fichas:
    idx_padrao = lista_fichas.index(ficha_banco)
else:
    _dia_sel = data_objeto.strftime("%A")
    _map = {"Sunday": 0, "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5}
    _idx = _map.get(_dia_sel, 0)
    idx_padrao = _idx if _idx < len(lista_fichas) else 0

ficha_sel = st.sidebar.selectbox("Ficha Ativa", lista_fichas, index=idx_padrao)

st.sidebar.markdown("<br><hr style='margin: 15px 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

st.sidebar.markdown('<div class="sidebar-logout">', unsafe_allow_html=True)
if st.sidebar.button("🚪 Sair do Aplicativo", use_container_width=True):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.query_params.clear()
    st.rerun()
st.sidebar.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown("""<div class="sidebar-footer">
    Desenvolvido por <strong>André Dantas</strong><br>
    <span style="font-size: 0.68rem; color: #cbd5e1;">- Sistema Privado -</span>
</div>""", unsafe_allow_html=True)

if "rest_target" in st.session_state:
    restante = int(st.session_state["rest_target"] - time.time())
    if restante > 0:
        st.markdown(f"""<div style="position: sticky; top: 0px; z-index: 9999; margin: -1rem -1rem 1.5rem -1rem; padding: 12px 18px; background: rgba(15, 23, 42, 0.95); backdrop-filter: blur(10px); border-radius: 0 0 16px 16px; border-bottom: 2px solid #10b981; box-shadow: 0 10px 25px rgba(0,0,0,0.35); display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.4rem;">⏱️</span>
                <div>
                    <div style="font-weight: 700; color: #f8fafc; font-size: 0.95rem;">Descanso em Curso</div>
                    <div style="color: #94a3b8; font-size: 0.75rem;">Respire fundo para a próxima série</div>
                </div>
            </div>
            <div style="background: #10b981; color: #022c22; font-family: monospace; font-size: 1.35rem; font-weight: 800; padding: 4px 14px; border-radius: 9999px;">
                {restante}s
            </div>
        </div>""", unsafe_allow_html=True)
        if st.session_state.pop("subir_scroll", False):
            components.html('', height=0)
        time.sleep(1)
        st.rerun()
    else:
        st.markdown("""<div style="position: sticky; top: 0px; z-index: 9999; margin: -1rem -1rem 1.5rem -1rem; padding: 12px 18px; background: #ecfdf5; border-radius: 0 0 16px 16px; border-bottom: 2px solid #10b981; box-shadow: 0 10px 20px rgba(16, 185, 129, 0.2); text-align: center;">
            <span style="font-size: 1.05rem; font-weight: 800; color: #065f46;">🔔 Descanso Concluído! Próxima série!</span>
        </div>""", unsafe_allow_html=True)
        _alvo = st.session_state.get("alvo_scroll", "")
        if _alvo:
            _js = f'<script>setTimeout(function(){{ var el = window.parent.document.getElementById("{_alvo}"); if (el) {{ el.scrollIntoView({{behavior: "smooth", block: "center"}}); }} }}, 300);</script>'
            components.html(_js, height=0)
        del st.session_state["rest_target"]

dia_semana_abrev = agora_br.strftime("%A")
DIAS_PT = {
    "Monday": "Segunda-feira", "Tuesday": "Terça-feira", "Wednesday": "Quarta-feira",
    "Thursday": "Quinta-feira", "Friday": "Sexta-feira", "Saturday": "Sábado", "Sunday": "Domingo"
}
dia_nome_pt = DIAS_PT.get(dia_semana_abrev, dia_semana_abrev)

st.markdown(f"""<div class="hevy-header">
    <div>
        <h1 class="hevy-title">{ficha_sel}</h1>
        <p class="hevy-subtitle">{NOME_ATUAL} &bull; {dia_nome_pt} &bull; {agora_br.strftime('%d/%m/%Y')}</p>
    </div>
    <span style="background: #dcfce7; color: #15803d; font-weight: 700; font-size: 0.8rem; padding: 4px 12px; border-radius: 9999px; border: 1px solid #bbf7d0;">
        HOJE
    </span>
</div>""", unsafe_allow_html=True)

conn = get_connection()
dados_sessao = []
series_feitas_hoje = carregar_series_concluidas(USUARIO_ATUAL, data_sel, ficha_sel)

for item in FICHAS[ficha_sel]:
    nome_ex = item[0]
    num_series = item[1]
    alvo_reps = item[2]
    descanso_seg = 60

    yt_query = urllib.parse.quote(f"execucao {nome_ex}")
    yt_url = f"https://www.youtube.com/results?search_query={yt_query}"

    st.markdown(f"""<div class="exercise-card">
        <div class="exercise-title">
            <span>{nome_ex}</span>
            <a href="{yt_url}" target="_blank" class="video-link">▶ Vídeo</a>
        </div>
        <div style="font-size: 0.8rem; color: #64748b; margin-bottom: 8px;">Meta: {num_series} séries &bull; {alvo_reps} reps &bull; ⏱️ 60s</div>
        <div class="table-header">
            <div>SET</div>
            <div>DESCANSO</div>
            <div>STATUS</div>
        </div>
    </div>""", unsafe_allow_html=True)

    for s in range(1, num_series + 1):
        ancora_id = f"card_{s}_" + nome_ex.replace(" ", "_").replace("(", "").replace(")", "").replace("/", "")
        st.markdown(f"<div id='{ancora_id}'></div>", unsafe_allow_html=True)
        col_set, col_desc, col_done = st.columns([1, 2.5, 2.5])

        with col_set:
            st.markdown(f"<div class='set-badge'>{s}</div>", unsafe_allow_html=True)

        with col_desc:
            label_desc = "⏱️ 60s"
            if st.button(label_desc, key=f"t_{nome_ex}_{s}"):
                st.session_state["alvo_scroll"] = ancora_id
                st.session_state["subir_scroll"] = True
                st.session_state["rest_target"] = time.time() + 60
                st.rerun()

        with col_done:
            done_key = f"done_{data_sel}_{ficha_sel}_{nome_ex}_{s}"
            if done_key not in st.session_state:
                st.session_state[done_key] = (nome_ex, s) in series_feitas_hoje
            is_done = st.session_state[done_key]
            btn_label = "✓"
            btn_type = "primary" if is_done else "secondary"

            if st.button(btn_label, key=f"btn_done_{nome_ex}_{s}", type=btn_type, use_container_width=True):
                novo_estado = not is_done
                st.session_state[done_key] = novo_estado
                alternar_status_serie(USUARIO_ATUAL, data_sel, ficha_sel, nome_ex, s, novo_estado)
                if novo_estado:
                    st.session_state["alvo_scroll"] = ancora_id
                st.session_state["subir_scroll"] = True
                    st.session_state["rest_target"] = time.time() + 60
                st.rerun()

        dados_sessao.append((USUARIO_ATUAL, data_sel, ficha_sel, nome_ex, s, 0.0, 0, 1 if is_done else 0))

conn.close()

st.markdown('<div class="finish-btn">', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
if st.button("✓ FINALIZAR TREINO", key="finish_all"):
    conn = get_connection()
    c = conn.cursor()
    salvos = 0
    for d in dados_sessao:
        if d[7] == 1:
            c.execute("""INSERT INTO registro_treino (usuario, data, ficha, exercicio, serie_num, carga, repeticoes, concluido)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", d)
            salvos += 1
    conn.commit()
    conn.close()
    if salvos > 0:
        st.balloons()
        st.success(f"🔥 Treino salvo! {salvos} séries concluídas.")
    else:
        st.warning("Marque ao menos uma série como concluída (✓) antes de finalizar.")
st.markdown('</div>', unsafe_allow_html=True)

try:
    with open("/home/ubuntu/treino/style.css") as f_css:
        st.markdown(f"", unsafe_allow_html=True)
except Exception:
    pass
