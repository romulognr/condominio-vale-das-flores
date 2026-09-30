import streamlit as st
import pandas as pd
from supabase import create_client, Client
import datetime
import uuid
import os
import base64

# ─────────────────────────────────────────────
#  CONFIGURAÇÃO DA PÁGINA E LOGÓTIPO
# ─────────────────────────────────────────────
st.set_page_config(page_title="Vale das Flores · Gestão", page_icon="🏡", layout="wide", initial_sidebar_state="expanded")

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

logo_base64 = get_base64_image("icon.png")

# ─────────────────────────────────────────────
#  ESTILOS GLOBAIS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main { background-color: #F0F4F8; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0F1B2D 0%, #1E3A5F 100%); border-right: none; }
[data-testid="stSidebar"] * { color: #E2E8F0 !important; }
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); border-radius: 8px; color: #E2E8F0 !important; }
[data-testid="stSidebar"] [data-testid="stSelectbox"] svg { fill: #94A3B8; }
[data-testid="stSidebar"] .stButton > button { background: rgba(255,255,255,0.08) !important; border: 1px solid rgba(255,255,255,0.2) !important; color: #E2E8F0 !important; border-radius: 8px !important; width: 100%; transition: all 0.2s; }
[data-testid="stSidebar"] .stButton > button:hover { background: rgba(239,68,68,0.3) !important; border-color: rgba(239,68,68,0.5) !important; }
.metric-card { background: #FFFFFF; border-radius: 12px; padding: 20px 24px; border-left: 4px solid; box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04); margin-bottom: 4px; transition: transform 0.15s, box-shadow 0.15s; }
.metric-card:hover { transform: translateY(-2px); box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
.metric-card.green  { border-left-color: #10B981; }
.metric-card.blue   { border-left-color: #3B82F6; }
.metric-card.red    { border-left-color: #EF4444; }
.metric-card.amber  { border-left-color: #F59E0B; }
.metric-card.purple { border-left-color: #8B5CF6; }
.metric-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: #94A3B8; margin-bottom: 8px; }
.metric-value { font-size: 28px; font-weight: 700; color: #0F1B2D; line-height: 1; margin-bottom: 4px; }
.metric-sub { font-size: 12px; color: #64748B; font-weight: 400; }
.section-header { display: flex; align-items: center; gap: 10px; margin: 28px 0 16px; }
.section-header h3 { font-size: 16px; font-weight: 600; color: #0F1B2D; margin: 0; }
.section-divider { flex: 1; height: 1px; background: #E2E8F0; }
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
[data-testid="stDataFrame"] thead tr th { background: #0F1B2D !important; color: #E2E8F0 !important; font-weight: 600; font-size: 12px; text-transform: uppercase; padding: 12px 16px !important; }
.stTextInput > div > div > input, .stNumberInput > div > div > input, .stSelectbox > div > div, .stTextArea > div > div > textarea { border-radius: 8px !important; border: 1.5px solid #E2E8F0 !important; font-size: 14px !important; }
.stForm [data-testid="stFormSubmitButton"] > button { background: #1E3A5F !important; color: white !important; border: none !important; padding: 10px 24px !important; border-radius: 8px !important; font-weight: 600 !important; }
.badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.badge-sindico { background: #DBEAFE !important; color: #1E40AF !important; }
.badge-condomino { background: #D1FAE5 !important; color: #065F46 !important; }
.page-title { font-size: 26px; font-weight: 700; color: #0F1B2D; margin-bottom: 4px; }
.page-subtitle { font-size: 14px; color: #64748B; margin-bottom: 0; }
.login-btn button { background: #1E3A5F !important; color: white !important; border: none !important; border-radius: 10px !important; height: 46px !important; font-weight: 600 !important; font-size: 15px !important; width: 100%; }
.relatorio-box { background: white; padding: 24px; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-bottom: 20px;}
.relatorio-box h4 { color: #1E3A5F; font-weight: 700; margin-top:0;}
.relatorio-box ul { margin-top: 10px; margin-bottom: 10px; padding-left: 20px; }
.relatorio-box li { margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CONSTANTES & SUPABASE
# ─────────────────────────────────────────────
SUPABASE_URL = "https://qsfmbvdzhhaugtwedizj.supabase.co"
SUPABASE_KEY = "sb_publishable_LUw2gLDbStafOZSeQwkL-Q_s1Re2qo4"
TOTAL_CASAS  = 26

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

def fmt_brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def metric_card(label: str, value: str, sub: str = "", color: str = "blue") -> str:
    return f'<div class="metric-card {color}"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-sub">{sub}</div></div>'

def section_header(icon: str, title: str):
    st.markdown(f'<div class="section-header"><span style="font-size:18px">{icon}</span><h3>{title}</h3><div class="section-divider"></div></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  AUTH
# ─────────────────────────────────────────────
if "user" not in st.session_state: st.session_state.user = None
if "perfil" not in st.session_state: st.session_state.perfil = None

def fazer_login(login_input: str, password_input: str):
    try:
        clean_login = login_input.strip().lower()
        res = supabase.table("perfis").select("*").eq("login", clean_login).execute()
        if res.data and len(res.data) > 0:
            perfil_encontrado = res.data[0]
            if perfil_encontrado.get("senha") == password_input:
                st.session_state.user = {"id": perfil_encontrado["id"]}
                st.session_state.perfil = perfil_encontrado
                st.rerun()
            else:
                st.error("Senha incorreta.")
        else:
            st.error("Utilizador não encontrado.")
    except Exception as e:
        st.error(f"Erro ao efetuar login: {e}")

def fazer_logout():
    st.session_state.user = None
    st.session_state.perfil = None
    st.rerun()

if st.session_state.user is None or st.session_state.perfil is None:
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        if logo_base64:
            st.markdown(f'<div style="text-align:center; padding: 20px 0;"><img src="data:image/png;base64,{logo_base64}" style="max-width:200px;"></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:center; padding: 48px 0 24px;"><div style="font-size:52px; margin-bottom:10px">🏡</div><div style="font-size:24px; font-weight:700; color:#0F1B2D;">Vale das Flores</div><div style="font-size:14px; color:#64748B; margin-top:4px;">Portal de Transparência do Condomínio</div></div>', unsafe_allow_html=True)
        
        login_input = st.text_input("Login", placeholder="Digite 'administrador' ou seu CPF")
        senha_input = st.text_input("Senha", type="password", placeholder="Sua senha")
        st.markdown('<div class="login-btn">', unsafe_allow_html=True)
        if st.button("Entrar no Painel", use_container_width=True):
            if login_input and senha_input: fazer_login(login_input, senha_input)
            else: st.warning("Preencha Login e Senha.")
        st.markdown('</div><br>', unsafe_allow_html=True)
        st.caption("💻 Sistema desenvolvido por **Rômulo Henrique**")
    st.stop()

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
perfil = st.session_state.perfil
funcao = perfil["funcao"]
st.sidebar.markdown(f'<div style="padding: 12px 0 20px;"><div style="font-size:36px; margin-bottom:8px">👤</div><div style="font-size:16px; font-weight:700; color:#F1F5F9">{perfil["nome"]}</div><div style="font-size:12px; color:#94A3B8; margin:2px 0 8px">{perfil["bloco_unidade"]}</div><span class="badge {"badge-sindico" if funcao == "sindico" else "badge-condomino"}">{funcao}</span></div><hr style="border-color:rgba(255,255,255,0.1); margin-bottom:20px">', unsafe_allow_html=True)

menu_options = ["📊 Dashboard", "📑 Relatórios Oficiais", "📹 Câmeras Ao Vivo"]
if funcao == "sindico":
    menu_options += ["➕ Lançar Movimentação", "👥 Cadastrar Morador", "📄 Gestão de Boletos"]

escolha = st.sidebar.selectbox("Navegação", menu_options, label_visibility="collapsed")
st.sidebar.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
if st.sidebar.button("Sair do Sistema 🚪", use_container_width=True): fazer_logout()

@st.cache_data(ttl=60)
def carregar_financas():
    res = supabase.table("financas").select("*").order("data", desc=True).execute()
    if not res.data: return pd.DataFrame()
    df = pd.DataFrame(res.data)
    df["valor"] = df["valor"].astype(float)
    df["data"]  = pd.to_datetime(df["data"])
    return df

def calcular_kpis(df: pd.DataFrame, casa_logada: str, mes_sel: int, ano_sel: int):
    entradas = df[df["tipo"] == "entrada"]["valor"].sum() if not df.empty else 0
    saidas   = df[df["tipo"] == "saida"]["valor"].sum() if not df.empty else 0
    
    df_mes = df[(df["data"].dt.month == mes_sel) & (df["data"].dt.year == ano_sel)] if not df.empty else pd.DataFrame()
    taxas_mes = df_mes[(df_mes["categoria"] == "Taxa Condominial") & (df_mes["tipo"] == "entrada")] if not df_mes.empty else pd.DataFrame()
    
    if not taxas_mes.empty:
        cotas_pagas = sum([round(v / 250) for v in taxas_mes["valor"]])
        pagaram = min(int(cotas_pagas), TOTAL_CASAS)
    else:
        pagaram = 0
        
    arrec_mes = taxas_mes["valor"].sum() if not taxas_mes.empty else 0
    saldo_global = entradas - saidas
    mes_iniciado = not df_mes.empty
    
    # Validação exclusiva pelo extrato (finanças)
    usuario_pago = casa_logada in taxas_mes["casa_pagadora"].tolist() if not taxas_mes.empty and "casa_pagadora" in taxas_mes.columns else False
    
    return {
        "caixa": saldo_global, "entradas": entradas, "saidas": saidas,
        "pagaram": pagaram, "inadimp": TOTAL_CASAS - pagaram, "pct_inadimp": ((TOTAL_CASAS - pagaram) / TOTAL_CASAS) * 100,
        "arrec_mes": arrec_mes, "mes": mes_sel, "ano": ano_sel,
        "usuario_pago": usuario_pago, "mes_iniciado": mes_iniciado
    }

# ─────────────────────────────────────────────
#  TELA: DASHBOARD
# ─────────────────────────────────────────────
if escolha == "📊 Dashboard":
    if logo_base64:
        st.markdown(f'<div style="margin-bottom:10px;"><img src="data:image/png;base64,{logo_base64}" style="max-width:150px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Painel Financeiro</div><div class="page-subtitle">Transparência e Resultados</div><br>', unsafe_allow_html=True)
    
    # Atualiza os dados do perfil logado na hora
    res_perfil_atual = supabase.table("perfis").select("*").eq("id", st.session_state.perfil["id"]).single().execute()
    if res_perfil_atual.data:
        perfil = res_perfil_atual.data
        st.session_state.perfil = perfil

    df = carregar_financas()
    hoje = datetime.date.today()
    periodo_atual = f"{hoje.month:02d}/{hoje.year}"
    
    periodos_str = []
    if not df.empty:
        periodos = df['data'].dt.to_period('M').unique().tolist()
        periodos_str = sorted([f"{p.month:02d}/{p.year}" for p in periodos], reverse=True)
    
    for extra_month in range(0, 3):
        m = (hoje.month + extra_month - 1) % 12 + 1
        y = hoje.year + (hoje.month + extra_month - 1) // 12
        p_str = f"{m:02d}/{y}"
        if p_str not in periodos_str:
            periodos_str.append(p_str)
            
    periodos_str = sorted(periodos_str, reverse=True)
    
    col_sel1, col_sel2 = st.columns([1, 3])
    with col_sel1:
        periodo_selecionado = st.selectbox("📅 Selecione o Mês de Referência:", periodos_str, index=periodos_str.index(periodo_atual) if periodo_atual in periodos_str else 0)
    
    mes_str, ano_str = periodo_selecionado.split("/")
    mes_sel, ano_sel = int(mes_str), int(ano_str)
    
    if not df.empty:
        kpi = calcular_kpis(df, perfil["bloco_unidade"], mes_sel, ano_sel)

        if funcao == "condomino":
            # ALERTA DE BOLETO EM ATRASO (Com Geração Automática de Múltiplos Botões)
            if perfil.get("boleto_atraso"):
                meses_atrasados = perfil.get("meses_atraso") or "meses anteriores"
                
                # Extrai os links separando por quebra de linha ou espaço
                raw_links = perfil["boleto_atraso"].replace(',', ' ').replace('\n', ' ').split(' ')
                links = [l.strip() for l in raw_links if l.strip().startswith('http')]
                
                botoes_html = ""
                if len(links) > 0:
                    for i, link in enumerate(links):
                        label = f"Baixar Boleto {i+1}" if len(links) > 1 else "Baixar Boleto Atualizado"
                        botoes_html += f'<a href="{link}" target="_blank"><button style="background:#EF4444;color:white;border:none;padding:12px 24px;border-radius:8px;font-weight:bold;cursor:pointer;margin-right:10px;margin-bottom:10px;">{label}</button></a>'
                else:
                    botoes_html = f'<a href="{perfil["boleto_atraso"]}" target="_blank"><button style="background:#EF4444;color:white;border:none;padding:12px 24px;border-radius:8px;font-weight:bold;cursor:pointer;">Baixar Boleto em Atraso</button></a>'

                st.markdown(f'<div style="background:#FEF2F2; border: 1px solid #EF4444; border-radius: 8px; padding: 24px; margin-bottom: 24px;">'
                            f'<h4 style="color:#B91C1C; margin-top:0;">🚨 ATENÇÃO: Pendências Financeiras</h4>'
                            f'<p style="color:#991B1B; margin-bottom:15px;">Identificámos pendências referentes a: <b>{meses_atrasados}</b>. Por favor, regularize a situação para evitarmos a suspensão de serviços.</p>'
                            f'<div>{botoes_html}</div>'
                            f'</div>', unsafe_allow_html=True)

            st.markdown(f"### 📌 Situação da {perfil['bloco_unidade']} ({periodo_selecionado})")
            
            if not kpi["mes_iniciado"]:
                st.info(f"⏳ A faturação deste mês ainda não foi processada.")
            elif not kpi["usuario_pago"]:
                col_c1, col_c2 = st.columns([2, 1])
                with col_c1:
                    st.error(f"⚠️ A taxa deste mês está em aberto.")
                with col_c2:
                    if perfil.get("link_boleto"):
                        st.markdown(f'<a href="{perfil["link_boleto"]}" target="_blank"><button style="background:#3B82F6;color:white;border:none;padding:10px 20px;border-radius:8px;font-weight:bold;width:100%;cursor:pointer;">📥 Descarregar Boleto do Mês</button></a>', unsafe_allow_html=True)
            else:
                st.success(f"✅ O pagamento deste mês encontra-se regularizado no sistema.")
            st.markdown("---")

        section_header("💰", "Resumo do Caixa (Histórico Completo)")
        c1, c2, c3 = st.columns(3)
        c1.markdown(metric_card("Saldo Global", fmt_brl(kpi["caixa"]), "Total em conta", "green"), unsafe_allow_html=True)
        c2.markdown(metric_card("Entradas G.", fmt_brl(kpi["entradas"]), "Acumulado", "blue"), unsafe_allow_html=True)
        c3.markdown(metric_card("Saídas G.", fmt_brl(kpi["saidas"]), "Acumulado", "red"), unsafe_allow_html=True)

        section_header("📉", f"Balanço do Mês ({periodo_selecionado})")
        m1, m2, m3 = st.columns(3)
        m1.markdown(metric_card("Adimplentes", f"{kpi['pagaram']}/{TOTAL_CASAS}", "", "green"), unsafe_allow_html=True)
        m2.markdown(metric_card("Inadimplentes", f"{kpi['inadimp']} casas", f"{kpi['pct_inadimp']:.1f}%", "red"), unsafe_allow_html=True)
        m3.markdown(metric_card("Arrecadado", fmt_brl(kpi["arrec_mes"]), "Neste mês", "blue"), unsafe_allow_html=True)

        section_header("📋", f"Movimentações Detalhadas ({periodo_selecionado})")
        df_exib = df[(df["data"].dt.month == mes_sel) & (df["data"].dt.year == ano_sel)][["data", "descricao", "categoria", "tipo", "valor"]].copy()
        
        if not df_exib.empty:
            df_exib["data"] = df_exib["data"].dt.strftime("%d/%m/%Y")
            df_exib["valor"] = df_exib["valor"].map(fmt_brl)
            st.dataframe(df_exib, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma movimentação registada para o mês selecionado.")
    else:
        st.info("O sistema financeiro ainda não tem movimentações. Importe a primeira planilha ou faça um lançamento manual.")

# ─────────────────────────────────────────────
#  TELA: RELATÓRIOS OFICIAIS (PDFs Extraídos)
# ─────────────────────────────────────────────
elif escolha == "📑 Relatórios Oficiais":
    st.markdown('<div class="page-title">Relatórios da Gestão</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Comunicados, resumos e transparência emitidos pelo Síndico.</div><br>', unsafe_allow_html=True)

    with st.expander("📄 Relatório Financeiro - Setembro/2026", expanded=True):
        st.markdown(r"""
        <div class="relatorio-box">
        <h4>Assunto: Relatório Financeiro Mensal</h4>
        <p>Para garantirmos a transparência total da nossa gestão e mantermos todos informados sobre a saúde financeira do Residencial Vale das Flores, envio o detalhamento das movimentações da nossa conta bancária referente ao mês de Setembro.</p>
        <p><b>Saldo Final de Agosto:</b> R\$ 2.908,63</p>
        <p><b>SETEMBRO/2026</b></p>
        <ul>
            <li><b>Entradas (Arrecadação de Taxas):</b> Recebimentos das cotas regulares e taxa unificada.</li>
            <li><b>Saídas (Contas de Consumo):</b> R\$ 472,18 (Equatorial Energia: faturas de R\$ 85,47 e R\$ 386,71).</li>
            <li><b>Saídas (Prestadores de Serviço):</b> R\$ 4.375,00 (Jean Pierre: R\$ 3.000,00 | Fernando Coelho [Encanador]: R\$ 775,00 | El Shaddai Construções: R\$ 600,00).</li>
            <li><b>Saídas (Materiais e Insumos):</b> R\$ 477,12 (Mateus Supermercados, Uni Cores, R G de Sousa, Rato Ferragista, Oliveira Construções).</li>
            <li><b>Saídas (Gestão e Administrativo):</b> R\$ 892,04 (Síndico: R\$ 650,00 | PIX Marketplace: R\$ 192,04 | Louriane de Assis: R\$ 50,00).</li>
        </ul>
        <p><b>Saldo Atual em Conta:</b> R\$ 1.197,79</p>
        <p><b>QUADRO DE INADIMPLÊNCIA ATUALIZADO</b></p>
        <ul>
            <li><b>Inadimplência Acumulada:</b> R\$ 2.000,00 (Valor referente a 8 cotas condominiais em atraso, referentes aos meses de Julho e Agosto).</li>
            <li><i>Nota da Gestão:</i> Já estamos em contato de forma individual com as unidades pendentes para facilitar a regularização.</li>
        </ul>
        <br><i>Todos os comprovantes estão rigorosamente arquivados comigo. Sigo à total disposição para conversarmos.</i><br>
        <b>Um abraço, Rômulo Henrique da Silva Lima<br>Síndico - Condomínio Vale das Flores</b>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("📄 Relatório Financeiro - Agosto/2026", expanded=False):
        st.markdown(r"""
        <div class="relatorio-box">
        <h4>Assunto: Relatório Financeiro Mensal</h4>
        <p>Para garantirmos a transparência total da nossa gestão e mantermos todos informados sobre a saúde financeira do Residencial Vale das Flores, envio o detalhamento das movimentações da nossa conta bancária referente ao mês de Agosto.</p>
        <p><b>Saldo Final de Julho:</b> R\$ 692,97</p>
        <p><b>AGOSTO/2026</b></p>
        <ul>
            <li><b>Entradas (Arrecadação de Taxas):</b> Recebimentos das cotas regulares e do lote unificado.</li>
            <li><b>Saídas (Contas de Consumo e Internet):</b> R\$ 327,07 (Equatorial Energia: R\$ 227,08 | Chapanet: R\$ 99,99).</li>
            <li><b>Saídas (Prestadores de Serviço):</b> R\$ 4.082,46 (Jean Pierre: R\$ 3.150,00 | Manoel Renato: R\$ 632,46 | Tiago Ribeiro: R\$ 300,00).</li>
            <li><b>Saídas (Materiais e Insumos):</b> R\$ 177,11 (Mateus Supermercados, SM Pontes, KL Sousa, Raimunda Moraes).</li>
            <li><i>Nota da Gestão:</i> Excepcionalmente neste mês de agosto, não houve a retirada da remuneração do síndico em prol do caixa do condomínio.</li>
        </ul>
        <p><b>Saldo Final de Agosto:</b> R\$ 2.908,63</p>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("📄 Relatório Financeiro - Julho/2026", expanded=False):
        st.markdown(r"""
        <div class="relatorio-box">
        <h4>Assunto: Relatório Financeiro Mensal</h4>
        <p>Para garantirmos a transparência total da nossa gestão e mantermos todos informados sobre a saúde financeira do Residencial Vale das Flores, envio o detalhamento das movimentações da nossa conta bancária referente ao mês de Julho.</p>
        <p><b>Saldo Final de Junho:</b> R\$ 2.110,47</p>
        <p><b>JULHO/2026</b></p>
        <ul>
            <li><b>Entradas (Arrecadação de Taxas):</b> Recebimentos das cotas regulares e do lote unificado.</li>
            <li><b>Saídas (Contas de Consumo):</b> R\$ 270,41 (Equatorial Energia).</li>
            <li><b>Saídas (Prestadores de Serviço):</b> R\$ 5.180,00 (Jean Pierre: R\$ 3.150,00 | Fernando Coelho: R\$ 1.300,00 - eletricista / bomba | Luiz Mendes: R\$ 300,00 | Manoel Renato: R\$ 250,00 | Geraldo da Conceição: R\$ 180,00).</li>
            <li><b>Saídas (Materiais e Insumos):</b> R\$ 1.999,99 (FV Material de Construção, RG Sousa). Destinado à manutenção da bomba de água/poço.</li>
            <li><i>Nota da Gestão:</i> Excepcionalmente neste mês de Julho, não houve a retirada da remuneração do síndico em prol do caixa do condomínio.</li>
        </ul>
        <p><b>Saldo Final de Julho:</b> R\$ 692,97</p>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  TELA: LANÇAR MOVIMENTAÇÃO (COM IMPORTAÇÃO)
# ─────────────────────────────────────────────
elif escolha == "➕ Lançar Movimentação":
    st.markdown('<div class="page-title">Lançar Movimentação</div>', unsafe_allow_html=True)
    aba_manual, aba_planilha = st.tabs(["✍️ Lançamento Manual / Ajuste", "📥 Importar Planilha"])
    
    with aba_manual:
        st.info("💡 **Dica:** Para atualizar manualmente o valor que está no banco, utilize a categoria **'Ajuste de Saldo (Manual)'**. Escolha 'Entrada' para adicionar fundos ou 'Saída' para retirar.")
        with st.form("form_lancamento", clear_on_submit=True):
            col_f1, col_f2 = st.columns(2)
            desc   = col_f1.text_input("Descrição (Ex: Ajuste de saldo inicial, ou Compra material)")
            val_f  = col_f1.number_input("Valor (R$)", min_value=0.01)
            data_f = col_f1.date_input("Data")
            tipo_f = col_f2.selectbox("Tipo", ["entrada", "saida"])
            cat_f  = col_f2.selectbox("Categoria", ["Taxa Condominial", "Ajuste de Saldo (Manual)", "Manutenção", "Água/Luz", "Outros"])
            casa_f = col_f2.selectbox("Casa pagadora (Se Taxa Condominial)", ["Não se aplica"] + [f"Casa {i}" for i in range(1, TOTAL_CASAS + 1)])
            
            if st.form_submit_button("✅ Guardar"):
                if desc and val_f > 0:
                    casa_salvar = casa_f if cat_f == "Taxa Condominial" and casa_f != "Não se aplica" else None
                    supabase.table("financas").insert({"descricao": desc, "tipo": tipo_f, "categoria": cat_f, "valor": val_f, "data": str(data_f), "casa_pagadora": casa_salvar, "criado_por": str(st.session_state.user["id"])}).execute()
                    carregar_financas.clear(); st.success("Registado!"); st.rerun()

    with aba_planilha:
        st.info("💡 A sua planilha Excel ou CSV deve conter exatamente estas 5 colunas: **Data, Descricao, Categoria, Tipo, Valor**")
        arquivo = st.file_uploader("Selecione o ficheiro Excel (.xlsx) ou CSV", type=["csv", "xlsx"])
        if arquivo:
            try:
                if arquivo.name.endswith('.csv'): df_import = pd.read_csv(arquivo)
                else: df_import = pd.read_excel(arquivo)
                if st.button("🚀 Confirmar e Importar Tudo"):
                    registos = []
                    for _, row in df_import.iterrows():
                        registos.append({
                            "data": str(pd.to_datetime(row['Data']).date()),
                            "descricao": str(row['Descricao']),
                            "categoria": str(row['Categoria']),
                            "tipo": str(row['Tipo']).lower(),
                            "valor": float(row['Valor']),
                            "criado_por": str(st.session_state.user["id"])
                        })
                    supabase.table("financas").insert(registos).execute()
                    carregar_financas.clear()
                    st.success(f"{len(registos)} registos importados com sucesso!")
            except Exception as e:
                st.error(f"Erro na importação: {e}")

# ─────────────────────────────────────────────
#  TELA: GESTÃO DE BOLETOS
# ─────────────────────────────────────────────
elif escolha == "📄 Gestão de Boletos":
    st.markdown('<div class="page-title">Gestão de Boletos e Pagamentos</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Associe links de cobranças e faturas aos moradores.</div><br>', unsafe_allow_html=True)
    
    res_perfis = supabase.table("perfis").select("*").order("bloco_unidade").execute()
    
    if res_perfis.data:
        df_perfis = pd.DataFrame(res_perfis.data)
        df_perfis = df_perfis[df_perfis["bloco_unidade"].str.contains("Casa", na=False)]
        
        with st.form("form_docs"):
            opcoes = {f"{r['bloco_unidade']} — {r['nome']}": r["id"] for _, r in df_perfis.iterrows()}
            casa_sel = st.selectbox("Selecione o Morador / Casa", list(opcoes.keys()))
            
            st.markdown("---")
            st.markdown("##### 📅 Emissão do Mês Atual")
            link_bol = st.text_input("Link do Boleto do Mês (Para pagamento normal)", placeholder="Cole o link do Google Drive aqui...")
            
            st.markdown("##### 🚨 Situação de Atraso (Opcional)")
            st.info("Preencha estes campos apenas se o morador tiver dívidas antigas. Isto criará um alerta vermelho no painel dele.")
            
            col_b1, col_b2 = st.columns([1, 2])
            meses_atraso = col_b1.text_input("Meses em Atraso", placeholder="Ex: Julho e Agosto")
            link_atraso = col_b2.text_area("Links dos Boletos em Atraso (Cole um por linha ou separe por espaço)", height=68, placeholder="https://...\nhttps://...")
            
            if st.form_submit_button("💾 Guardar / Atualizar Morador"):
                updates = {}
                if link_bol: updates["link_boleto"] = "" if link_bol.lower() == "apagar" else link_bol
                if link_atraso: updates["boleto_atraso"] = "" if link_atraso.lower() == "apagar" else link_atraso
                if meses_atraso: updates["meses_atraso"] = "" if meses_atraso.lower() == "apagar" else meses_atraso
                
                if updates:
                    supabase.table("perfis").update(updates).eq("id", opcoes[casa_sel]).execute()
                    st.success("Documentos atualizados com sucesso!")
                    st.rerun()
                else:
                    st.info("Nenhum campo preenchido. (Dica: digite 'apagar' na caixa para remover um dado existente).")
        
        st.subheader("📋 Situação Atual dos Documentos")
        df_view = df_perfis.copy()
        
        if "boleto_atraso" not in df_view.columns: df_view["boleto_atraso"] = None
        if "meses_atraso" not in df_view.columns: df_view["meses_atraso"] = None
            
        df_view["link_boleto"] = df_view["link_boleto"].apply(lambda x: "✅ Anexado" if pd.notnull(x) and x else "❌")
        df_view["boleto_atraso"] = df_view.apply(lambda row: f"🚨 {row['meses_atraso']}" if pd.notnull(row['boleto_atraso']) and row['boleto_atraso'] else "Limpo", axis=1)
        
        df_view = df_view[["bloco_unidade", "nome", "link_boleto", "boleto_atraso"]]
        df_view.columns = ["Casa", "Morador", "Boleto do Mês", "Situação de Atraso"]
        st.dataframe(df_view, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
#  TELA: CADASTRO E CAMERAS
# ─────────────────────────────────────────────
elif escolha == "👥 Cadastrar Morador":
    st.markdown('<div class="page-title">Cadastrar Morador</div>', unsafe_allow_html=True)
    with st.form("form_cadastro", clear_on_submit=True):
        col_c1, col_c2 = st.columns(2)
        nome_m  = col_c1.text_input("Nome completo")
        cpf_m   = col_c1.text_input("CPF (Servirá de Login e Senha)")
        bloco_m = col_c2.selectbox("Casa", [f"Casa {i}" for i in range(1, TOTAL_CASAS + 1)])
        funcao_m = col_c2.selectbox("Papel", ["condomino", "sindico"])
        
        if st.form_submit_button("👤 Cadastrar"):
            if nome_m and cpf_m:
                try:
                    clean_cpf = ''.join(filter(str.isdigit, cpf_m))
                    novo_id = str(uuid.uuid4())
                    
                    supabase.table("perfis").insert({
                        "id": novo_id,
                        "nome": nome_m,
                        "bloco_unidade": bloco_m,
                        "funcao": funcao_m,
                        "login": clean_cpf,
                        "senha": clean_cpf
                    }).execute()
                    st.success(f"✅ {nome_m} cadastrado com sucesso! Login e Senha são o CPF.")
                except Exception as e: 
                    st.error(f"Erro ao cadastrar: {e}")
            else: 
                st.warning("Preencha todos os campos.")

elif escolha == "📹 Câmeras Ao Vivo":
    st.markdown('<div class="page-title">Câmeras Ao Vivo</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Monitorização em tempo real (YouTube)</div><br>', unsafe_allow_html=True)
    
    if funcao == "sindico":
        with st.expander("⚙️ Gerir Câmeras (Área do Síndico)", expanded=False):
            with st.form("form_camera", clear_on_submit=True):
                col_cam1, col_cam2 = st.columns(2)
                nome_cam = col_cam1.text_input("Nome/Local da Câmera (ex: Portaria Principal)")
                link_cam = col_cam2.text_input("Link do YouTube")
                
                if st.form_submit_button("➕ Adicionar Câmera"):
                    if nome_cam and link_cam:
                        video_id = ""
                        if "v=" in link_cam: video_id = link_cam.split("v=")[1][:11]
                        elif "youtu.be/" in link_cam: video_id = link_cam.split("youtu.be/")[1][:11]
                        
                        if video_id:
                            embed_url = f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=1"
                            novo_id_cam = str(uuid.uuid4())
                            supabase.table("cameras").insert({"id": novo_id_cam, "nome_camera": nome_cam, "link_stream": embed_url}).execute()
                            st.success("Câmera adicionada!")
                            st.rerun()
                        else:
                            st.error("Link do YouTube inválido.")
                    else:
                        st.warning("Preencha o nome e o link.")
            
            if st.button("🗑️ Remover todas as câmeras", type="primary"):
                res_cam = supabase.table("cameras").select("id").execute()
                for c in res_cam.data:
                    supabase.table("cameras").delete().eq("id", c["id"]).execute()
                st.success("Câmeras removidas!")
                st.rerun()

    res_cameras = supabase.table("cameras").select("*").order("criado_em").execute()
    
    if res_cameras.data:
        cols = st.columns(2)
        for i, cam in enumerate(res_cameras.data):
            with cols[i % 2]:
                st.markdown(f"**{cam['nome_camera']}**")
                st.markdown(f'''
                    <iframe width="100%" height="300" src="{cam['link_stream']}" 
                    title="Câmera {cam['nome_camera']}" frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                    allowfullscreen style="border-radius: 12px; margin-bottom: 20px; border: 2px solid #E2E8F0;">
                    </iframe>
                ''', unsafe_allow_html=True)
    else:
        st.info("Nenhuma câmera configurada no momento. O síndico precisa adicionar os links.")
