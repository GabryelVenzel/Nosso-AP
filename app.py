import streamlit as st
import pandas as pd
from datetime import date

# 1. Configuração da página e CSS Customizado
st.set_page_config(page_title="Te Amo Muito - Nosso AP", layout="wide", initial_sidebar_state="collapsed")

# CSS para reduzir os espaços em branco padrão do Streamlit e centralizar o título
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1 { text-align: center; margin-bottom: 2rem; }
    </style>
""", unsafe_allow_html=True)

# 2. Inicialização do estado (sessão) - MANTIDO
if 'gabryel' not in st.session_state: st.session_state.gabryel = 0.0
if 'julia' not in st.session_state: st.session_state.julia = 0.0
if 'emprestimo_pago' not in st.session_state: st.session_state.emprestimo_pago = 0.0

if 'parcelas' not in st.session_state:
    start_date = date(2026, 5, 30)
    parcelas_data = []
    for i in range(39):
        mes = (start_date.month + i - 1) % 12 + 1
        ano = start_date.year + (start_date.month + i - 1) // 12
        dia = 28 if mes == 2 else 30
        data_venc = date(ano, mes, min(dia, 31))
        parcelas_data.append({"ID": f"#{str(i+1).zfill(2)}", "Data": data_venc.strftime("%d/%m/%Y"), "Valor (R$)": 3275.00, "Paga": False})
    st.session_state.parcelas = pd.DataFrame(parcelas_data)

if 'moveis' not in st.session_state:
    st.session_state.moveis = pd.DataFrame(columns=["Item", "Valor (R$)", "Comprado"])

# 3. Cabeçalho (Sem a imagem gigante)
st.markdown("<h1>Nosso Apartamento 🏢</h1>", unsafe_allow_html=True)

# 4. Cálculos Principais
VALOR_PARCELA = 3275.0
saldo_devedor = max(0.0, 20000.0 - st.session_state.emprestimo_pago)
perc_devedor = min(100.0, (st.session_state.emprestimo_pago / 20000.0) * 100) if 20000.0 else 0

pagas_df = st.session_state.parcelas[st.session_state.parcelas['Paga'] == True]
num_pagas = len(pagas_df)
valor_total_pago = num_pagas * VALOR_PARCELA
perc_parcelas = (num_pagas / 39.0) * 100

total_moveis_meta = st.session_state.moveis["Valor (R$)"].sum() if not st.session_state.moveis.empty else 0.0
moveis_comprados_df = st.session_state.moveis[st.session_state.moveis["Comprado"] == True] if not st.session_state.moveis.empty else pd.DataFrame()
total_moveis_comprados = moveis_comprados_df["Valor (R$)"].sum() if not moveis_comprados_df.empty else 0.0
perc_moveis = (total_moveis_comprados / total_moveis_meta * 100) if total_moveis_meta > 0 else 0.0

# 5. Progresso Triplo (Agora dentro de cartões)
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.caption("SALDO DEVEDOR (20K)")
        st.metric("Restante", f"R$ {saldo_devedor:,.2f}")
        st.progress(int(perc_devedor), text=f"{perc_devedor:.0f}% Pago")

with col2:
    with st.container(border=True):
        st.caption(f"PARCELAS AP (Total pago: R$ {valor_total_pago:,.2f})")
        st.metric("Progresso", f"{num_pagas} de 39 pagas")
        st.progress(int(perc_parcelas), text=f"{perc_parcelas:.0f}% Concluído")

with col3:
    with st.container(border=True):
        st.caption(f"MÓVEIS E DECORAÇÃO (Comprados: R$ {total_moveis_comprados:,.2f})")
        st.metric("Meta Total", f"R$ {total_moveis_meta:,.2f}")
        st.progress(int(perc_moveis), text=f"{perc_moveis:.0f}% Adquirido")

st.write("") # Espaçamento

# 6. Layout Principal Dividido
left_col, right_col = st.columns([1, 1.8], gap="large")

with left_col:
    # CARTÃO: GESTÃO DE RESERVAS
    with st.container(border=True):
        st.subheader("Gestão de Reservas", anchor=False)
        total_casal = st.session_state.gabryel + st.session_state.julia
        meses_cobertura = int(total_casal / VALOR_PARCELA)
        
        # Destaque para o saldo total
        st.info(f"**Saldo Total:** R$ {total_casal:,.2f}  |  **Cobertura:** {meses_cobertura} meses")
        st.divider()
        
        # Gabryel
        st.write("**👦🏻 Gabryel Venzel**")
        st.metric("Saldo Atual", f"R$ {st.session_state.gabryel:,.2f}", label_visibility="collapsed")
        cg1, cg2, cg3 = st.columns([2, 1, 1])
        novo_valor_g = cg1.number_input("Valor", step=100.0, key="in_g", label_visibility="collapsed", placeholder="R$")
        if cg2.button("➕", key="add_g", help="Adicionar", use_container_width=True): 
            st.session_state.gabryel += novo_valor_g
            st.rerun()
        if cg3.button("➖", key="sub_g", help="Subtrair", use_container_width=True): 
            st.session_state.gabryel = max(0.0, st.session_state.gabryel - novo_valor_g)
            st.rerun()

        st.write("") # Espaço

        # Júlia
        st.write("**👸🏻 Júlia Navarro**")
        st.metric("Saldo Atual", f"R$ {st.session_state.julia:,.2f}", label_visibility="collapsed")
        cj1, cj2, cj3 = st.columns([2, 1, 1])
        novo_valor_j = cj1.number_input("Valor", step=100.0, key="in_j", label_visibility="collapsed", placeholder="R$")
        if cj2.button("➕", key="add_j", help="Adicionar", use_container_width=True): 
            st.session_state.julia += novo_valor_j
            st.rerun()
        if cj3.button("➖", key="sub_j", help="Subtrair", use_container_width=True): 
            st.session_state.julia = max(0.0, st.session_state.julia - novo_valor_j)
            st.rerun()

    # Imagem da planta menor e mais elegante
    try:
        with st.expander("Ver Planta do Apartamento", expanded=False):
            st.image("planta.jpg", use_container_width=True)
    except FileNotFoundError:
        pass

with right_col:
    # CARTÃO: ABATER EMPRÉSTIMO
    with st.container(border=True):
        st.subheader("Abater Empréstimo de Entrada", anchor=False)
        st.caption("O valor será subtraído dos R$ 20.000,00 iniciais.")
        
        ca1, ca2 = st.columns([3, 1])
        abater = ca1.number_input("Valor pago R$", min_value=0.0, step=100.0, label_visibility="collapsed")
        if ca2.button("Lançar Pagamento", use_container_width=True, type="primary"):
            st.session_state.emprestimo_pago = min(20000.0, st.session_state.emprestimo_pago + abater)
            st.rerun()
            
    # CARTÃO: CRONOGRAMA
    with st.container(border=True):
        st.subheader("Cronograma Bliss (30/05/2026)", anchor=False)
        edited_parcelas = st.data_editor(
            st.session_state.parcelas,
            hide_index=True,
            use_container_width=True,
            disabled=["ID", "Data", "Valor (R$)"],
            height=300 # Limita a altura para criar scroll
        )
        if not edited_parcelas.equals(st.session_state.parcelas):
            st.session_state.parcelas = edited_parcelas
            st.rerun()

    # CARTÃO: MÓVEIS
    with st.container(border=True):
        st.subheader("Lista de Móveis e Decoração", anchor=False)
        with st.form("form_moveis", border=False):
            c_nome, c_valor, c_btn = st.columns([3, 2, 1])
            nome_item = c_nome.text_input("Nome do Item", placeholder="Ex: Sofá")
            valor_item = c_valor.number_input("Valor Est. R$", min_value=0.0, step=50.0)
            
            # Alinha o botão do formulário na parte inferior
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
                use_container_width=True
            )
            if not edited_moveis.equals(st.session_state.moveis):
                st.session_state.moveis = edited_moveis
                st.rerun()
