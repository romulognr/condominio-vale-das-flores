import streamlit as st
import pandas as pd
from supabase import create_client, Client
import datetime
import uuid

# ─────────────────────────────────────────────
#  CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(page_title="Vale das Flores · Gestão", page_icon="🏡", layout="wide", initial_sidebar_state="expanded")

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
.stTextInput > div > div > input, .stNumberInput > div > div > input, .stSelectbox > div > div { border-radius: 8px !important; border: 1.5px solid #E2E8F0 !important; font-size: 14px !important; }
.stForm [data-testid="stFormSubmitButton"] > button { background: #1E3A5F !important; color: white !important; border: none !important; padding: 10px 24px !important; border-radius: 8px !important; font-weight: 600 !important; }
.badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.badge-sindico { background: #DBEAFE; color: #1E40AF; }
.badge-condomino { background: #D1FAE5; color: #065F46; }
.page-title { font-size: 26px; font-weight: 700; color: #0F1B2D; margin-bottom: 4px; }
.page-subtitle { font-size: 14px; color: #64748B; margin-bottom: 0; }
.login-btn button { background: #1E3A5F !important; color: white !important; border: none !important; border-radius: 10px !important; height: 46px !important; font-weight: 600 !important; font-size: 15px !important; width: 100%; }
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
#  AUTH (DIRETO NA TABELA PERFIS)
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

menu_options = ["📊 Dashboard", "📹 Câmeras Ao Vivo"]
if funcao == "sindico":
    menu_options += ["➕ Lançar Movimentação", "👥 Cadastrar Morador", "📄 Boletos e Comprovantes"]

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
    reserva  = df[df["categoria"] == "Fundo de Reserva"]["valor"].sum() if not df.empty else 0
    doacoes  = df[df["categoria"] == "Doações"]["valor"].sum() if not df.empty else 0
    
    df_mes    = df[(df["data"].dt.month == mes_sel) & (df["data"].dt.year == ano_sel)] if not df.empty else pd.DataFrame()
    taxas_mes = df_mes[(df_mes["categoria"] == "Taxa Condominial") & (df_mes["tipo"] == "entrada")] if not df_mes.empty else pd.DataFrame()
    
    pagaram   = min(taxas_mes["casa_pagadora"].nunique() if not taxas_mes.empty and "casa_pagadora" in taxas_mes.columns else 0, TOTAL_CASAS)
    arrec_mes = taxas_mes["valor"].sum() if not taxas_mes.empty else 0
    
    return {
        "caixa": entradas - saidas, "entradas": entradas, "saidas": saidas, "reserva": reserva, "doacoes": doacoes,
        "pagaram": pagaram, "inadimp": TOTAL_CASAS - pagaram, "pct_inadimp": ((TOTAL_CASAS - pagaram) / TOTAL_CASAS) * 100,
        "arrec_mes": arrec_mes, "pro_labore": arrec_mes * 0.10, "mes": mes_sel, "ano": ano_sel,
        "usuario_pago": casa_logada in taxas_mes["casa_pagadora"].tolist() if not taxas_mes.empty and "casa_pagadora" in taxas_mes.columns else False
    }

# ─────────────────────────────────────────────
#  TELA: DASHBOARD
# ─────────────────────────────────────────────
if escolha == "📊 Dashboard":
    st.markdown('<div class="page-title">Painel Financeiro</div><div class="page-subtitle">Residencial Vale das Flores</div><br>', unsafe_allow_html=True)
    df = carregar_financas()
    if df.empty: 
        st.info("Nenhuma movimentação registada ainda.")
        st.stop()

    hoje = datetime.date.today()
    periodo_atual = f"{hoje.month:02d}/{hoje.year}"
    periodos = df['data'].dt.to_period('M').unique().tolist()
    periodos_str = sorted([f"{p.month:02d}/{p.year}" for p in periodos], reverse=True)
    if periodo_atual not in periodos_str:
        periodos_str.insert(0, periodo_atual)
    
    col_sel1, col_sel2 = st.columns([1, 3])
    with col_sel1:
        periodo_selecionado = st.selectbox("📅 Selecione o Mês de Referência:", periodos_str)
    
    mes_str, ano_str = periodo_selecionado.split("/")
    mes_sel, ano_sel = int(mes_str), int(ano_str)
    
    kpi = calcular_kpis(df, perfil["bloco_unidade"], mes_sel, ano_sel)

    if funcao == "condomino":
        st.markdown(f"### 📌 A Minha Unidade (Referência: {periodo_selecionado})")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if not kpi["usuario_pago"]:
                st.error(f"⚠️ A taxa de {periodo_selecionado} da **{perfil['bloco_unidade']}** está em aberto.")
                if perfil.get("link_boleto"):
                    st.markdown(f'<a href="{perfil["link_boleto"]}" target="_blank"><button style="background:#EF4444;color:white;border:none;padding:10px 20px;border-radius:8px;font-weight:bold;width:100%;cursor:pointer;">📥 Descarregar Boleto</button></a>', unsafe_allow_html=True)
            else:
                st.success(f"✅ Pagamento de {periodo_selecionado} regularizado.")
        with col_c2:
            st.info("Comprovativo de Pagamento (Anexado pelo Síndico)")
            if perfil.get("link_comprovante"):
                st.markdown(f'<a href="{perfil["link_comprovante"]}" target="_blank"><button style="background:#10B981;color:white;border:none;padding:10px 20px;border-radius:8px;font-weight:bold;width:100%;cursor:pointer;">👁️ Ver Comprovativo</button></a>', unsafe_allow_html=True)
            else:
                st.caption("O síndico ainda não anexou o comprovativo deste mês.")
        st.markdown("---")

    section_header("💰", "Resumo do Caixa (Histórico Completo)")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(metric_card("Saldo", fmt_brl(kpi["caixa"]), "", "green"), unsafe_allow_html=True)
    c2.markdown(metric_card("Entradas", fmt_brl(kpi["entradas"]), "", "blue"), unsafe_allow_html=True)
    c3.markdown(metric_card("Saídas", fmt_brl(kpi["saidas"]), "", "red"), unsafe_allow_html=True)
    c4.markdown(metric_card("Reserva", fmt_brl(kpi["reserva"]), "", "purple"), unsafe_allow_html=True)

    section_header("📉", f"Situação de Adimplência — {periodo_selecionado}")
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(metric_card("Adimplentes", f"{kpi['pagaram']}/{TOTAL_CASAS}", "", "green"), unsafe_allow_html=True)
    m2.markdown(metric_card("Inadimplentes", f"{kpi['inadimp']} casas", f"{kpi['pct_inadimp']:.1f}%", "red"), unsafe_allow_html=True)
    m3.markdown(metric_card("Doações", fmt_brl(kpi["doacoes"]), "Mês atual", "amber"), unsafe_allow_html=True)
    m4.markdown(metric_card("Pró-Labore (10%)", fmt_brl(kpi["pro_labore"]), "Mês atual", "purple"), unsafe_allow_html=True)

    section_header("📋", f"Movimentações do Mês ({periodo_selecionado})")
    df_exib = df[(df["data"].dt.month == mes_sel) & (df["data"].dt.year == ano_sel)][["data", "descricao", "categoria", "tipo", "valor"]].copy()
    
    if not df_exib.empty:
        df_exib["data"] = df_exib["data"].dt.strftime("%d/%m/%Y")
        df_exib["valor"] = df_exib["valor"].map(fmt_brl)
        st.dataframe(df_exib, use_container_width=True, hide_index=True)
        
        csv = df_exib.to_csv(index=False).encode('utf-8')
        st.download_button(label=f"📄 Descarregar Relatório de {periodo_selecionado} (CSV)", data=csv, file_name=f"relatorio_{mes_sel}_{ano_sel}.csv", mime="text/csv")
    else:
        st.info("Nenhuma movimentação registada para o mês selecionado.")

# ─────────────────────────────────────────────
#  TELA: LANÇAR MOVIMENTAÇÃO (COM IMPORTAÇÃO)
# ─────────────────────────────────────────────
elif escolha == "➕ Lançar Movimentação":
    st.markdown('<div class="page-title">Lançar Movimentação</div>', unsafe_allow_html=True)
    aba_manual, aba_planilha = st.tabs(["✍️ Lançamento Manual", "📥 Importar Planilha"])
    
    with aba_manual:
        with st.form("form_lancamento", clear_on_submit=True):
            col_f1, col_f2 = st.columns(2)
            desc   = col_f1.text_input("Descrição")
            val_f  = col_f1.number_input("Valor (R$)", min_value=0.01)
            data_f = col_f1.date_input("Data")
            tipo_f = col_f2.selectbox("Tipo", ["entrada", "saida"])
            cat_f  = col_f2.selectbox("Categoria", ["Taxa Condominial", "Doações", "Manutenção", "Água/Luz", "Fundo de Reserva", "Pró-Labore Síndico", "Outros"])
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
                st.write("Pré-visualização dos dados a importar:")
                st.dataframe(df_import.head())
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
#  TELA: BOLETOS E COMPROVANTES
# ─────────────────────────────────────────────
elif escolha == "📄 Boletos e Comprovantes":
    st.markdown('<div class="page-title">Boletos e Comprovantes</div>', unsafe_allow_html=True)
    res_perfis = supabase.table("perfis").select("id, nome, bloco_unidade, link_boleto, link_comprovante").order("bloco_unidade").execute()
    if res_perfis.data:
        df_perfis = pd.DataFrame(res_perfis.data)
        df_perfis = df_perfis[df_perfis["bloco_unidade"].str.contains("Casa", na=False)]
        
        with st.form("form_docs"):
            opcoes = {f"{r['bloco_unidade']} — {r['nome']}": r["id"] for _, r in df_perfis.iterrows()}
            casa_sel = st.selectbox("Selecione o Morador / Casa", list(opcoes.keys()))
            col_b1, col_b2 = st.columns(2)
            link_bol = col_b1.text_input("Link do Boleto (Deixe em branco para não alterar)")
            link_cmp = col_b2.text_input("Link do Comprovativo de Pagamento")
            
            if st.form_submit_button("💾 Guardar Links"):
                updates = {}
                if link_bol: updates["link_boleto"] = link_bol
                if link_cmp: updates["link_comprovante"] = link_cmp
                if updates:
                    supabase.table("perfis").update(updates).eq("id", opcoes[casa_sel]).execute()
                    st.success("Documentos atualizados!"); st.rerun()
                else:
                    st.warning("Preencha pelo menos um dos links.")
        
        st.subheader("📋 Situação Atual dos Documentos")
        df_view = df_perfis[["bloco_unidade", "nome", "link_boleto", "link_comprovante"]].copy()
        df_view["link_boleto"] = df_view["link_boleto"].apply(lambda x: "✅ Anexado" if pd.notnull(x) and x else "❌ Pendente")
        df_view["link_comprovante"] = df_view["link_comprovante"].apply(lambda x: "✅ Anexado" if pd.notnull(x) and x else "❌ Pendente")
        df_view.columns = ["Casa", "Morador", "Status Boleto", "Status Comprovativo"]
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
                    # Gera um UUID válido para evitar conflito com a coluna UUID do Supabase
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
    st.info("Módulo de câmeras ativo. Adicione links via painel do síndico.")
