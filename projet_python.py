import streamlit as st
import pandas as pd

st.title("Simulateur d'épargne")

capital = st.number_input("Capital de départ (€)", value=500)
versement = st.number_input("Versement mensuel (€)", value=100)
duree = st.slider("Durée (années)", 1, 30, 10)

taux_par_profil = {
    "Prudent": 0.025,
    "Équilibré": 0.05,
    "Dynamique": 0.075,
}

resultats = {}
for profil, taux in taux_par_profil.items():
    historique = []
    c = capital
    for annee in range(1, duree + 1):
        c = c + c * taux + versement * 12
        historique.append(round(c, 2))
    resultats[profil] = historique

df = pd.DataFrame(resultats)
st.line_chart(df)
st.write(df)