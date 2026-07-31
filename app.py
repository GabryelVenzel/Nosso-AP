import streamlit as st
import pandas as pd
from datetime import date

# 1. Configuração da página e CSS Customizado
st.set_page_config(page_title="Te Amo Muito - Nosso AP", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1 { text-align: center; margin-bottom: 2rem; }
    </style>
""", unsafe_allow_html=True)

# 2. Inicialização do estado (sessão)
if 'gabryel' not in st.session_state: st.session_state.gabryel = 0.0
if 'julia' not in st.session_state: st.session_state.julia = 0.0
if 'emprestimo_pago' not in st.session_state: st.session_state.emprestimo_pago = 0.0

if 'parcelas' not in st.session_state:
    # Valores extraídos do PDF da Caixa (36 meses)
    caixa_valores = [
        189.91, 213.55, 252.95, 300.23, 347.51, 402.67, 457.84, 513.00, 576.04, 646.96, 741.52, 796.69,
        851.85, 907.01, 970.05, 1033.09, 1111.90, 1190.70, 1269.50, 1316.78, 1364.06, 1411.35, 1450.75, 1490.15,
        1529.55, 1561.07, 1576.83, 1592.59, 1608.35, 1624.11, 1639.87, 1655.63, 1663.51, 1671.39, 1679.28, 1687.16
    ]
    
    start_date = date(2026, 5, 1)
    parcelas_data = []
    
    # Gerando 54 meses (De Maio/2026 até Outubro/2030 - cobre as 50 parcelas)
    for i in range(54):
        mes = (start_date.month + i - 1) % 12 + 1
        ano = start_date.year + (start_date.month + i - 1) // 12
        mes_ano = f"{mes:02d}/{ano}"

        # Lógica Bliss
        if i == 0: bliss = 3275.0           # 05/2026
        elif i == 1: bliss = 3375.0         # 06/2026 (3275 + 100 extra)
        elif i == 2: bliss = 3275.0         # 07/2026
        elif i == 3: bliss = 3275.0         # 08/2026
        else: bliss = 2522.96               # 09/2026 em diante (50 parcelas)

        # Lógica Evolução de Obra Caixa (Inicia no mês 3 que é Agosto/2026)
        if 3 <= i < 3 + 36:
            caixa = caixa_valores[i - 3]
        else:
            caixa = 0.0

        parcelas_data.append({
            "Mês/Ano": mes_ano, 
            "Entrada Bliss (R$)": bliss, 
            "Evolução Caixa (R$)": caixa, 
            "Paga": False
        })
    st.session_state.parcelas = pd.DataFrame(parcelas_data)

if 'moveis' not in st.session_state:
    st.session_state.moveis = pd.DataFrame(columns=["Item", "Valor (R$)", "Comprado"])

# 3. Cabeçalho
st.markdown("<h1>Nosso Apartamento 🏢</h1>", unsafe_allow_html=True)

# 4. Cálculos Principais
saldo_devedor = max(0.0, 20000.0 - st.session_state.emprestimo_pago)
perc_devedor = min(100.0, (st.session_state.emprestimo_pago / 20000.0) * 100) if 20000.0 else 0

# Cálculos Parcelas
df_parcelas = st.session_state.parcelas
df_parcelas['Total_Mes'] = df_parcelas['Entrada Bliss (R$)'] + df_parcelas['Evolução Caixa (R$)']
valor_total_geral = df_parcelas['Total_Mes'].sum()

pagas_df = df_parcelas[df_parcelas['Paga'] == True]
valor_total_pago = pagas_df['Total_Mes'].sum()
perc_parcelas = (valor_total_pago / valor_total_geral) * 100 if valor_total_geral > 0 else 0

# Cálculos Móveis
total_moveis_meta = st.session_state.moveis["Valor (R$)"].sum() if not st.session_state.moveis.empty else 0.0
moveis_comprados_df = st.session_state.moveis[st.session_state.moveis["Comprado"] == True] if not st.session_state.moveis.empty else pd.DataFrame()
total_moveis_comprados = moveis_comprados_df["Valor (R$)"].sum() if not moveis_comprados_df.empty else 0.0
perc_moveis = (total_moveis_comprados / total_moveis_meta * 100) if total_moveis_meta > 0 else 0.0

# 5. LINHA SUPERIOR (Progresso e Empréstimo)
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.caption("SALDO DEVEDOR (20K)")
        st.metric("Restante", f"R$ {saldo_devedor:,.2f}")
        st.progress(int(perc_devedor), text=f"{perc_devedor:.0f}% Pago")
        
    # Abater Empréstimo alinhado abaixo do Saldo Devedor
    with st.container(border=True):
        st.subheader("Abater Empréstimo", anchor=False)
        st.caption("Abate dos R$ 20.000,00 iniciais.")
        ca1, ca2 = st.columns([2, 1])
        abater = ca1.number_input("Valor pago R$", min_value=0.0, step=100.0, label_visibility="collapsed")
        if ca2.button("Lançar", use_container_width=True, type="primary"):
            st.session_state.emprestimo_pago = min(20000.0, st.session_state.emprestimo_pago + abater)
            st.rerun()

with col2:
    with st.container(border=True):
        st.caption("PARCELAS AP (BLISS + CAIXA)")
        st.metric("Total Pago", f"R$ {valor_total_pago:,.2f}", f"de R$ {valor_total_geral:,.2f}", delta_color="off")
        st.progress(int(perc_parcelas), text=f"{perc_parcelas:.1f}% Concluído")

with col3:
    with st.container(border=True):
        st.caption(f"MÓVEIS E DECORAÇÃO")
        st.metric("Comprados", f"R$ {total_moveis_comprados:,.2f}", f"Meta: R$ {total_moveis_meta:,.2f}", delta_color="off")
        st.progress(int(perc_moveis), text=f"{perc_moveis:.0f}% Adquirido")

st.write("") # Espaçamento

# 6. LINHA INFERIOR (Móveis, Reservas e Tabela)
left_col, right_col = st.columns([1, 1.8], gap="large")

with left_col:
    # CARTÃO: MÓVEIS (Movido para a esquerda)
    with st.container(border=True):
        st.subheader("Lista de Móveis e Decoração", anchor=False)
        with st.form("form_moveis", border=False):
            nome_item = st.text_input("Nome do Item", placeholder="Ex: Geladeira")
            c_val, c_btn = st.columns([2, 1])
            valor_item = c_val.number_input("Valor Est. R$", min_value=0.0, step=50.0)
            st.markdown("""<style> .stFormSubmitButton { margin-top: 1.75rem; } </style>""", unsafe_allow_html=True)
            submitted = c_btn.form_submit_button("Adicionar", use_container_width=True)
            
            if submitted and nome_item:
                novo_item = pd.DataFrame([{"Item": nome_item, "Valor (R$)": valor_item, "Comprado": False}])
                st.session_state.moveis = pd.concat([st.session_state.moveis, novo_item], ignore_index=True)
                st.rerun()
                
        if not st.session_state.moveis.empty:
            edited_moveis = st.data_editor(
                st.session_state.moveis,
                hide_index=True,
                num_rows="dynamic",
                use_container_width=True,
                height=300
            )
            if not edited_moveis.equals(st.session_state.moveis):
                st.session_state.moveis = edited_moveis
                st.rerun()

with right_col:
    c_reserva, c_tabela = st.columns([1, 1.5])
    
    with c_reserva:
        # CARTÃO: GESTÃO DE RESERVAS (Movido para a direita)
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
            
            st.info(f"**Saldo:** R$ {total_casal:,.2f}\n\n**Cobertura:** {meses_cobertura} meses inteiros")
            st.divider()
            
            st.write("**👦🏻 Gabryel**")
            st.metric("Saldo", f"R$ {st.session_state.gabryel:,.2f}", label_visibility="collapsed")
            cg1, cg2, cg3 = st.columns([2, 1, 1])
            novo_valor_g = cg1.number_input("Valor", step=100.0, key="in_g", label_visibility="collapsed", placeholder="R$")
            if cg2.button("➕", key="add_g", use_container_width=True): 
                st.session_state.gabryel += novo_valor_g; st.rerun()
            if cg3.button("➖", key="sub_g", use_container_width=True): 
                st.session_state.gabryel = max(0.0, st.session_state.gabryel - novo_valor_g); st.rerun()

            st.write("**👸🏻 Júlia**")
            st.metric("Saldo", f"R$ {st.session_state.julia:,.2f}", label_visibility="collapsed")
            cj1, cj2, cj3 = st.columns([2, 1, 1])
            novo_valor_j = cj1.number_input("Valor", step=100.0, key="in_j", label_visibility="collapsed", placeholder="R$")
            if cj2.button("➕", key="add_j", use_container_width=True): 
                st.session_state.julia += novo_valor_j; st.rerun()
            if cj3.button("➖", key="sub_j", use_container_width=True): 
                st.session_state.julia = max(0.0, st.session_state.julia - novo_valor_j); st.rerun()

    with c_tabela:
        # CARTÃO: CRONOGRAMA
        with st.container(border=True):
            st.subheader("Cronograma Conjunto", anchor=False)
            st.caption("Edite os valores livremente se houver reajuste.")
            # Drop the calculation column before showing to user, it recalculates automatically
            display_df = st.session_state.parcelas.drop(columns=['Total_Mes'], errors='ignore')
            
            edited_parcelas = st.data_editor(
                display_df,
                hide_index=True,
                use_container_width=True,
                disabled=["Mês/Ano"], 
                height=450
            )
            if not edited_parcelas.equals(display_df):
                st.session_state.parcelas = edited_parcelas
                st.rerun()

# 7. PLANTA DO APARTAMENTO (Fundo da tela)
st.write("")
try:
    with st.expander("📐 Abrir Planta do Apartamento", expanded=False):
        st.image("planta.jpg", use_container_width=True)
except FileNotFoundError:
    pass
