import streamlit as st
import pandas as pd
from supabase import create_client, Client
import datetime

# ─────────────────────────────────────────────
#  CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Vale das Flores · Gestão",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  ESTILOS GLOBAIS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main { background-color: #F0F4F8; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F1B2D 0%, #1E3A5F 100%);
    border-right: none;
}
[data-testid="stSidebar"] * { color: #E2E8F0 !important; }
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 8px;
    color: #E2E8F0 !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] svg { fill: #94A3B8; }
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    color: #E2E8F0 !important;
    border-radius: 8px !important;
    width: 100%;
    transition: all 0.2s;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(239,68,68,0.3) !important;
    border-color: rgba(239,68,68,0.5) !important;
}

/* ── Metric Cards ── */
.metric-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 20px 24px;
    border-left: 4px solid;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
    margin-bottom: 4px;
    transition: transform 0.15s, box-shadow 0.15s;
}
.metric-card:hover { transform: translateY(-2px); box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
.metric-card.green  { border-left-color: #10B981; }
.metric-card.blue   { border-left-color: #3B82F6; }
.metric-card.red    { border-left-color: #EF4444; }
.metric-card.amber  { border-left-color: #F59E0B; }
.metric-card.purple { border-left-color: #8B5CF6; }
.metric-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: #94A3B8; margin-bottom: 8px; }
.metric-value { font-size: 28px; font-weight: 700; color: #0F1B2D; line-height: 1; margin-bottom: 4px; }
.metric-sub { font-size: 12px; color: #64748B; font-weight: 400; }

/* ── Section Headers ── */
.section-header { display: flex; align-items: center; gap: 10px; margin: 28px 0 16px; }
.section-header h3 { font-size: 16px; font-weight: 600; color: #0F1B2D; margin: 0; }
.section-divider { flex: 1; height: 1px; background: #E2E8F0; }

/* ── Tables ── */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
[data-testid="stDataFrame"] table { border-collapse: collapse; }
[data-testid="stDataFrame"] thead tr th {
    background: #0F1B2D !important;
    color: #E2E8F0 !important;
    font-weight: 600; font-size: 12px;
    text-transform: uppercase; letter-spacing: 0.06em;
    padding: 12px 16px !important;
}
[data-testid="stDataFrame"] tbody tr:nth-child(even) { background: #F8FAFC; }
[data-testid="stDataFrame"] tbody tr:hover { background: #EFF6FF; }
[data-testid="stDataFrame"] tbody td { padding: 10px 16px !important; font-size: 13px; }

/* ── Forms & Inputs ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    border-radius: 8px !important;
    border: 1.5px solid #E2E8F0 !important;
    font-size: 14px !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important;
}
.stForm [data-testid="stFormSubmitButton"] > button {
    background: #1E3A5F !important; color: white !important; border: none !important;
    padding: 10px 24px !important; border-radius: 8px !important; font-weight: 600 !important;
}
.stForm [data-testid="stFormSubmitButton"] > button:hover {
    background: #0F1B2D !important; transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(15,27,45,0.3) !important;
}
.stButton > button { border-radius: 8px !important; font-weight: 600 !important; font-size: 13px !important; transition: all 0.2s !important; }
.stAlert { border-radius: 10px !important; }

/* ── Badges ── */
.badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.badge-sindico { background: #DBEAFE; color: #1E40AF; }
.badge-condomino { background: #D1FAE5; color: #065F46; }

/* ── Page titles ── */
.page-title { font-size: 26px; font-weight: 700; color: #0F1B2D; margin-bottom: 4px; }
.page-subtitle { font-size: 14px; color: #64748B; margin-bottom: 0; }

/* ── Camera cards ── */
.camera-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
    margin-bottom: 16px;
}
.camera-title {
    font-size: 14px;
    font-weight: 600;
    color: #0F1B2D;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.live-dot {
    display: inline-block;
    width: 8px; height: 8px;
    background: #EF4444;
    border-radius: 50%;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}
.no-camera-box {
    background: #F8FAFC;
    border: 2px dashed #CBD5E1;
    border-radius: 12px;
    padding: 60px 24px;
    text-align: center;
    color: #94A3B8;
}

/* ── Login ── */
.login-btn button {
    background: #1E3A5F !important; color: white !important; border: none !important;
    border-radius: 10px !important; height: 46px !important;
    font-weight: 600 !important; font-size: 15px !important; width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CONSTANTES & SUPABASE
# ─────────────────────────────────────────────
SUPABASE_URL = "https://qsfmbvdzhhaugtwedizj.supabase.co"
SUPABASE_KEY = "sb_publishable_LUw2gLDbStafOZSeQwkL-Q_s1Re2qo4"
TOTAL_CASAS  = 26
VALOR_CONDO  = 250.00

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# ─────────────────────────────────────────────
#  HELPERS GERAIS
# ─────────────────────────────────────────────
def cpf_to_email(cpf: str) -> str:
    return f"{''.join(filter(str.isdigit, cpf))}@condo.com"

def fmt_brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def metric_card(label: str, value: str, sub: str = "", color: str = "blue") -> str:
    return f"""
    <div class="metric-card {color}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {f'<div class="metric-sub">{sub}</div>' if sub else ''}
    </div>"""

def section_header(icon: str, title: str):
    st.markdown(
        f'<div class="section-header">'
        f'<span style="font-size:18px">{icon}</span>'
        f'<h3>{title}</h3>'
        f'<div class="section-divider"></div>'
        f'</div>',
        unsafe_allow_html=True
    )

def youtube_embed(url: str, height: int = 315) -> str:
    """Converte qualquer URL do YouTube em embed iframe."""
    import re
    # Extrai o video ID de diferentes formatos de URL
    patterns = [
        r"(?:v=|youtu\.be/)([A-Za-z0-9_\-]{11})",
        r"(?:embed/)([A-Za-z0-9_\-]{11})",
        r"(?:live/)([A-Za-z0-9_\-]{11})",
    ]
    video_id = None
    for p in patterns:
        m = re.search(p, url)
        if m:
            video_id = m.group(1)
            break

    if video_id:
        embed_url = f"https://www.youtube.com/embed/{video_id}?autoplay=0&rel=0"
        return (
            f'<div class="camera-card">'
            f'<iframe width="100%" height="{height}" src="{embed_url}" '
            f'frameborder="0" allowfullscreen style="border-radius:8px;display:block;"></iframe>'
            f'</div>'
        )
    # Fallback: tenta usar a URL diretamente
    return (
        f'<div class="camera-card">'
        f'<iframe width="100%" height="{height}" src="{url}" '
        f'frameborder="0" allowfullscreen style="border-radius:8px;display:block;"></iframe>'
        f'</div>'
    )

# ─────────────────────────────────────────────
#  AUTH
# ─────────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None
if "perfil" not in st.session_state:
    st.session_state.perfil = None

def fazer_login(cpf: str, password: str):
    try:
        email = cpf_to_email(cpf)
        auth  = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user = auth.user
        perfil = (
            supabase.table("perfis")
            .select("id, nome, funcao, bloco_unidade, link_boleto")
            .eq("id", auth.user.id)
            .single()
            .execute()
        )
        st.session_state.perfil = perfil.data
        st.rerun()
    except Exception:
        st.error("CPF ou senha incorretos. Verifique suas credenciais.")

def fazer_logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    st.session_state.user  = None
    st.session_state.perfil = None
    st.rerun()

# ─────────────────────────────────────────────
#  TELA DE LOGIN
# ─────────────────────────────────────────────
if st.session_state.user is None:
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("""
        <div style="text-align:center; padding: 48px 0 24px;">
            <div style="font-size:52px; margin-bottom:10px">🏡</div>
            <div style="font-size:24px; font-weight:700; color:#0F1B2D;">Vale das Flores</div>
            <div style="font-size:14px; color:#64748B; margin-top:4px;">Portal de Transparência do Condomínio</div>
        </div>
        """, unsafe_allow_html=True)

        cpf_input   = st.text_input("CPF", placeholder="Digite apenas os números")
        senha_input = st.text_input("Senha", type="password", placeholder="Sua senha de acesso")

        st.markdown('<div class="login-btn">', unsafe_allow_html=True)
        if st.button("Entrar no Painel", use_container_width=True):
            if cpf_input and senha_input:
                fazer_login(cpf_input, senha_input)
            else:
                st.warning("Preencha CPF e senha antes de continuar.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("💻 Sistema desenvolvido por **Rômulo Henrique**")

    st.stop()

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
perfil    = st.session_state.perfil
funcao    = perfil["funcao"]
badge_cls = "badge-sindico" if funcao == "sindico" else "badge-condomino"

st.sidebar.markdown(f"""
<div style="padding: 12px 0 20px;">
    <div style="font-size:36px; margin-bottom:8px">👤</div>
    <div style="font-size:16px; font-weight:700; color:#F1F5F9">{perfil['nome']}</div>
    <div style="font-size:12px; color:#94A3B8; margin:2px 0 8px">{perfil['bloco_unidade']}</div>
    <span class="badge {badge_cls}">{funcao}</span>
</div>
<hr style="border-color:rgba(255,255,255,0.1); margin-bottom:20px">
""", unsafe_allow_html=True)

menu_options = ["📊 Dashboard", "📹 Câmeras Ao Vivo"]
if funcao == "sindico":
    menu_options += ["➕ Lançar Movimentação", "👥 Cadastrar Morador", "📄 Gerenciar Boletos"]

escolha = st.sidebar.selectbox("Navegação", menu_options, label_visibility="collapsed")

st.sidebar.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
if st.sidebar.button("Sair do Sistema 🚪", use_container_width=True):
    fazer_logout()

st.sidebar.markdown("""
<div style="position:absolute; bottom:20px; left:0; right:0; text-align:center;
     font-size:11px; color:#475569; padding:0 20px;">
    💻 Desenvolvido por<br><b style="color:#94A3B8">Rômulo Henrique</b>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  DADOS
# ─────────────────────────────────────────────
@st.cache_data(ttl=60)
def carregar_financas():
    res = supabase.table("financas").select("*").order("data", desc=True).execute()
    if not res.data:
        return pd.DataFrame()
    df = pd.DataFrame(res.data)
    df["valor"] = df["valor"].astype(float)
    df["data"]  = pd.to_datetime(df["data"])
    return df

def calcular_kpis(df: pd.DataFrame, casa_logada: str):
    hoje = datetime.date.today()
    mes, ano = hoje.month, hoje.year

    entradas = df[df["tipo"] == "entrada"]["valor"].sum()
    saidas   = df[df["tipo"] == "saida"]["valor"].sum()
    reserva  = df[df["categoria"] == "Fundo de Reserva"]["valor"].sum()
    doacoes  = df[df["categoria"] == "Doações"]["valor"].sum()

    df_mes    = df[(df["data"].dt.month == mes) & (df["data"].dt.year == ano)]
    taxas_mes = df_mes[(df_mes["categoria"] == "Taxa Condominial") & (df_mes["tipo"] == "entrada")]

    pagaram     = min(taxas_mes["casa_pagadora"].nunique() if "casa_pagadora" in taxas_mes.columns else 0, TOTAL_CASAS)
    inadimp     = TOTAL_CASAS - pagaram
    arrec_mes   = taxas_mes["valor"].sum()
    usuario_pago = (
        casa_logada in taxas_mes["casa_pagadora"].tolist()
        if "casa_pagadora" in taxas_mes.columns else False
    )

    return {
        "caixa": entradas - saidas,
        "entradas": entradas,
        "saidas": saidas,
        "reserva": reserva,
        "doacoes": doacoes,
        "pagaram": pagaram,
        "inadimp": inadimp,
        "pct_inadimp": (inadimp / TOTAL_CASAS) * 100,
        "arrec_mes": arrec_mes,
        "pro_labore": arrec_mes * 0.10,
        "mes": mes,
        "ano": ano,
        "usuario_pago": usuario_pago,
    }

# ─────────────────────────────────────────────
#  TELA: DASHBOARD
# ─────────────────────────────────────────────
if escolha == "📊 Dashboard":
    st.markdown('<div class="page-title">Painel Financeiro</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Residencial Vale das Flores · Transparência em tempo real</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    df = carregar_financas()

    if df.empty:
        st.info("Nenhuma movimentação financeira registrada ainda.")
        st.stop()

    kpi = calcular_kpis(df, perfil["bloco_unidade"])

    # Alerta de adimplência para condômino
    if funcao == "condomino":
        if not kpi["usuario_pago"]:
            st.error(
                f"⚠️ **Atenção, {perfil['nome']}:** A taxa condominial da "
                f"**{perfil['bloco_unidade']}** referente a "
                f"{kpi['mes']:02d}/{kpi['ano']} está em aberto."
            )
            if perfil.get("link_boleto"):
                st.markdown(
                    f'<a href="{perfil["link_boleto"]}" target="_blank">'
                    f'<button style="background:#EF4444;color:white;border:none;'
                    f'padding:10px 20px;border-radius:8px;font-weight:bold;cursor:pointer;">'
                    f'📥 Baixar Boleto Atualizado</button></a>',
                    unsafe_allow_html=True
                )
            else:
                st.caption("O boleto ainda não foi anexado pelo síndico.")
        else:
            st.success(
                f"✅ O pagamento da **{perfil['bloco_unidade']}** para "
                f"{kpi['mes']:02d}/{kpi['ano']} está regularizado."
            )
        st.markdown("<br>", unsafe_allow_html=True)

    # KPIs: Caixa
    section_header("💰", "Resumo do Caixa")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(metric_card("Saldo Disponível",  fmt_brl(kpi["caixa"]),    "Entradas menos saídas", "green"),  unsafe_allow_html=True)
    c2.markdown(metric_card("Total de Entradas", fmt_brl(kpi["entradas"]), "Histórico acumulado",   "blue"),   unsafe_allow_html=True)
    c3.markdown(metric_card("Total de Saídas",   fmt_brl(kpi["saidas"]),   "Histórico acumulado",   "red"),    unsafe_allow_html=True)
    c4.markdown(metric_card("Fundo de Reserva",  fmt_brl(kpi["reserva"]),  "Reserva constituída",   "purple"), unsafe_allow_html=True)

    # KPIs: Adimplência
    section_header("📉", f"Adimplência — {kpi['mes']:02d}/{kpi['ano']}")
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(metric_card("Adimplentes",       f"{kpi['pagaram']} / {TOTAL_CASAS}", f"{kpi['inadimp']} pendentes",                 "green"),  unsafe_allow_html=True)
    m2.markdown(metric_card("Inadimplentes",      f"{kpi['inadimp']} casas",           f"{kpi['pct_inadimp']:.1f}% do total",         "red"),    unsafe_allow_html=True)
    m3.markdown(metric_card("Doações Recebidas",  fmt_brl(kpi["doacoes"]),             "Total acumulado",                             "amber"),  unsafe_allow_html=True)
    m4.markdown(metric_card("Pró-Labore Síndico", fmt_brl(kpi["pro_labore"]),          f"10% de {fmt_brl(kpi['arrec_mes'])}",         "purple"), unsafe_allow_html=True)

    # Gráficos
    section_header("📈", "Análise por Categoria")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("**Origem das Receitas**")
        df_ent = df[df["tipo"] == "entrada"]
        if not df_ent.empty:
            st.bar_chart(df_ent.groupby("categoria")["valor"].sum(), color="#10B981")
        else:
            st.caption("Sem entradas registradas.")
    with col_g2:
        st.markdown("**Destinação das Despesas**")
        df_sai = df[df["tipo"] == "saida"]
        if not df_sai.empty:
            st.bar_chart(df_sai.groupby("categoria")["valor"].sum(), color="#EF4444")
        else:
            st.caption("Sem saídas registradas.")

    # Tabela + edição (síndico)
    section_header("📋", "Movimentações Registradas")

    if funcao == "sindico":
        with st.expander("✏️  Editar ou Excluir um Registro", expanded=False):
            df_sel = df.copy()
            df_sel["display"] = (
                df_sel["data"].dt.strftime("%d/%m/%Y") + " · "
                + df_sel["descricao"] + " (" + df_sel["valor"].map(fmt_brl) + ")"
            )
            selecionado = st.selectbox("Registro:", df_sel["display"].tolist(), label_visibility="collapsed")

            if selecionado:
                idx    = df_sel[df_sel["display"] == selecionado].index[0]
                reg_id = df_sel.loc[idx, "id"]
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    nova_desc = st.text_input("Descrição", value=df_sel.loc[idx, "descricao"])
                    novo_val  = st.number_input("Valor (R$)", value=float(df_sel.loc[idx, "valor"]), min_value=0.01, step=0.01)
                with col_e2:
                    cats = ["Taxa Condominial", "Doações", "Manutenção", "Água/Luz",
                            "Fundo de Reserva", "Pró-Labore Síndico", "Outros"]
                    nova_cat  = st.selectbox("Categoria", cats, index=cats.index(df_sel.loc[idx, "categoria"]))
                    nova_data = st.date_input("Data", value=df_sel.loc[idx, "data"].date())

                st.markdown("<br>", unsafe_allow_html=True)
                col_b1, col_b2, _ = st.columns([1, 1, 3])

                if col_b1.button("💾 Salvar", key=f"save_{reg_id}", use_container_width=True):
                    try:
                        supabase.table("financas").update({
                            "descricao": nova_desc, "valor": novo_val,
                            "categoria": nova_cat,  "data": str(nova_data),
                        }).eq("id", reg_id).execute()
                        carregar_financas.clear()
                        st.success("Registro atualizado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao atualizar: {e}")

                if col_b2.button("🗑️ Excluir", key=f"del_{reg_id}", use_container_width=True):
                    try:
                        supabase.table("financas").delete().eq("id", reg_id).execute()
                        carregar_financas.clear()
                        st.toast("Registro removido.", icon="🗑️")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao excluir: {e}")

    df_exib = df[["data", "descricao", "categoria", "tipo", "valor"]].copy()
    df_exib["data"]  = df_exib["data"].dt.strftime("%d/%m/%Y")
    df_exib["valor"] = df_exib["valor"].map(fmt_brl)
    df_exib.columns  = ["Data", "Descrição", "Categoria", "Tipo", "Valor"]
    st.dataframe(df_exib, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────
#  TELA: CÂMERAS AO VIVO
# ─────────────────────────────────────────────
elif escolha == "📹 Câmeras Ao Vivo":
    st.markdown('<div class="page-title">Câmeras Ao Vivo</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Monitoramento do Residencial Vale das Flores</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Painel de gerenciamento — apenas síndico
    if funcao == "sindico":
        with st.expander("⚙️ Gerenciar Câmeras", expanded=False):
            st.markdown("**Adicionar nova câmera**")
            with st.form("form_camera", clear_on_submit=True):
                col_cam1, col_cam2 = st.columns(2)
                nome_cam = col_cam1.text_input("Nome da câmera", placeholder="Ex: Portão de Entrada")
                link_cam = col_cam2.text_input("Link YouTube (live ou vídeo)", placeholder="https://youtube.com/live/...")
                if st.form_submit_button("➕ Cadastrar Câmera", use_container_width=True):
                    if nome_cam and link_cam:
                        try:
                            supabase.table("cameras").insert({
                                "nome_camera": nome_cam,
                                "link_stream": link_cam
                            }).execute()
                            st.success(f"Câmera '{nome_cam}' cadastrada com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao cadastrar câmera: {e}")
                    else:
                        st.warning("Preencha o nome e o link antes de salvar.")

            # Remover câmera
            try:
                res_cam_del = supabase.table("cameras").select("*").order("nome_camera").execute()
                if res_cam_del.data:
                    st.markdown("---")
                    st.markdown("**Remover câmera existente**")
                    cam_opcoes = {c["nome_camera"]: c["id"] for c in res_cam_del.data}
                    col_r1, col_r2 = st.columns([3, 1])
                    cam_sel = col_r1.selectbox("Selecione a câmera:", list(cam_opcoes.keys()), label_visibility="collapsed")
                    if col_r2.button("🗑️ Remover", use_container_width=True):
                        supabase.table("cameras").delete().eq("id", cam_opcoes[cam_sel]).execute()
                        st.warning(f"Câmera '{cam_sel}' removida.")
                        st.rerun()
            except Exception as e:
                st.error(f"Erro ao carregar câmeras: {e}")

    # Exibição das câmeras para todos
    try:
        res_cameras = supabase.table("cameras").select("*").order("nome_camera").execute()
    except Exception as e:
        st.error(f"Erro ao carregar câmeras: {e}")
        res_cameras = None

    if res_cameras and res_cameras.data:
        cams = res_cameras.data
        # Grade 2 colunas
        for i in range(0, len(cams), 2):
            cols = st.columns(2)
            for j, cam in enumerate(cams[i:i+2]):
                with cols[j]:
                    # Cabeçalho do card
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:8px;'
                        f'margin-bottom:8px;">'
                        f'<span class="live-dot"></span>'
                        f'<span style="font-size:14px;font-weight:600;color:#0F1B2D;">'
                        f'{cam["nome_camera"]}</span></div>',
                        unsafe_allow_html=True
                    )
                    # Embed robusto via iframe
                    st.markdown(youtube_embed(cam["link_stream"], height=280), unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="no-camera-box">
            <div style="font-size:48px;margin-bottom:12px">📷</div>
            <div style="font-size:16px;font-weight:600;color:#64748B;">Nenhuma câmera integrada</div>
            <div style="font-size:13px;margin-top:6px;">
                O síndico ainda não adicionou câmeras ao painel.
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  TELA: LANÇAR MOVIMENTAÇÃO
# ─────────────────────────────────────────────
elif escolha == "➕ Lançar Movimentação":
    st.markdown('<div class="page-title">Lançar Movimentação</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Registre entradas e saídas financeiras do condomínio</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("form_lancamento", clear_on_submit=True):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            desc   = st.text_input("Descrição do lançamento")
            val_f  = st.number_input("Valor (R$)", min_value=0.01, value=250.00, step=0.01)
            data_f = st.date_input("Data", datetime.date.today())
        with col_f2:
            tipo_f = st.selectbox("Tipo", ["entrada", "saida"],
                                  format_func=lambda x: "⬆️ Entrada" if x == "entrada" else "⬇️ Saída")
            cats   = ["Taxa Condominial", "Doações", "Manutenção", "Água/Luz",
                      "Fundo de Reserva", "Pró-Labore Síndico", "Outros"]
            cat_f  = st.selectbox("Categoria", cats)
            casas  = ["Não se aplica"] + [f"Casa {i}" for i in range(1, TOTAL_CASAS + 1)]
            casa_f = st.selectbox("Casa pagadora (Taxa Condominial)", casas)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("✅ Confirmar Registro", use_container_width=True):
            if not desc or val_f <= 0:
                st.warning("Preencha a descrição e o valor antes de confirmar.")
            else:
                casa_salvar = casa_f if cat_f == "Taxa Condominial" and casa_f != "Não se aplica" else None
                try:
                    supabase.table("financas").insert({
                        "descricao":    desc,
                        "tipo":         tipo_f,
                        "categoria":    cat_f,
                        "valor":        val_f,
                        "data":         str(data_f),
                        "casa_pagadora": casa_salvar,
                        "criado_por":   st.session_state.user.id,
                    }).execute()
                    carregar_financas.clear()
                    st.success(f"Movimentação '{desc}' registrada com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao registrar: {e}")


# ─────────────────────────────────────────────
#  TELA: CADASTRAR MORADOR
# ─────────────────────────────────────────────
elif escolha == "👥 Cadastrar Morador":
    st.markdown('<div class="page-title">Cadastrar Morador</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Crie o acesso de um novo condômino ao sistema</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("form_cadastro", clear_on_submit=True):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            nome_m  = st.text_input("Nome completo")
            cpf_m   = st.text_input("CPF (apenas números)")
            senha_m = st.text_input("Senha inicial", type="password")
        with col_c2:
            bloco_m  = st.selectbox("Casa", [f"Casa {i}" for i in range(1, TOTAL_CASAS + 1)])
            funcao_m = st.selectbox("Papel", ["condomino", "sindico"],
                                    format_func=lambda x: "Condômino" if x == "condomino" else "Síndico")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("👤 Cadastrar Morador", use_container_width=True):
            if not (nome_m and cpf_m and senha_m):
                st.warning("Preencha todos os campos obrigatórios.")
            else:
                try:
                    email_m = cpf_to_email(cpf_m)
                    auth_r  = supabase.auth.sign_up({"email": email_m, "password": senha_m})
                    if auth_r.user:
                        supabase.table("perfis").insert({
                            "id":            auth_r.user.id,
                            "nome":          nome_m,
                            "bloco_unidade": bloco_m,
                            "funcao":        funcao_m,
                        }).execute()
                        st.success(f"✅ {nome_m} da {bloco_m} cadastrado com sucesso!")
                    else:
                        st.error("Não foi possível criar o usuário. Verifique os dados.")
                except Exception as e:
                    st.error(f"Erro ao cadastrar: {e}")


# ─────────────────────────────────────────────
#  TELA: GERENCIAR BOLETOS
# ─────────────────────────────────────────────
elif escolha == "📄 Gerenciar Boletos":
    st.markdown('<div class="page-title">Gerenciar Boletos</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Insira ou atualize o link do boleto de cada casa</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    try:
        res_perfis = (
            supabase.table("perfis")
            .select("id, nome, bloco_unidade, link_boleto")
            .order("bloco_unidade")
            .execute()
        )
    except Exception as e:
        st.error(f"Erro ao carregar moradores: {e}")
        st.stop()

    if res_perfis.data:
        df_perfis = pd.DataFrame(res_perfis.data)
        df_perfis = df_perfis[df_perfis["bloco_unidade"].str.contains("Casa", na=False)]

        section_header("🔗", "Vincular Boleto a uma Casa")
        with st.form("form_boleto", clear_on_submit=True):
            opcoes = {f"{r['bloco_unidade']} — {r['nome']}": r["id"] for _, r in df_perfis.iterrows()}
            col_b1, col_b2 = st.columns(2)
            casa_sel = col_b1.selectbox("Morador / Casa", list(opcoes.keys()))
            link_url = col_b2.text_input("Link do Boleto (Google Drive, OneDrive, banco...)")

            if st.form_submit_button("💾 Salvar Boleto", use_container_width=True):
                if link_url:
                    try:
                        supabase.table("perfis").update({"link_boleto": link_url}).eq("id", opcoes[casa_sel]).execute()
                        st.success(f"Boleto atualizado para {casa_sel}!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")
                else:
                    st.warning("Insira uma URL válida antes de salvar.")

        section_header("📋", "Situação Atual dos Boletos")
        df_view = df_perfis[["bloco_unidade", "nome", "link_boleto"]].copy()
        df_view.columns = ["Casa", "Morador", "Link do Boleto"]
        df_view["Link do Boleto"] = df_view["Link do Boleto"].fillna("⚠️ Nenhum boleto anexado")
        st.dataframe(df_view, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum morador cadastrado ainda.")


# ─────────────────────────────────────────────
#  RODAPÉ
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#94A3B8; font-size:13px;'>"
    "💻 Sistema de Transparência desenvolvido por <b>Rômulo Henrique</b></p>",
    unsafe_allow_html=True
)