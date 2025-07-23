from tinydb import TinyDB
import datetime
import streamlit as st
import pandas as pd

# Banco de dados
DB_FILE = "hardware_data.json"
db = TinyDB(DB_FILE)

# Funções auxiliares
def salvar_dados(dados):
    db.insert(dados)

def carregar_dados():
    return pd.DataFrame(db.all())

def remover_registro(doc_id):
    db.remove(doc_ids=[doc_id])

# Interface principal
def interface():
    st.set_page_config(page_title="Cadastro de Hardware", layout="wide")
    st.title("Cadastro de Produtos")

    # Formulário de entrada
    with st.form("formulario"):
        col1, col2, col3 = st.columns(3)
        categoria = col1.selectbox("Categoria", ["CPU", "Placa Mãe", "Memoria RAM", "Monitor"])
        nome = col2.text_input("Nome do Produto")
        valor = col3.number_input("Valor no Pix (R$)", min_value=0.0, step=0.01)

        cupom = st.text_input("Cupom (opcional)")
        link = st.text_input("Link da Promoção")
        enviado = st.form_submit_button("Confirmar")

        if enviado:
            if not nome:
                st.error("O campo 'Nome do Produto' é obrigatório.")
            elif not link:
                st.error("O campo 'Link da Promoção' é obrigatório.")
            else:
                data = datetime.datetime.now().strftime('%Y-%m-%d')
                salvar_dados({
                    "Categoria": categoria,
                    "Nome": nome,
                    "Valor": valor,
                    "Cupom": cupom,
                    "Data": data,
                    "Link": link
                })
                st.success("Produto salvo com sucesso!")
                st.rerun()

    st.markdown("---")
    st.subheader("Produtos Cadastrados")

    # Carregar dados
    df = carregar_dados()

    if df.empty:
        st.info("Nenhum produto cadastrado ainda.")
        return

    # Resetar índice para exibição a partir do 1
    df = df.reset_index(drop=True)
    df.index = df.index + 1
    df["Selecionar"] = False  # Checkbox para exclusão

    # Mostrar tabela com checkboxes por linha
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        column_order=["Selecionar"] + [col for col in df.columns if col != "Selecionar"],
        disabled=[col for col in df.columns if col != "Selecionar"],
        hide_index=False,
        key="tabela"
    )

    # Botão para excluir linhas selecionadas
    linhas_para_excluir = edited_df[edited_df["Selecionar"] == True]
    if not linhas_para_excluir.empty and st.button("Excluir Linhas Selecionadas"):
        todos_os_docs = db.all()
        for i in linhas_para_excluir.index:
            doc_id = todos_os_docs[i - 1].doc_id  # Corrige para índice real no TinyDB
            remover_registro(doc_id)
        st.success(f"{len(linhas_para_excluir)} linha(s) excluída(s) com sucesso!")
        st.rerun()

if __name__ == "__main__":
    interface()
