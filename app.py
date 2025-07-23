from tinydb import TinyDB, Query
import datetime
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import os

DB_FILE = "hardware_data.json"
db = TinyDB(DB_FILE)
Produto = Query()

COLUMNS = ["Categoria", "Nome", "Valor", "Cupom", "Data", "Link"]

def salvar_dados(dados):
    db.insert(dados)

def carregar_dados():
    registros = db.all()
    return pd.DataFrame(registros)

def remover_registro(index):
    db.remove(doc_ids=[index])

def interface():
    st.set_page_config(page_title="Cadastro de Hardware", layout="wide")
    st.title("Cadastro de Produtos")

    # Inicializar session_state se não existir
    for key in ["categoria", "nome", "valor", "cupom", "link"]:
        if key not in st.session_state:
            if key == "valor":
                st.session_state[key] = 0.0
            elif key == "categoria":
                st.session_state[key] = "CPU"
            else:
                st.session_state[key] = ""

    with st.form("formulario"):
        col1, col2, col3 = st.columns(3)
        categoria = col1.selectbox("Categoria", ["CPU", "Placa Mãe", "Memoria RAM", "Monitor"], key="categoria")
        nome = col2.text_input("Nome do Produto", key="nome")
        valor = col3.number_input("Valor no Pix (R$)", min_value=0.0, step=0.01, key="valor")

        cupom = st.text_input("Cupom (opcional)", key="cupom")
        link = st.text_input("Link da Promoção", key="link")
        enviado = st.form_submit_button("Confirmar")

        if enviado:
            if not nome:
                st.error("O campo 'Nome do Produto' é obrigatório.")
            elif not link:
                st.error("O campo 'Link da Promoção' é obrigatório.")
            else:
                data = datetime.datetime.now().strftime('%Y-%m-%d')
                salvar_dados({"Categoria": categoria, "Nome": nome, "Valor": valor, "Cupom": cupom, "Data": data, "Link": link})
                st.success("Produto salvo com sucesso!")
                # Resetar campos do formulário
                st.session_state["categoria"] = "CPU"
                st.session_state["nome"] = ""
                st.session_state["valor"] = 0.0
                st.session_state["cupom"] = ""
                st.session_state["link"] = ""

    st.markdown("---")
    st.subheader("Consultar Produtos")

    filtro_nome = st.text_input("Filtrar por Nome")
    col1, col2 = st.columns(2)
    data_inicio = col1.date_input("Data inicial", format="YYYY-MM-DD")
    data_fim = col2.date_input("Data final", format="YYYY-MM-DD")

    df = carregar_dados()

    if filtro_nome:
        df = df[df['Nome'].str.contains(filtro_nome, case=False, na=False)]

    if 'Data' in df.columns:
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        data_inicio = pd.to_datetime(data_inicio)
        data_fim = pd.to_datetime(data_fim)
        df = df[(df['Data'] >= data_inicio) & (df['Data'] <= data_fim)]

    st.dataframe(df)

    if not df.empty:
        st.subheader("Remover Registro")
        index_para_remover = st.number_input("Digite o índice da linha que deseja remover:", min_value=0, max_value=len(df) - 1, step=1)
        if st.button("Remover Linha"):
            doc_id = db.all()[index_para_remover].doc_id
            remover_registro(doc_id)
            st.success(f"Linha {index_para_remover} removida com sucesso!")
            st.experimental_rerun()

    if st.button("Gerar Gráfico de Histórico de Preço"):
        if df.empty:
            st.warning("Sem dados para gerar gráfico.")
        else:
            fig, ax = plt.subplots(figsize=(10, 6))
            pivot_df = df.pivot_table(index="Nome", columns="Data", values="Valor")
            pivot_df = pivot_df.sort_index(axis=1)  # Ordenar datas
            pivot_df.T.plot(ax=ax, marker='o')
            ax.set_title('Histórico de Preço dos Produtos')
            ax.set_xlabel('Data')
            ax.set_ylabel('Preço (R$)')
            ax.legend(title="Nome do Produto", bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)

if __name__ == '__main__':
    interface()
