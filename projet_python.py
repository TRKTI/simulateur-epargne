import io
import time
import unicodedata

import streamlit as st
import pandas as pd
import altair as alt
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="Lucide", page_icon="static/logo-icon.svg", layout="wide")

VIOLET = "#635BFF"
CYAN = "#22D3EE"

# Dégradé violet (couleur du logo) vers cyan, utilisé sur "Lucide" partout où le nom apparaît en grand.
# Cyan saturé (pas pastel) pour que la transition soit visible sur un mot aussi court, et affichage
# en inline-block pour que le dégradé soit calé sur la largeur réelle du texte (pas celle du conteneur).
LUCIDE_GRADIENT_STYLE = (
    f"display: inline-block; background: linear-gradient(90deg, {VIOLET}, {CYAN}); "
    "-webkit-background-clip: text; background-clip: text; "
    "-webkit-text-fill-color: transparent; color: transparent; font-weight: 700;"
)

# Écran de transition affiché brièvement entre le hero et le site : chiffres flottants flous,
# purement CSS (keyframes), pas de JS. Les animation-delay négatifs évitent que tout parte du même
# point de départ, pour un effet déjà "en mouvement" dès l'affichage.
TRANSITION_HTML = f"""
<style>
@keyframes lucide-flotte {{
    0% {{ transform: translateY(18px); opacity: 0; filter: blur(4px); }}
    50% {{ opacity: 0.55; filter: blur(1px); }}
    100% {{ transform: translateY(-18px); opacity: 0; filter: blur(4px); }}
}}
.lucide-transition {{
    position: relative;
    height: 60vh;
    min-height: 380px;
    background: #0B1120;
    overflow: hidden;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
}}
.lucide-transition .chiffre {{
    position: absolute;
    font-weight: 700;
    animation-name: lucide-flotte;
    animation-timing-function: ease-in-out;
    animation-iteration-count: infinite;
}}
.lucide-transition .message {{
    position: relative;
    z-index: 2;
    color: #EAF0FB;
    font-size: 1.1rem;
    letter-spacing: 0.02em;
}}
</style>
<div class="lucide-transition">
    <span class="chiffre" style="top:15%; left:12%; font-size:2.2rem; color:{VIOLET}; animation-duration:3.2s; animation-delay:-0.4s;">12%</span>
    <span class="chiffre" style="top:65%; left:18%; font-size:1.6rem; color:{CYAN}; animation-duration:2.6s; animation-delay:-1.2s;">1 000&euro;</span>
    <span class="chiffre" style="top:25%; left:75%; font-size:2rem; color:{CYAN}; animation-duration:3.6s; animation-delay:-0.8s;">7,5%</span>
    <span class="chiffre" style="top:70%; left:70%; font-size:1.8rem; color:{VIOLET}; animation-duration:2.9s; animation-delay:-2s;">3%</span>
    <span class="chiffre" style="top:45%; left:8%; font-size:1.4rem; color:{VIOLET}; animation-duration:3.4s; animation-delay:-1.6s;">1,7%</span>
    <span class="chiffre" style="top:10%; left:45%; font-size:1.5rem; color:{CYAN}; animation-duration:2.4s; animation-delay:-0.6s;">20 ans</span>
    <span class="chiffre" style="top:80%; left:42%; font-size:1.7rem; color:{VIOLET}; animation-duration:3.1s; animation-delay:-1.9s;">10%</span>
    <span class="chiffre" style="top:38%; left:85%; font-size:1.3rem; color:{CYAN}; animation-duration:2.8s; animation-delay:-0.3s;">+2 061&euro;</span>
    <p class="message">Un instant...</p>
</div>
"""

if "a_demarre" not in st.session_state:
    st.session_state.a_demarre = False

if not st.session_state.a_demarre:
    hero = st.empty()
    with hero.container():
        st.container(height=48, border=False)
        with st.container(horizontal_alignment="center"):
            with st.container(horizontal=True, vertical_alignment="center", gap="small", width="content"):
                st.image("static/logo-icon.svg", width=24)
                st.markdown(
                    f'<span style="{LUCIDE_GRADIENT_STYLE}">Lucide</span> '
                    '<span style="color: #94A3B8; font-size: 0.85em;">- vois clair dans ton épargne</span>',
                    unsafe_allow_html=True,
                )

        st.container(height=64, border=False)
        with st.container(horizontal_alignment="center"):
            st.title("On t'a appris à travailler pour gagner de l'argent. Personne ne t'a appris quoi en faire.")
            st.caption("*Découvre-le maintenant, en 5 minutes.*")
            demarrer = st.button("Démarrer", type="primary")

    if demarrer:
        hero.markdown(TRANSITION_HTML, unsafe_allow_html=True)
        time.sleep(1.8)

        st.session_state.a_demarre = True
        st.session_state.quiz_ouvert = False
        st.session_state.aller_direct_au_cours = True
        st.session_state.cours_etape = 0
        st.rerun()
    st.stop()

st.logo("static/logo.svg", size="large", icon_image="static/logo-icon.svg")


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


def suggerer_enveloppe(profil, duree):
    if profil == "Prudent":
        return "Livret", "disponibilité immédiate et sécurité du capital"
    elif profil == "Dynamique" and duree >= 5:
        return "PEA", "fiscalité avantageuse sur les plus-values après 5 ans"
    elif profil == "Dynamique" and duree < 5:
        return "Livret", "horizon trop court pour profiter de la fiscalité PEA"
    else:
        return "Assurance-vie", "bon compromis flexibilité / fiscalité dégressive"


def calculer_impot(enveloppe, duree, gain):
    if enveloppe == "Livret":
        return 0
    elif enveloppe == "PEA":
        return gain * 0.30 if duree < 5 else gain * 0.172
    elif enveloppe == "Assurance-vie":
        return gain * 0.30 if duree < 8 else gain * 0.247


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


if "quiz_profil" not in st.session_state:
    st.session_state.quiz_profil = None
if "quiz_ouvert" not in st.session_state:
    st.session_state.quiz_ouvert = True  # s'ouvre une seule fois, au tout premier chargement
if "cours_etape" not in st.session_state:
    st.session_state.cours_etape = 0


def fermer_quiz():
    st.session_state.quiz_ouvert = False


@st.dialog("Petit quiz pour démarrer", on_dismiss=fermer_quiz)
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


NB_ETAPES_COURS = 7  # 0 Épargner, 1 Taux, 2 Comparaison, 3 Pyramide, 4 Fiscalité, 5 Enveloppes, 6 Étape finale


def navigation_cours(etape, texte_suivant="Suivant"):
    with st.container(horizontal=True):
        if etape > 0:
            if st.button("Précédent", key=f"cours_precedent_{etape}"):
                st.session_state.cours_etape -= 1
                st.rerun()
        if st.button(texte_suivant, type="primary", key=f"cours_suivant_{etape}"):
            st.session_state.cours_etape += 1
            st.rerun()


def vue_cours():
    st.subheader("Cours")
    etape = st.session_state.cours_etape
    st.progress((etape + 1) / NB_ETAPES_COURS, text=f"Étape {etape + 1}/{NB_ETAPES_COURS}")

    if etape == 0:
        st.subheader("Épargner")
        st.markdown("""
Épargner, c'est mettre de côté une partie de ce que tu gagnes pour t'en servir plus tard. Plus tu commences tôt, plus cet argent a de temps pour "travailler" pour toi.
""")
        navigation_cours(etape)

    elif etape == 1:
        st.subheader("Le taux")
        st.markdown("""
Le taux, c'est ce que ton épargne te rapporte chaque année. 3% sur 1 000€ = environ 30€ au bout d'un an.

Le vrai levier : les **intérêts composés** — tu gagnes des intérêts sur tes intérêts précédents. Sur 10-20 ans, l'effet est énorme.
""")
        navigation_cours(etape)

    elif etape == 2:
        st.subheader("L'écart, en vrai")
        st.write("Même somme de départ, même durée : regarde ce qui se passe si elle dort, si elle est en Livret, ou si elle est investie.")

        somme = st.number_input("Somme de départ (€)", min_value=0, value=1000, step=100, key="cours_somme")
        duree_demo = st.slider("Durée (années)", 1, 30, 10, key="cours_duree_demo")

        scenarios = {
            "Argent qui dort (0%)": 0.0,
            "Épargne sécurisée - Livret A (~1,7%)": 0.017,
            "Investi - profil dynamique (~7,5%)": 0.075,
        }

        lignes_demo = []
        capital_final_par_scenario = {}
        for nom_scenario, taux_scenario in scenarios.items():
            lignes = simuler(somme, 0, duree_demo, taux_scenario)
            capital_final_par_scenario[nom_scenario] = lignes[-1]["Capital"]
            for ligne in lignes:
                lignes_demo.append({"Scénario": nom_scenario, "Année": ligne["Année"], "Capital": ligne["Capital"]})

        inflation_demo = 1.5
        for annee in range(1, duree_demo + 1):
            valeur_reelle = somme / (1 + inflation_demo / 100) ** annee
            lignes_demo.append({
                "Scénario": "Argent qui dort - pouvoir d'achat réel",
                "Année": annee,
                "Capital": round(valeur_reelle, 2),
            })

        df_demo = pd.DataFrame(lignes_demo)
        chart_demo = alt.Chart(df_demo).mark_line().encode(
            x=alt.X("Année:Q", title="Année"),
            y=alt.Y("Capital:Q", title="Capital (€)"),
            color=alt.Color("Scénario:N", title=""),
            strokeDash=alt.condition(
                alt.datum.Scénario == "Argent qui dort - pouvoir d'achat réel",
                alt.value([5, 4]),
                alt.value([1, 0]),
            ),
        )
        st.altair_chart(chart_demo)

        capital_dort = capital_final_par_scenario["Argent qui dort (0%)"]
        capital_investi = capital_final_par_scenario["Investi - profil dynamique (~7,5%)"]
        ecart = capital_investi - capital_dort
        valeur_reelle_dort = somme / (1 + inflation_demo / 100) ** duree_demo

        with st.container(horizontal=True):
            st.metric(f"Écart après {duree_demo} ans : investi vs argent qui dort", f"{round(ecart, 2)} €", border=True)
            st.metric(
                "Pouvoir d'achat réel de l'argent qui dort",
                f"{round(valeur_reelle_dort, 2)} €",
                f"{round(valeur_reelle_dort - somme, 2)} €",
                border=True,
            )

        st.caption(f"📌 Ligne pointillée : pouvoir d'achat réel de l'argent qui dort, année après année. Hypothèse d'inflation constante à {inflation_demo}%/an. (Indicatif, pas un conseil personnalisé.)")

        navigation_cours(etape)

    elif etape == 3:
        st.subheader("La pyramide de l'épargne")
        st.markdown("""
Avant de choisir où placer ton argent, une question compte plus que le taux : à quoi sert cette somme ? Trois étages.

**1. Épargne de précaution** — se calcule sur tes **dépenses mensuelles**, pas ton salaire (erreur fréquente). Repère : 3 mois de dépenses en CDI stable, 6 à 9 mois si revenus irréguliers (indépendant, CDD), +1 mois par enfant à charge. Toujours 100% liquide et sécurisée : LEP en priorité si tu y es éligible (2,50%, plafond 10 000€), sinon Livret A/LDDS (1,70%, plafond 22 950€ pour le Livret A). Jamais sur un compte courant, qui perd du pouvoir d'achat face à l'inflation.

**2. Épargne projets** (2 à 5 ans) — Livret A/LDDS ou fonds euros d'assurance-vie selon l'horizon.

**3. Épargne long terme** (retraite, patrimoine, 5-8 ans et plus) — PEA, assurance-vie en unités de compte, PER.
""")
        navigation_cours(etape)

    elif etape == 4:
        st.subheader("La fiscalité")
        st.markdown("""
L'État prélève une partie de tes gains — jamais sur ce que tu as versé. En France, la référence est la **flat tax** (30%), mais elle varie selon l'enveloppe et la durée de détention.
""")
        navigation_cours(etape)

    elif etape == 5:
        st.subheader("Les enveloppes")
        st.markdown("""
Une enveloppe, c'est le contenant de ton épargne (Livret, PEA, Assurance-vie...), avec ses propres règles de fiscalité, plafond et disponibilité. Le simulateur t'en suggère une selon ton profil — modifiable à tout moment.
""")
        navigation_cours(etape)

    else:
        st.subheader("À toi de jouer")
        st.write("Deux chiffres, et on prépare le simulateur avec tes valeurs.")

        revenu = st.number_input("Ton revenu mensuel (€)", min_value=0, value=1500, step=50)
        epargne = st.number_input("Ce que tu veux mettre de côté chaque mois (€)", min_value=0, value=150, step=10)

        if revenu > 0:
            pourcentage = epargne / revenu * 100
            st.caption(f"📌 Repère générique : on recommande souvent de mettre de côté entre 10 et 20% de ses revenus. Toi, tu es à **{round(pourcentage, 1)}%**. (Indicatif, pas un conseil personnalisé — à ajuster selon ta situation.)")

        with st.container(horizontal=True):
            if st.button("Précédent", key=f"cours_precedent_{etape}"):
                st.session_state.cours_etape -= 1
                st.rerun()
            if st.button("Voir mon simulateur", type="primary", key=f"cours_suivant_{etape}"):
                st.session_state.versement_input = float(epargne)
                st.session_state.cours_etape = 0
                st.session_state.quiz_ouvert = True
                st.switch_page(page_information_profil)


def vue_information_profil():
    with st.sidebar:
        st.subheader("Tes paramètres")

        capital = st.number_input("Capital de départ (€)", value=500)
        versement = st.number_input("Versement mensuel (€)", value=100, key="versement_input")
        duree = st.slider("Durée (années)", 1, 30, 10)

        profils_liste = ["Prudent", "Équilibré", "Dynamique"]
        index_profil = profils_liste.index(st.session_state.quiz_profil) if st.session_state.quiz_profil else 0
        profil = st.selectbox("Profil de risque", profils_liste, index=index_profil,
                               help="Le niveau de risque (et donc de rendement potentiel) que tu es prêt à accepter. Plus le profil est dynamique, plus le taux peut monter haut — mais rien n'est garanti.")

        if st.session_state.quiz_profil:
            st.caption(f"Pré-rempli par le quiz : {st.session_state.quiz_profil}")
        if st.button("Refaire le quiz de profil"):
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
                                  help="Le contenant qui détermine comment tes gains sont imposés. Termes techniques ? Direction le glossaire en haut de la page.")
        st.caption(f"Suggestion pour un profil {profil.lower()} sur {duree} ans : **{suggestion}** — {raison}. (Indicatif, pas un conseil personnalisé.)")

        if profil == "Prudent":
            taux_max, taux_defaut = 5.0, 2.5
        elif profil == "Équilibré":
            taux_max, taux_defaut = 10.0, 5.0
        else:
            taux_max, taux_defaut = 15.0, 7.5

        if enveloppe == "Livret":
            taux_max = min(taux_max, 3.0)
            taux_defaut = min(taux_defaut, taux_max)
            st.caption("Taux plafonné à 3% : un Livret réglementé ne rend pas plus que ça.")

        taux = st.slider(f"Taux {profil} (%)", 0.0, taux_max, taux_defaut) / 100

    if st.session_state.quiz_ouvert and st.session_state.quiz_profil is None:
        quiz_profil()

    with st.container(horizontal=True, vertical_alignment="center"):
        st.image("static/logo-icon.svg", width=48)
        st.markdown(
            f'<h1 style="{LUCIDE_GRADIENT_STYLE} font-size: 2.5rem; margin: 0; line-height: 1;">Lucide</h1>',
            unsafe_allow_html=True,
        )
    st.caption("Le simulateur d'épargne qui n'a rien à cacher. Vois clair sur ton capital, tes profils de risque et l'impact réel de la fiscalité française.")

    with st.popover("Glossaire", icon=":material/menu_book:"):
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

    historique = simuler(capital, versement, duree, taux)
    df_evolution = pd.DataFrame(historique)

    c = df_evolution["Capital"].iloc[-1]
    total_verse = df_evolution["Versé cumulé"].iloc[-1]
    gain = df_evolution["Gain cumulé"].iloc[-1]

    impot = calculer_impot(enveloppe, duree, gain)
    capital_net = c - impot

    with st.container(border=True):
        st.subheader(f"Résultat — profil {profil}")
        st.caption(f"Enveloppe simulée : **{enveloppe}**")

        with st.container(horizontal=True):
            st.metric("Capital final", f"{round(c, 2)} €", f"+{round(gain, 2)} €", border=True)
            st.metric("Impôt estimé", f"{round(impot, 2)} €", border=True)
            st.metric("Capital net", f"{round(capital_net, 2)} €", border=True)

        tab_evolution, tab_comparaison = st.tabs(["Évolution", "Comparer les profils"])

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
            "Télécharger ma carte résultat",
            data=carte_png,
            file_name="lucide-resultat.png",
            mime="image/png",
            icon=":material/share:",
        )

    with st.expander("Détail année par année", icon=":material/table_chart:"):
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
            **Avantages**
            - Disponible à tout moment, sans délai ni pénalité
            - Zéro risque de perte en capital
            - Totalement exonéré d'impôt et de prélèvements sociaux

            **Inconvénients**
            - Plafond de dépôt : 22 950€ (Livret A)
            - Rendement faible, souvent proche ou sous l'inflation
            - Pas d'effet de levier sur le long terme
            """)
            st.markdown("**Dans la pratique** — le Livret A/LDDS sert avant tout de matelas de sécurité immédiatement disponible, pas de moteur de performance. Au-delà de l'épargne de précaution, la plupart des ressources pédagogiques recommandent de chercher un rendement ailleurs pour ne pas perdre de pouvoir d'achat face à l'inflation sur le long terme.")
        elif enveloppe == "PEA":
            st.markdown("""
            **Avantages**
            - Fiscalité très avantageuse après 5 ans (17,2% au lieu de 30%)
            - Accès à un large choix d'ETF et d'actions
            - Plafond élevé : 150 000€ de versements

            **Inconvénients**
            - Retrait avant 5 ans = perte de l'avantage fiscal (souvent clôture du plan)
            - Capital non garanti, soumis aux fluctuations des marchés
            - Réservé aux résidents fiscaux français
            """)
            st.markdown("**Dans la pratique** — la diversification via des ETF monde larges (type MSCI World) est une approche couramment recommandée par les acteurs de l'éducation financière pour réduire le risque spécifique lié à une seule action ou un seul secteur, plutôt que de miser sur des titres isolés.")
        elif enveloppe == "Assurance-vie":
            st.markdown("""
            **Avantages**
            - Fiscalité dégressive avec le temps, abattement après 8 ans
            - Transmission facilitée en cas de décès (hors succession classique)
            - Flexible : retraits partiels possibles à tout moment

            **Inconvénients**
            - Fiscalité moins avantageuse que le PEA si retrait avant 8 ans
            - Frais parfois élevés selon le contrat (gestion, entrée)
            - Rendement variable selon le support (fonds euros vs unités de compte)
            """)
            st.markdown("**Dans la pratique** — le fonds euros sécurise le capital mais son rendement suit la tendance des taux d'intérêt (souvent proche de celui des livrets ces dernières années), tandis que les unités de compte (actions, ETF, immobilier...) visent un rendement plus élevé en échange d'un risque de perte en capital. La répartition entre les deux dépend de l'horizon et de la tolérance au risque de chacun.")


def vue_comment_debuter():
    st.subheader("Comment débuter")
    st.write("Le bon endroit pour ouvrir tes comptes dépend surtout de ton niveau d'autonomie face à l'épargne — pas d'un nom d'établissement en particulier.")

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**Peu de connaissances, débutant total**")
            st.write("Privilégie un établissement avec un conseiller physique disponible et un accompagnement pédagogique, quitte à avoir des frais un peu plus élevés au départ.")
            st.caption("Catégorie type : banques traditionnelles (réseau physique).")
    with col2:
        with st.container(border=True):
            st.markdown("**À l'aise, autonome**")
            st.write("Les banques en ligne et courtiers spécialisés offrent des frais réduits et une gestion 100% autonome, sans accompagnement humain systématique.")
            st.caption("Catégorie type : banques en ligne, courtiers en ligne.")

    st.subheader("Critères à comparer objectivement")
    st.markdown("""
    - **Frais de tenue de compte** : certains établissements les facturent, d'autres non.
    - **Frais de courtage** (pour un PEA) : varient fortement d'un courtier à l'autre.
    - **Disponibilité d'un conseiller** : présence physique, joignabilité, réactivité.
    - **Simplicité de l'interface** : application/site clair ou non, selon ton aisance avec ces outils.
    """)
    st.caption("Ces catégories sont indicatives — aucun établissement n'est recommandé ici personnellement, à toi de comparer selon tes propres critères. (Indicatif, pas un conseil personnalisé.)")


page_information_profil = st.Page(vue_information_profil, title="Information et profil", icon=":material/person:", default=True)
page_cours = st.Page(vue_cours, title="Cours", icon=":material/school:")
page_comment_debuter = st.Page(vue_comment_debuter, title="Comment débuter", icon=":material/explore:")

pages = st.navigation([page_information_profil, page_cours, page_comment_debuter])

if st.session_state.pop("aller_direct_au_cours", False):
    st.switch_page(page_cours)

pages.run()
