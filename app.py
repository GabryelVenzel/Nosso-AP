import streamlit as st
import pandas as pd
from datetime import date

# 1. Configuração da página
st.set_page_config(page_title="Te Amo Muito - Nosso AP", layout="wide")

# 2. Inicialização do estado (sessão)
if 'gabryel' not in st.session_state: st.session_state.gabryel = 0.0
if 'julia' not in st.session_state: st.session_state.julia = 0.0
if 'emprestimo_pago' not in st.session_state: st.session_state.emprestimo_pago = 0.0

if 'parcelas' not in st.session_state:
    start_date = date(2026, 5, 30)
    parcelas_data = []
    for i in range(39):
        # Ajuste de data simplificado
        mes = (start_date.month + i - 1) % 12 + 1
        ano = start_date.year + (start_date.month + i - 1) // 12
        dia = 28 if mes == 2 else 30
        data_venc = date(ano, mes, min(dia, 31))
        parcelas_data.append({"ID": f"#{str(i+1).zfill(2)}", "Data": data_venc.strftime("%d/%m/%Y"), "Valor": 3275.00, "Paga": False})
    st.session_state.parcelas = pd.DataFrame(parcelas_data)

if 'moveis' not in st.session_state:
    st.session_state.moveis = pd.DataFrame(columns=["Item", "Valor (R$)", "Comprado"])

# 3. Cabeçalho
st.title("Nosso Apartamento 🏢")
try:
    st.image("portaria.jpg", use_container_width=True)
except FileNotFoundError:
    pass # Caso a imagem não esteja no diretório ainda

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

# 5. Progresso Triplo
col1, col2, col3 = st.columns(3)

with col1:
    st.info("Saldo Devedor (20k)")
    st.metric("Restante", f"R$ {saldo_devedor:,.2f}")
    st.progress(int(perc_devedor), text=f"{perc_devedor:.0f}% Pago")

with col2:
    st.info("Parcelas AP")
    st.metric(f"Pagas (Total: R$ {valor_total_pago:,.2f})", f"{num_pagas} de 39")
    st.progress(int(perc_parcelas), text=f"{perc_parcelas:.0f}% Concluído")

with col3:
    st.success("Móveis e Decoração")
    st.metric(f"Meta: R$ {total_moveis_meta:,.2f}", f"Comprados: R$ {total_moveis_comprados:,.2f}")
    st.progress(int(perc_moveis), text=f"{perc_moveis:.0f}% Adquirido")

st.divider()

# 6. Layout Principal
left_col, right_col = st.columns([1, 2])

with left_col:
    st.subheader("Gestão de Reservas")
    total_casal = st.session_state.gabryel + st.session_state.julia
    meses_cobertura = int(total_casal / VALOR_PARCELA)
    
    st.metric("Saldo Total", f"R$ {total_casal:,.2f}", f"Cobertura: {meses_cobertura} meses", delta_color="normal")
    
    st.write("##### Gabryel Venzel")
    st.metric("Saldo Atual", f"R$ {st.session_state.gabryel:,.2f}")
    novo_valor_g = st.number_input("Adicionar/Subtrair (Gabryel)", step=100.0, key="in_g")
    c1, c2 = st.columns(2)
    if c1.button("Adicionar", key="add_g"): 
        st.session_state.gabryel += novo_valor_g
        st.rerun()
    if c2.button("Subtrair", key="sub_g"): 
        st.session_state.gabryel = max(0.0, st.session_state.gabryel - novo_valor_g)
        st.rerun()

    st.write("##### Júlia Navarro (Princesa)")
    st.metric("Saldo Atual", f"R$ {st.session_state.julia:,.2f}")
    novo_valor_j = st.number_input("Adicionar/Subtrair (Júlia)", step=100.0, key="in_j")
    c3, c4 = st.columns(2)
    if c3.button("Adicionar", key="add_j"): 
        st.session_state.julia += novo_valor_j
        st.rerun()
    if c4.button("Subtrair", key="sub_j"): 
        st.session_state.julia = max(0.0, st.session_state.julia - novo_valor_j)
        st.rerun()

    try:
        st.image("planta.jpg", caption="Planta B.AP21", use_container_width=True)
    except FileNotFoundError:
        pass

with right_col:
    st.subheader("Abater Empréstimo de Entrada")
    abater = st.number_input("Valor pago R$", min_value=0.0, step=100.0)
    if st.button("Lançar Pagamento"):
        st.session_state.emprestimo_pago = min(20000.0, st.session_state.emprestimo_pago + abater)
        st.rerun()
        
    st.divider()

    st.subheader("Cronograma Bliss (30/05/2026)")
    # st.data_editor permite edição nativa da tabela
    edited_parcelas = st.data_editor(
        st.session_state.parcelas,
        hide_index=True,
        use_container_width=True,
        disabled=["ID", "Data", "Valor"] # Bloqueia edição de tudo exceto o checkbox "Paga"
    )
    if not edited_parcelas.equals(st.session_state.parcelas):
        st.session_state.parcelas = edited_parcelas
        st.rerun()

    st.divider()

    st.subheader("Lista de Móveis e Decoração")
    with st.form("form_moveis"):
        c_nome, c_valor, c_btn = st.columns([2, 1, 1])
        nome_item = c_nome.text_input("Nome do Item (ex: Sofá)")
        valor_item = c_valor.number_input("Valor Est. R$", min_value=0.0, step=50.0)
        submitted = c_btn.form_submit_button("Adicionar")
        if submitted and nome_item:
            novo_item = pd.DataFrame([{"Item": nome_item, "Valor (R$)": valor_item, "Comprado": False}])
            st.session_state.moveis = pd.concat([st.session_state.moveis, novo_item], ignore_index=True)
            st.rerun()
            
    if not st.session_state.moveis.empty:
        # num_rows="dynamic" permite deletar linhas selecionando-as e apertando Delete/Backspace
        edited_moveis = st.data_editor(
            st.session_state.moveis,
            hide_index=True,
            num_rows="dynamic",
            use_container_width=True
        )
        if not edited_moveis.equals(st.session_state.moveis):
            st.session_state.moveis = edited_moveis
            st.rerun()