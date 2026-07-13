import streamlit as st
import re
import random
import unicodedata


def sans_accents(texte: str) -> str:
    """Enlève les accents pour rendre le matching insensible aux accents."""
    return "".join(
        c for c in unicodedata.normalize("NFKD", texte)
        if not unicodedata.combining(c)
    )

# ─────────────────────────────────────────────
#  CONFIGURATION DE LA PAGE
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Chatbot BRVM",
    page_icon="💹",
    layout="centered"
)

# ─────────────────────────────────────────────
#  LOGO
#  Place le fichier logo (ex: logo_brvm.png) à côté de ce script,
#  ou dans un sous-dossier "assets/", et ajuste LOGO_PATH si besoin.
# ─────────────────────────────────────────────
import os

LOGO_PATH = "logo_brvm.jpg"

if os.path.exists(LOGO_PATH):
    col_logo, col_title = st.columns([1, 4])
    with col_logo:
        st.image(LOGO_PATH, width=90)
    with col_title:
        st.markdown("### Chatbot BRVM")
else:
    st.title("💹 Chatbot BRVM")

# ─────────────────────────────────────────────
#  MOTEUR DE RÈGLES (mots-clés / regex)
#  Format : (motif_regex, [liste de réponses possibles])
#  IMPORTANT : le motif fourre-tout (.*) doit rester en DERNIER
# ─────────────────────────────────────────────
PAIRS = [
    (r"(bonjour|salut|hello|bonsoir)",
        ["Bonjour, bienvenue ! Je suis le chatbot de la BRVM, posez-moi vos questions.",
         "Salut, bienvenue ! Comment puis-je vous aider ?",
         "Bonjour, comment puis-je vous aider ?"]),

    (r"c'?est quoi la brvm\??",
        ["La BRVM est la Bourse Régionale des Valeurs Mobilières, commune aux 8 pays de l'UEMOA. C'est Lieu où se rencontrent l'offre et la demande de valeurs mobilières"]),

    (r"ou se trouve la brvm\??|où se trouve la brvm\??",
        ["Le siège de la BRVM est situé à Abidjan, en Côte d'Ivoire, avec des antennes de représentation dans les différents pays de l'UEMOA."]),

    (r"comment investir a la brvm|comment investir à la brvm\??",
        ["Pour investir à la BRVM, vous devez passer par une SGI (Société de Gestion et d'Intermédiation). Vous pourrez ensuite investir sur des actions ou des obligations."]),

    (r"C'est quoi une (SGI)\??",
        ["Sociéte de gestion et d'intermediation,sociéte agréée par le CREPMF et habilitéé à effectuer l'activité d'intermediation financière sur la BRVM"]),

    (r"c'?est quoi une action\??",
        ["Valeur mobilière représentant une part de capital d'une société. C’est un titre de propriété."]),

    (r"C'est quoi Un actionnaire\??",
        ["Le detenteur d'une action est appelé un actionnaire"]),

    (r"C'est quoi un ordre d'achat\??",
        ["Decision(ou requete) d'un investisseur portant sur l'acquisition de valeurs mobilières."]),

    (r"C'est un ordre de vente\??",
        ["Décision (ou requete) d'un investisseur portant sur la cession de valeurs mobilierès. "]),

    (r"Quels sont les indices de la BRVM\??",
     ["Les indices de la BRVM sont: le BRVM composite, le BRVM-10 , le BRVM-30 et le BRVM PRESTIGE"]),

    (r"Brvm-10\??",
     ["Indice representant la performance de l'ensemble du marché action de la BRVM"]),
    (r"BRVM Composite",
     ["Indice représentant la performance de l'ensemble du marché action de la BRVM"]),

    (r"Un indice boursier\??",
     ["indicateur de la performance d'un marché boursier ou d'un panier de titres"]),

    (r"Ou télécharger les rapports\??",
     ["Pour telecharger les rapport annuel rendez vous sur le site web dans la rubrique Rapport des societés cotées"]),


    (r"c'?est quoi une obligation\??",
        ["Valeur mobilière représentant une part de dette d'une société, de l'Etat, ou d’une collectivité locale."]),
    (r"C'est quoi un droit\??",
        ["Tritre conferant a un actionnaire ordinaire le droit d'acheter d'autres actions à un prix fixé à l'avance"]),

    (r"(?=.*sgi)(?=.*trouv)",
        ["Dans quel pays vous trouvez-vous\?"]),

    (r"Benin", ["SGI BENIN, AFRICABOURSE, AGI"]),
    (r"Burkina", ["CORIS BOURSE, SBIF, SA2IF"]),
    (r"Cote d'ivoire", ["Vous pouvez consulter la liste officielle et à jour des SGI en Côte d'Ivoire sur brvm.org (Annuaire Officiel de l'APSGI)."]),
    (r"Mali",["SGI MALI, CIFA BOURSE, GLOBAL CAPITAL"]),
    (r"Niger",["SGI NIGER"]),
    (r"Senegal",["CGF BOURSE,FGI"]),
    (r"Togo",["SGI TOGO, CGF BOURSE"]),
    (r"Guinée-Bissau",["Il y'a pas de SGI agrée pour le moment"]),

    (r"horaire|heure de cotation|quand.*cot",
        ["La BRVM cote du lundi au vendredi, de 9h00 à 15h30 (heure d'Abidjan), hors jours fériés."]),

    (r"merci",
        ["Je vous en prie !", "Avec plaisir !"]),

    (r"au revoir|bye|a bientot|à bientôt",
        ["Au revoir et à bientôt !"]),

    (r"(.*)",
        ["Désolé, je ne comprends pas votre question. Essayez de reformuler, ou demandez-moi ce qu'est la BRVM, une action, ou une obligation."]),
]

def trouver_reponse(message: str) -> str:
    """Parcourt les règles dans l'ordre et renvoie la première réponse qui matche."""
    message = sans_accents(message.strip().lower())
    for motif, reponses in PAIRS:
        motif_norm = sans_accents(motif)
        if re.fullmatch(motif_norm, message, re.IGNORECASE) or re.search(motif_norm, message, re.IGNORECASE):
            return random.choice(reponses)
    return "Désolé, je ne comprends pas votre question."

# ─────────────────────────────────────────────
#  ÉTAT DE LA CONVERSATION
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour 👋 Je suis le chatbot de la BRVM. Posez-moi une question (ex : *c'est quoi la BRVM ?*, *comment investir à la BRVM*, *horaires de cotation*, *Ou je peux trouver une SGI*)."}
    ]

# ─────────────────────────────────────────────
#  INTERFACE
# ─────────────────────────────────────────────
st.caption("Démo — moteur basé sur mots-clés (règles + regex). Version future : modèle plus intelligent.")

# Affichage de l'historique
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Suggestions rapides
st.write("**Suggestions :**")
cols = st.columns(3)
suggestions = ["C'est quoi la BRVM ?", "Comment investir à la BRVM ?", "Horaires de cotation"]
suggestion_clicked = None
for col, s in zip(cols, suggestions):
    if col.button(s):
        suggestion_clicked = s

# Zone de saisie
user_input = st.chat_input("Écrivez votre message...")

message_a_traiter = suggestion_clicked or user_input

if message_a_traiter:
    # Message utilisateur
    st.session_state.messages.append({"role": "user", "content": message_a_traiter})
    with st.chat_message("user"):
        st.markdown(message_a_traiter)

    # Réponse du bot
    reponse = trouver_reponse(message_a_traiter)
    st.session_state.messages.append({"role": "assistant", "content": reponse})
    with st.chat_message("assistant"):
        st.markdown(reponse)

    st.rerun()