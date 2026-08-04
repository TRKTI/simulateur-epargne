import io
import unicodedata

import streamlit as st
import pandas as pd
import altair as alt
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="Lucide", page_icon="🔎", layout="wide")

st.logo("static/logo.svg", size="large", icon_image="static/logo-icon.svg")

if "quiz_profil" not in st.session_state:
    st.session_state.quiz_profil = None
if "quiz_ouvert" not in st.session_state:
    st.session_state.quiz_ouvert = True  # s'ouvre une seule fois, au tout premier chargement


def fermer_quiz():
    st.session_state.quiz_ouvert = False


@st.dialog("🎯 Petit quiz pour démarrer", on_dismiss=fermer_quiz)
def quiz_profil():
    st.write("3 questions pour pré-remplir ton profil de risque. Tu pourras toujours le changer ensuite.")

    q1 = st.radio(
        "Ton épargne perd 10% en un an, tu réagis comment ?",
        ["Je retire tout, plus jamais ça", "Je regarde mais je ne touche à rien", "J'en profite pour remettre au pot"],
    )
    q2 = st.radio(
        "Dans combien de temps penses-tu avoir besoin de cet argent ?",
        ["Moins de 3 ans", "Entre 3 et 8 ans", "Plus de 8 ans"],
    )
    q3 = st.radio(
        "Ton objectif principal ?",
        ["Sécuriser, ne jamais perdre un centime", "Un compromis entre sécurité et performance", "Maximiser le rendement, quitte à prendre des risques"],
    )

    if st.button("Valider", type="primary"):
        reponses_prudentes = ["Je retire tout, plus jamais ça", "Moins de 3 ans", "Sécuriser, ne jamais perdre un centime"]
        reponses_dynamiques = ["J'en profite pour remettre au pot", "Plus de 8 ans", "Maximiser le rendement, quitte à prendre des risques"]

        votes = []
        for reponse in [q1, q2, q3]:
            if reponse in reponses_prudentes:
                votes.append("Prudent")
            elif reponse in reponses_dynamiques:
                votes.append("Dynamique")
            else:
                votes.append("Équilibré")

        if votes.count("Prudent") >= 2:
            profil_suggere = "Prudent"
        elif votes.count("Dynamique") >= 2:
            profil_suggere = "Dynamique"
        else:
            profil_suggere = "Équilibré"

        st.session_state.quiz_profil = profil_suggere
        st.session_state.quiz_ouvert = False
        st.rerun()


if st.session_state.quiz_ouvert and st.session_state.quiz_profil is None:
    quiz_profil()


def suggerer_enveloppe(profil, duree):
    if profil == "Prudent":
        return "Livret", "disponibilité immédiate et sécurité du capital"
    elif profil == "Dynamique" and duree >= 5:
        return "PEA", "fiscalité avantageuse sur les plus-values après 5 ans"
    elif profil == "Dynamique" and duree < 5:
        return "Livret", "horizon trop court pour profiter de la fiscalité PEA"
    else:
        return "Assurance-vie", "bon compromis flexibilité / fiscalité dégressive"


def texte_carte(texte):
    """Nettoie le texte pour la police par défaut de Pillow, qui ne couvre que l'ASCII de base
    (accents et € s'affichent en carré vide sinon)."""
    texte = texte.replace("—", "-").replace("€", "EUR")
    normalise = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in normalise if not unicodedata.combining(c))


def generer_carte_resultat(profil, enveloppe, duree, capital_final, gain, capital_net):
    """Dessine une carte-résultat 1200x630 (format partage réseaux sociaux) et la retourne en PNG (bytes)."""
    largeur, hauteur = 1200, 630
    fond = (11, 17, 32)
    accent = (99, 91, 255)
    vert = (52, 211, 153)
    texte_couleur = (234, 240, 251)
    gris = (148, 163, 184)

    image = Image.new("RGB", (largeur, hauteur), fond)
    dessin = ImageDraw.Draw(image)

    police_grand = ImageFont.load_default(size=64)
    police_moyen = ImageFont.load_default(size=32)
    police_petit = ImageFont.load_default(size=22)

    dessin.ellipse([80, 70, 130, 120], outline=accent, width=5)
    dessin.ellipse([97, 87, 113, 103], fill=accent)
    dessin.text((150, 78), "Lucide", font=police_moyen, fill=texte_couleur)

    dessin.text((80, 220), texte_carte(f"Capital après {duree} ans — profil {profil}"), font=police_petit, fill=gris)
    dessin.text((80, 250), texte_carte(f"{capital_final:,.0f} €").replace(",", " "), font=police_grand, fill=accent)

    dessin.text((80, 360), texte_carte(f"Gains estimés : +{gain:,.0f} €").replace(",", " "), font=police_moyen, fill=vert)
    dessin.text((80, 410), texte_carte(f"Capital net après impôt ({enveloppe}) : {capital_net:,.0f} €").replace(",", " "), font=police_moyen, fill=texte_couleur)

    dessin.text((80, hauteur - 60), texte_carte("Simule le tien sur Lucide — vois clair sur ton épargne"), font=police_petit, fill=gris)

    tampon = io.BytesIO()
    image.save(tampon, format="PNG")
    return tampon.getvalue()


with st.sidebar:
    st.subheader("🧮 Tes paramètres")

    capital = st.number_input("Capital de départ (€)", value=500)
    versement = st.number_input("Versement mensuel (€)", value=100)
    duree = st.slider("Durée (années)", 1, 30, 10)

    profils_liste = ["Prudent", "Équilibré", "Dynamique"]
    index_profil = profils_liste.index(st.session_state.quiz_profil) if st.session_state.quiz_profil else 0
    profil = st.selectbox("Profil de risque", profils_liste, index=index_profil,
                           help="Le niveau de risque (et donc de rendement potentiel) que tu es prêt à accepter. Plus le profil est dynamique, plus le taux peut monter haut — mais rien n'est garanti.")

    if st.session_state.quiz_profil:
        st.caption(f"🎯 Pré-rempli par le quiz : {st.session_state.quiz_profil}")
    if st.button("🎯 Refaire le quiz de profil"):
        st.session_state.quiz_ouvert = True
        st.session_state.quiz_profil = None
        st.rerun()

    inflation = 1.5  # % - à mettre à jour manuellement, moyenne 2026 (INSEE)

    st.caption(f"""
    📌 **Taux réglementés (août 2026)** — Livret A / LDDS : 1,70% · LEP : 2,50%
    📌 **Inflation (repère)** : {inflation}% — un taux d'épargne en dessous fait perdre du pouvoir d'achat en réel
    """)

    suggestion, raison = suggerer_enveloppe(profil, duree)
    enveloppe = st.selectbox("Enveloppe fiscale", ["Livret", "PEA", "Assurance-vie"],
                              index=["Livret", "PEA", "Assurance-vie"].index(suggestion),
                              help="Le contenant qui détermine comment tes gains sont imposés. Termes techniques ? Direction le glossaire 📖 en haut de la page.")
    st.caption(f"💡 Suggestion pour un profil {profil.lower()} sur {duree} ans : **{suggestion}** — {raison}. (Indicatif, pas un conseil personnalisé.)")

    if profil == "Prudent":
        taux_max, taux_defaut = 5.0, 2.5
    elif profil == "Équilibré":
        taux_max, taux_defaut = 10.0, 5.0
    else:
        taux_max, taux_defaut = 15.0, 7.5

    if enveloppe == "Livret":
        taux_max = min(taux_max, 3.0)
        taux_defaut = min(taux_defaut, taux_max)
        st.caption("🔒 Taux plafonné à 3% : un Livret réglementé ne rend pas plus que ça.")

    taux = st.slider(f"Taux {profil} (%)", 0.0, taux_max, taux_defaut) / 100

st.title("🔎 Lucide")
st.caption("Le simulateur d'épargne qui n'a rien à cacher. Vois clair sur ton capital, tes profils de risque et l'impact réel de la fiscalité française.")

with st.popover("📖 Glossaire", icon=":material/menu_book:"):
    st.markdown("""
    - **PEA** (Plan d'Épargne en Actions) : enveloppe pour investir en actions/ETF, fiscalité avantageuse après 5 ans.
    - **Livret A / LDDS / LEP** : livrets d'épargne réglementés par l'État, taux fixé, zéro fiscalité, mais plafonnés.
    - **Assurance-vie** : enveloppe flexible, fiscalité qui s'allège avec le temps (abattement après 8 ans).
    - **Flat tax** : prélèvement forfaitaire unique de 30% sur les gains (12,8% impôt + 17,2% prélèvements sociaux).
    - **Prélèvements sociaux** : part de la flat tax (17,2%) qui finance la sécurité sociale, due même quand l'impôt est exonéré.
    - **Abattement** : montant de gains exonéré d'impôt chaque année (ex : 4 600€ pour une assurance-vie après 8 ans).
    - **Plus-value / gain** : différence entre ce que vaut ton épargne aujourd'hui et ce que tu as versé.
    - **Capital net** : ce qu'il te reste après impôt — l'argent réellement disponible.
    """)


def simuler(capital, versement, duree, taux):
    """Simule l'évolution du capital année par année. Retourne une liste de lignes (dicts)."""
    lignes = []
    c = capital
    total_verse = capital
    for annee in range(1, duree + 1):
        c = c + c * taux + versement * 12
        total_verse += versement * 12
        lignes.append({
            "Année": annee,
            "Capital": round(c, 2),
            "Versé cumulé": round(total_verse, 2),
            "Gain cumulé": round(c - total_verse, 2),
        })
    return lignes


historique = simuler(capital, versement, duree, taux)
df_evolution = pd.DataFrame(historique)

c = df_evolution["Capital"].iloc[-1]
total_verse = df_evolution["Versé cumulé"].iloc[-1]
gain = df_evolution["Gain cumulé"].iloc[-1]


def calculer_impot(enveloppe, duree, gain):
    if enveloppe == "Livret":
        return 0
    elif enveloppe == "PEA":
        return gain * 0.30 if duree < 5 else gain * 0.172
    elif enveloppe == "Assurance-vie":
        return gain * 0.30 if duree < 8 else gain * 0.247


impot = calculer_impot(enveloppe, duree, gain)
capital_net = c - impot

emoji_profil = {"Prudent": "🛡️", "Équilibré": "⚖️", "Dynamique": "🚀"}

with st.container(border=True):
    st.subheader(f"{emoji_profil[profil]} Résultat — profil {profil}")
    st.caption(f"🏦 Enveloppe simulée : **{enveloppe}**")

    with st.container(horizontal=True):
        st.metric("Capital final", f"{round(c, 2)} €", f"+{round(gain, 2)} €", border=True)
        st.metric("Impôt estimé", f"{round(impot, 2)} €", border=True)
        st.metric("Capital net", f"{round(capital_net, 2)} €", border=True)

    tab_evolution, tab_comparaison = st.tabs(["📈 Évolution", "⚖️ Comparer les profils"])

    with tab_evolution:
        courbe = alt.Chart(df_evolution).mark_area(
            line={"color": "#635BFF"},
            color="#635BFF",
            opacity=0.25,
        ).encode(
            x=alt.X("Année:Q", title="Année"),
            y=alt.Y("Capital:Q", title="Capital (€)"),
        )
        st.altair_chart(courbe)

    with tab_comparaison:
        taux_par_defaut = {"Prudent": 0.025, "Équilibré": 0.05, "Dynamique": 0.075}
        lignes_comparaison = []
        for nom_profil, taux_defaut in taux_par_defaut.items():
            for ligne in simuler(capital, versement, duree, taux_defaut):
                lignes_comparaison.append({
                    "Profil": nom_profil,
                    "Année": ligne["Année"],
                    "Capital": ligne["Capital"],
                })
        df_comparaison = pd.DataFrame(lignes_comparaison)

        courbe_comparaison = alt.Chart(df_comparaison).mark_line().encode(
            x=alt.X("Année:Q", title="Année"),
            y=alt.Y("Capital:Q", title="Capital (€)"),
            color=alt.Color("Profil:N", title="Profil"),
        )
        st.altair_chart(courbe_comparaison)
        st.caption("Estimation à taux par défaut pour chaque profil (2,5% / 5% / 7,5%), indépendamment du taux que tu as réglé ci-contre.")

    progression = min(gain / total_verse, 1.0) if total_verse > 0 else 0
    st.progress(progression, text=f"Tes gains représentent {round(progression*100, 1)}% de ce que tu as versé")

    carte_png = generer_carte_resultat(profil, enveloppe, duree, c, gain, capital_net)
    st.download_button(
        "📤 Télécharger ma carte résultat",
        data=carte_png,
        file_name="lucide-resultat.png",
        mime="image/png",
        icon=":material/share:",
    )

with st.expander("📅 Détail année par année", icon=":material/table_chart:"):
    st.dataframe(
        df_evolution,
        hide_index=True,
        column_config={
            "Capital": st.column_config.NumberColumn("Capital", format="%.2f €"),
            "Versé cumulé": st.column_config.NumberColumn("Versé cumulé", format="%.2f €"),
            "Gain cumulé": st.column_config.NumberColumn("Gain cumulé", format="%.2f €"),
        },
    )

with st.expander(f"Comment est calculé l'impôt pour {enveloppe} ?", icon=":material/calculate:"):
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

with st.expander(f"Avantages et inconvénients : {enveloppe}", icon=":material/balance:"):
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
