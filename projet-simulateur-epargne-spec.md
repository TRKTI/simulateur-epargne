# Simulateur d'épargne — Spécification projet

## 1. Fonctionnalités
- Simulateur générique + 3 enveloppes françaises : Livret, PEA, Assurance-vie
- Entrées : capital initial, versement mensuel, taux, durée, profil de risque (prudent/équilibré/dynamique)
- Versements variables (augmentation annuelle, pauses) : reporté à v2
- Fiscalité française intégrée (différenciateur clé face aux robo-advisors)
- Visualisation : graphique d'évolution, tableau année par année, comparaison des 3 profils

## 2. Conseils et positionnement
- Pas de recommandation personnalisée précise (évite le statut CIF/ORIAS)
- Contenu éducatif statique (articles, FAQ) en complément du simulateur
- Positionnement : outil pédagogique, transparent ("boîte de verre"), jamais "achète ce produit"

## 3. Technique
- v1 : Streamlit, pas de backend ni base de données
- v2 (si traction) : React + FastAPI, comptes utilisateurs, sauvegarde de simulations
- Design : esthétique "grand livre comptable" (validée dans le prototype React initial)
- Responsive mobile obligatoire

## 4. Périmètre du livrable
- v1 : une seule page (simulateur + bloc éducatif court)
- v2 : pages séparées (simulateur / blog / à propos)

## Plan du site v1
1. Header + intro courte
2. Formulaire de simulation (inputs)
3. Résultat + graphique comparatif
4. Tableau détaillé année par année
5. Bloc pédagogique "comprendre les hypothèses"
6. Disclaimer légal

## Idées éducatives (pour v2, angle écoles/IUT)
- Contexte : éducation financière obligatoire en 4e dès sept. 2026 (Passeport EDUCFI) — bon timing marché
- Mode "mise en situation" façon jeu (scénarios de choix, conséquence visible dans le temps)
- Quiz de profil au démarrage (pré-remplit le simulateur)
- Glossaire intégré (tooltips sur termes techniques : PEA, flat tax, etc.)
- Carte de résultat partageable/exportable (levier viral)
- Mode "classe" pour présentation par un enseignant
- Cible : petits épargnants / étudiants / alternants (créneau ignoré par Yomoni, Nalo, Ramify)
- Différenciateur : transparence des calculs + crédibilité compta/fiscalité (parcours réel en cabinet)
- Monétisation envisagée (plus tard) : affiliation courtiers, ateliers IUT, ateliers B2B, freemium

## Suivi apprentissage Python
- ✅ Variables, opérateurs, `print()`
- ✅ Boucle `for` / `range()`
- ✅ `input()` et conversions de type (`float`, `int`)
- ✅ Fonctions (`def`, paramètres, appels multiples)
- ✅ Listes (`append`, `return`)
- ✅ Dictionnaires (`taux_par_profil[profil]`)
- ✅ Graphiques avec matplotlib (courbe simple + comparaison multi-profils)
- ✅ Streamlit : app interactive (`st.title`, `st.number_input`, `st.slider`, `st.selectbox`, `st.line_chart`)
- ✅ Pandas : DataFrame pour comparer les 3 profils sur un même graphique
- ✅ Déployé en ligne sur Streamlit Community Cloud (via GitHub) — site public et fonctionnel
- ✅ Conditions (`if`/`elif`/`else`) : logique fiscale par enveloppe (Livret/PEA/Assurance-vie)
- ✅ Suggestion d'enveloppe selon profil + horizon (encadré indicatif, pas un conseil personnalisé)
- ✅ Sliders de taux conditionnels au profil choisi
- ✅ Repères contextuels : taux réglementés en vigueur + inflation (`st.caption`)
- ✅ Notes pédagogiques par enveloppe : calcul de l'impôt + avantages/inconvénients (`st.expander`)
- ✅ Version à jour redéployée en ligne (GitHub → Streamlit Cloud, auto-redeploy)
- ✅ Faire évoluer le design : rebrand "Lucide", dark mode façon Finary, sidebar, cards, logo SVG, graphique corrigé (Claude Code)
- ✅ Plan du site v1 complet : formulaire, résultat+comparatif (onglets), tableau détaillé (expander), bloc pédagogique, disclaimer
- ✅ Fonction `simuler()` factorisée (réutilisée pour tableau + comparatif)
- ⏳ Versements variables (v2, mentionné dans spec)
- ⏳ Idées éducatives/ludiques (quiz profil, glossaire, carte partageable, mode classe) — prêtes à lancer
