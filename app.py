import streamlit as st
import pandas as pd
import requests
from datetime import date

# --- CONFIGURAÇÕES DO JSONBIN ---
API_KEY = "$2a$10$90et8fAGUxXj6yB/HPBhoOkxZUOGpyFIxI/sfxx1sL4HEKI0dnuD."
BIN_ID = "6a6bfaeeda38895dfea6bd89"
URL_JSONBIN = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS = {
    "X-Master-Key": API_KEY,
    "Content-Type": "application/json"
}

def salvar_nuvem():
    """Salva o estado atual no JSONBin"""
    dados = {
        "gabryel": st.session_state.gabryel,
        "julia": st.session_state.julia,
        "emprestimo_pago": st.session_state.emprestimo_pago,
        "parcelas": st.session_state.parcelas.to_dict('records'),
        "moveis": st.session_state.moveis.to_dict('records')
    }
    try:
        requests.put(URL_JSONBIN, json=dados, headers=HEADERS)
    except Exception as e:
        st.error(f"Erro ao salvar na nuvem: {e}")

# 1. Configuração da página e CSS Customizado
st.set_page_config(page_title="Te Amo Muito - Nosso AP", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1 { text-align: center; margin-bottom: 2rem; }
    </style>
""", unsafe_allow_html=True)

# 2. Leitura da Nuvem na inicialização
if 'dados_carregados' not in st.session_state:
    try:
        req = requests.get(URL_JSONBIN, headers=HEADERS)
        nuvem = req.json()['record']
        
        st.session_state.gabryel = nuvem.get('gabryel', 0.0)
        st.session_state.julia = nuvem.get('julia', 0.0)
        st.session_state.emprestimo_pago = nuvem.get('emprestimo_pago', 0.0)
        
        # Carrega Móveis
        moveis_nuvem = nuvem.get('moveis', [])
        if moveis_nuvem:
            st.session_state.moveis = pd.DataFrame(moveis_nuvem)
        else:
            st.session_state.moveis = pd.DataFrame(columns=["Item", "Valor (R$)", "Comprado"])
            
        # Carrega Parcelas (se a nuvem estiver vazia, recria do zero)
        parcelas_nuvem = nuvem.get('parcelas', [])
        if parcelas_nuvem:
            st.session_state.parcelas = pd.DataFrame(parcelas_nuvem)
        else:
            caixa_valores = [
                189.91, 213.55, 252.95, 300.23, 347.51, 402.67, 457.84, 513.00, 576.04, 646.96, 741.52, 796.69,
                851.85, 907.01, 970.05, 1033.09, 1111.90, 1190.70, 1269.50, 1316.78, 1364.06, 1411.35, 1450.75, 1490.15,
                1529.55, 1561.07, 1576.83, 1592.59, 1608.35, 1624.11, 1639.87, 1655.63, 1663.51, 1671.39, 1679.28, 1687.16
            ]
            start_date = date(2026, 5, 1)
            parcelas_data = []
            for i in range(54):
                mes = (start_date.month + i - 1) % 12 + 1
                ano = start_date.year + (start_date.month + i - 1) // 12
                mes_ano = f"{mes:02d}/{ano}"
                
                if i == 0: bliss = 3275.0
                elif i == 1: bliss = 3375.0
                elif i == 2: bliss = 3275.0
                elif i == 3: bliss = 3275.0
                else: bliss = 2522.96

                caixa = caixa_valores[i - 3] if 3 <= i < 3 + 36 else 0.0

                parcelas_data.append({
                    "Mês/Ano": mes_ano, 
                    "Entrada Bliss (R$)": bliss, 
                    "Evolução Caixa (R$)": caixa, 
                    "Outros (R$)": 0.0, 
                    "Paga": False
                })
            st.session_state.parcelas = pd.DataFrame(parcelas_data)
            
        st.session_state.dados_carregados = True
    except Exception as e:
        st.error(f"Erro ao conectar com o banco de dados. Verifique suas chaves. Erro: {e}")

# 3. Cabeçalho
st.markdown("<h1>Nosso Apartamento 🏢</h1>", unsafe_allow_html=True)

# 4. Cálculos Principais
saldo_devedor = max(0.0, 20000.0 - st.session_state.emprestimo_pago)
perc_devedor = min(100.0, (st.session_state.emprestimo_pago / 20000.0) * 100) if 20000.0 else 0

df_parcelas = st.session_state.parcelas
if 'Outros (R$)' not in df_parcelas.columns:
    df_parcelas['Outros (R$)'] = 0.0
    st.session_state.parcelas = df_parcelas

df_parcelas['Total_Mes'] = df_parcelas['Entrada Bliss (R$)'] + df_parcelas['Evolução Caixa (R$)'] + df_parcelas['Outros (R$)']
valor_total_geral = df_parcelas['Total_Mes'].sum()

pagas_df = df_parcelas[df_parcelas['Paga'] == True]
valor_total_pago = pagas_df['Total_Mes'].sum()
perc_parcelas = (valor_total_pago / valor_total_geral) * 100 if valor_total_geral > 0 else 0

total_moveis_meta = st.session_state.moveis["Valor (R$)"].sum() if not st.session_state.moveis.empty else 0.0
moveis_comprados_df = st.session_state.moveis[st.session_state.moveis["Comprado"] == True] if not st.session_state.moveis.empty else pd.DataFrame()
total_moveis_comprados = moveis_comprados_df["Valor (R$)"].sum() if not moveis_comprados_df.empty else 0.0
perc_moveis = (total_moveis_comprados / total_moveis_meta * 100) if total_moveis_meta > 0 else 0.0

ALTURA_CARDS = 245 

# 5. ESTRUTURA DE COLUNAS (2.5 para a esquerda ficar bem larga, 1 para a direita ficar estreita)
left_col, right_col = st.columns([2.5, 1], gap="large")

with left_col:
    # 1. PROGRESSO PARCELAS E SALDO DEVEDOR COMBINADO (Esquerda)
    top_l1, top_l2 = st.columns(2)
    
    with top_l1:
        with st.container(height=ALTURA_CARDS, border=True):
            st.caption("PARCELAS (BLISS + CAIXA + OUTROS)")
            st.metric("Total Pago", f"R$ {valor_total_pago:,.2f}", f"de R$ {valor_total_geral:,.2f}", delta_color="off")
            st.progress(int(perc_parcelas), text=f"{perc_parcelas:.1f}% Concluído")
            
    with top_l2:
        # Saldo Devedor e Abater Juntos
        with st.container(height=ALTURA_CARDS, border=True):
            st.caption("EMPRÉSTIMO ENTRADA (20 MIL REAIS)")
            st.metric("Restante", f"R$ {saldo_devedor:,.2f}")
            st.progress(int(perc_devedor), text=f"{perc_devedor:.0f}% Pago")
            
            st.divider() # Linha divisória fina
            
            ca1, ca2 = st.columns([2, 1])
            abater = ca1.number_input("Abater valor R$", min_value=0.0, step=100.0, label_visibility="collapsed", placeholder="Valor R$")
            if ca2.button("Lançar", use_container_width=True, type="primary"):
                st.session_state.emprestimo_pago = min(20000.0, st.session_state.emprestimo_pago + abater)
                salvar_nuvem()
                st.rerun()

    # 2. GESTÃO DE RESERVAS (Esquerda)
    with st.container(border=True):
        st.subheader("Gestão de Reservas", anchor=False)
        total_casal = st.session_state.gabryel + st.session_state.julia
        
        # Cálculo exato de meses de cobertura
        df_nao_pagas = df_parcelas[df_parcelas['Paga'] == False]
        saldo_restante = total_casal
        meses_cobertura = 0
        
        for _, row in df_nao_pagas.iterrows():
            custo_mes = row['Total_Mes']
            if custo_mes > 0 and saldo_restante >= custo_mes:
                saldo_restante -= custo_mes
                meses_cobertura += 1
            else:
                break
        
        # Estrutura Horizontal
        col_res1, col_res2, col_res3 = st.columns([1.2, 1, 1], gap="medium")
        
        with col_res1:
            # Destaque customizado para o Saldo e Meses
            st.markdown(f"""
                <div style="background-color: rgba(2, 132, 199, 0.1); padding: 20px; border-radius: 12px; text-align: center; border: 1px solid rgba(2, 132, 199, 0.2); height: 100%; display: flex; flex-direction: column; justify-content: center;">
                    <p style="margin: 0; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; color: #475569;">Saldo Total</p>
                    <h1 style="margin: 5px 0; color: #0284c7; font-size: 2.2rem; line-height: 1;">R$ {total_casal:,.2f}</h1>
                    <div>
                        <span style="background-color: #0284c7; color: white; padding: 4px 14px; border-radius: 20px; font-size: 0.95rem; font-weight: bold; display: inline-block; margin-top: 8px;">
                            {meses_cobertura} meses seguros
                        </span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        with col_res2:
            st.write("**👦🏻 Gabryel**")
            st.metric("Saldo", f"R$ {st.session_state.gabryel:,.2f}", label_visibility="collapsed")
            cg1, cg2, cg3 = st.columns([2, 1, 1])
            novo_valor_g = cg1.number_input("Valor Gabryel", step=100.0, key="in_g", label_visibility="collapsed", placeholder="R$")
            if cg2.button("➕", key="add_g", use_container_width=True): 
                st.session_state.gabryel += novo_valor_g; salvar_nuvem(); st.rerun()
            if cg3.button("➖", key="sub_g", use_container_width=True): 
                st.session_state.gabryel = max(0.0, st.session_state.gabryel - novo_valor_g); salvar_nuvem(); st.rerun()

        with col_res3:
            st.write("**👸🏻 Júlia**")
            st.metric("Saldo", f"R$ {st.session_state.julia:,.2f}", label_visibility="collapsed")
            cj1, cj2, cj3 = st.columns([2, 1, 1])
            novo_valor_j = cj1.number_input("Valor Júlia", step=100.0, key="in_j", label_visibility="collapsed", placeholder="R$")
            if cj2.button("➕", key="add_j", use_container_width=True): 
                st.session_state.julia += novo_valor_j; salvar_nuvem(); st.rerun()
            if cj3.button("➖", key="sub_j", use_container_width=True): 
                st.session_state.julia = max(0.0, st.session_state.julia - novo_valor_j); salvar_nuvem(); st.rerun()

    # 3. CRONOGRAMA CONJUNTO (Esquerda)
    with st.container(border=True):
        st.subheader("Cronograma de Pagamentos", anchor=False)
        st.caption("A cobertura de meses na Gestão de Reservas é calculada automaticamente baseada nos valores em aberto desta tabela.")
        display_df = st.session_state.parcelas.drop(columns=['Total_Mes'], errors='ignore')
        
        edited_parcelas = st.data_editor(
            display_df,
            hide_index=True,
            use_container_width=True,
            disabled=["Mês/Ano"], 
            height=400
        )
        if not edited_parcelas.equals(display_df):
            st.session_state.parcelas = edited_parcelas
            salvar_nuvem()
            st.rerun()

with right_col:
    # 4. MÓVEIS (Progresso movido para a estrema direita)
    with st.container(height=ALTURA_CARDS, border=True):
        st.caption(f"META DE MÓVEIS")
        st.metric("Comprados", f"R$ {total_moveis_comprados:,.2f}", f"Meta: R$ {total_moveis_meta:,.2f}", delta_color="off")
        st.progress(int(perc_moveis), text=f"{perc_moveis:.0f}% Adquirido")
        
    # 5. LISTA DE MÓVEIS (Estrema direita)
    with st.container(border=True):
        st.subheader("Móveis e Decoração", anchor=False)
        with st.form("form_moveis", border=False):
            nome_item = st.text_input("Nome do Item", placeholder="Ex: Geladeira")
            c_val, c_btn = st.columns([2, 1])
            valor_item = c_val.number_input("Valor Est. R$", min_value=0.0, step=50.0)
            st.markdown("""<style> .stFormSubmitButton { margin-top: 1.75rem; } </style>""", unsafe_allow_html=True)
            submitted = c_btn.form_submit_button("Adicionar", use_container_width=True)
            
            if submitted and nome_item:
                novo_item = pd.DataFrame([{"Item": nome_item, "Valor (R$)": valor_item, "Comprado": False}])
                st.session_state.moveis = pd.concat([st.session_state.moveis, novo_item], ignore_index=True)
                salvar_nuvem()
                st.rerun()
                
        if not st.session_state.moveis.empty:
            edited_moveis = st.data_editor(
                st.session_state.moveis,
                hide_index=True,
                num_rows="dynamic",
                use_container_width=True,
                height=550
            )
            if not edited_moveis.equals(st.session_state.moveis):
                st.session_state.moveis = edited_moveis
                salvar_nuvem()
                st.rerun()

# 6. PLANTA DO APARTAMENTO
st.write("")
try:
    with st.expander("📐 Abrir Planta do Apartamento", expanded=False):
        st.image("planta.jpg", use_container_width=True)
except FileNotFoundError:
    pass
