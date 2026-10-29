import pandas as pd
import streamlit as st

# Ordem da avaliação do carro, do pior para o melhor (a ordem oficial do
# Car Evaluation na UCI)
ORDEM_AVALIACAO = ["unacc", "acc", "good", "vgood"]


@st.cache_data
def load_data(path="data/clean/dataset.csv"):
    """Lê o dataset já tratado (exportado ao final do notebook de EDA)."""
    df = pd.read_csv(path)

    # Codificação ordinal do alvo, no mesmo padrão das colunas _cod do
    # notebook. Sem ela a correlação só cruza os seis atributos entre si — e
    # como o dataset é um fatorial completo, isso dá zero por construção.
    df["avaliacao_cod"] = df["avaliacao_4"].map(
        {nivel: codigo for codigo, nivel in enumerate(ORDEM_AVALIACAO)}
    )
    return df
