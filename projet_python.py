import streamlit as st
import pandas as pd

st.title("Simulateur d'épargne")

capital = st.number_input("Capital de départ (€)", value=500)
versement = st.number_input("Versement mensuel (€)", value=100)
duree = st.slider("Durée (années)", 1, 30, 10)
profil = st.selectbox("Profil de risque", ["Prudent", "Équilibré", "Dynamique"])

st.subheader("Taux actuel (modifiable)")

inflation = 1.5  # % - à mettre à jour manuellement, moyenne 2026 (INSEE)

st.caption(f"""
📌 **Taux réglementés en vigueur (août 2026)** — Livret A / LDDS : 1,70% · LEP : 2,50%
📌 **Inflation actuelle (repère)** : {inflation}% — un taux d'épargne en dessous de ce chiffre fait perdre du pouvoir d'achat en réel
""")

if profil == "Prudent":
    taux = st.slider("Taux Prudent (%)", 0.0, 5.0, 2.5) / 100
elif profil == "Équilibré":
    taux = st.slider("Taux Équilibré (%)", 0.0, 10.0, 5.0) / 100
else:
    taux = st.slider("Taux Dynamique (%)", 0.0, 15.0, 7.5) / 100

def suggerer_enveloppe(profil, duree):
    if profil == "Prudent":
        return "Livret", "disponibilité immédiate et sécurité du capital"
    elif profil == "Dynamique" and duree >= 5:
        return "PEA", "fiscalité avantageuse sur les plus-values après 5 ans"
    elif profil == "Dynamique" and duree < 5:
        return "Livret", "horizon trop court pour profiter de la fiscalité PEA"
    else:
        return "Assurance-vie", "bon compromis flexibilité / fiscalité dégressive"

suggestion, raison = suggerer_enveloppe(profil, duree)
st.info(f"💡 Pour un profil **{profil.lower()}** sur {duree} ans, l'enveloppe **{suggestion}** est souvent adaptée : {raison}. (Indicatif, pas un conseil personnalisé.)")

enveloppe = st.selectbox("Enveloppe fiscale", ["Livret", "PEA", "Assurance-vie"],
                          index=["Livret", "PEA", "Assurance-vie"].index(suggestion))

historique = []
c = capital
total_verse = capital
for annee in range(1, duree + 1):
    c = c + c * taux + versement * 12
    total_verse += versement * 12
    historique.append(round(c, 2))

gain = c - total_verse

def calculer_impot(enveloppe, duree, gain):
    if enveloppe == "Livret":
        return 0
    elif enveloppe == "PEA":
        return gain * 0.30 if duree < 5 else gain * 0.172
    elif enveloppe == "Assurance-vie":
        return gain * 0.30 if duree < 8 else gain * 0.247

impot = calculer_impot(enveloppe, duree, gain)
capital_net = c - impot

st.line_chart(historique)
st.write("Capital brut final :", round(c, 2), "€")
st.write("Gain total :", round(gain, 2), "€")
st.write("Impôt estimé :", round(impot, 2), "€")
st.write("**Capital net après impôt :**", round(capital_net, 2), "€")

with st.expander(f"Comment est calculé l'impôt pour {enveloppe} ?"):
    if enveloppe == "Livret":
        st.write("Les livrets réglementés (Livret A, LDDS, LEP) sont totalement exonérés d'impôt et de prélèvements sociaux, quelle que soit la durée de détention.")
    elif enveloppe == "PEA":
        st.write("""
        - **Avant 5 ans** : les gains sont soumis à la flat tax de 30% (12,8% impôt + 17,2% prélèvements sociaux).
        - **Après 5 ans** : exonération d'impôt sur le revenu, il reste seulement les 17,2% de prélèvements sociaux.
        """)
    elif enveloppe == "Assurance-vie":
        st.write("""
        - **Avant 8 ans** : flat tax de 30% sur les gains.
        - **Après 8 ans** : abattement annuel (4 600€ pour une personne seule, 9 200€ pour un couple), puis 24,7% sur le reste (7,5% impôt + 17,2% prélèvements sociaux).
        """)

with st.expander(f"Avantages et inconvénients : {enveloppe}"):
    if enveloppe == "Livret":
        st.markdown("""
        **✅ Avantages**
        - Disponible à tout moment, sans délai ni pénalité
        - Zéro risque de perte en capital
        - Totalement exonéré d'impôt et de prélèvements sociaux

        **❌ Inconvénients**
        - Plafond de dépôt : 22 950€ (Livret A)
        - Rendement faible, souvent proche ou sous l'inflation
        - Pas d'effet de levier sur le long terme
        """)
    elif enveloppe == "PEA":
        st.markdown("""
        **✅ Avantages**
        - Fiscalité très avantageuse après 5 ans (17,2% au lieu de 30%)
        - Accès à un large choix d'ETF et d'actions
        - Plafond élevé : 150 000€ de versements

        **❌ Inconvénients**
        - Retrait avant 5 ans = perte de l'avantage fiscal (souvent clôture du plan)
        - Capital non garanti, soumis aux fluctuations des marchés
        - Réservé aux résidents fiscaux français
        """)
    elif enveloppe == "Assurance-vie":
        st.markdown("""
        **✅ Avantages**
        - Fiscalité dégressive avec le temps, abattement après 8 ans
        - Transmission facilitée en cas de décès (hors succession classique)
        - Flexible : retraits partiels possibles à tout moment

        **❌ Inconvénients**
        - Fiscalité moins avantageuse que le PEA si retrait avant 8 ans
        - Frais parfois élevés selon le contrat (gestion, entrée)
        - Rendement variable selon le support (fonds euros vs unités de compte)
        """)
