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
from definitions_data import DEFINITIONS_BRVM

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
        ["La BRVM est la Bourse Régionale des Valeurs Mobilières, commune aux 8 pays de l'UEMOA. C'est le lieu ou s'echange les actions et les oblogations"]),

    (r"ou se trouve la brvm\??|où se trouve la brvm\??",
        ["Le siège de la BRVM est situé à Abidjan, en Côte d'Ivoire, avec des antennes de représentation dans les différents pays de l'UEMOA."]),

    (r"comment investir a la brvm|comment investir à la brvm",
        ["Pour investir à la BRVM, vous devez passer par une SGI (Société de Gestion et d'Intermédiation). Vous pourrez ensuite investir sur des actions ou des obligations."]),

    (r"c'?est quoi une action\??",
        ["Une action représente une part du capital d'une entreprise. En la détenant, vous devenez actionnaire de cette entreprise."]),


    (r"Quels sont les indices de la BRVM \?",
     ["Les indices de la BRVM sont: le BRVM composite, le BRVM-30 et le BRVM PRESTIGE"]),

    (r"Ou télécharger les rapports \?",
     ["Pour telecharger les rapport annuel rendez vous sur le site web dans la rubrique Rapport des societés cotées"]),


    (r"c'?est quoi une obligation\??",
        ["Une obligation est un titre de créance : en l'achetant, vous prêtez de l'argent à une entreprise ou un État, qui vous rembourse avec des intérêts."]),

    (r"(?=.*sgi)(?=.*trouv)",
        ["Dans quel pays vous trouvez-vous\?"]),

    (r"^(je suis (au|en|a|à)\s+)?benin\s*\??$", ["SGI BENIN, AFRICABOURSE, AGI"]),
    (r"^(je suis (au|en|a|à)\s+)?burkina(\s*faso)?\s*\??$", ["CORIS BOURSE, SBIF, SA2IF"]),
    (r"^(je suis (au|en|a|à)\s+)?cote d'?ivoire\s*\??$",
        ["Vous pouvez consulter la liste officielle et à jour des SGI en Côte d'Ivoire sur brvm.org (Annuaire Officiel de l'APSGI)."]),
    (r"^(je suis (au|en|a|à)\s+)?mali\s*\??$", ["SGI MALI, CIFA BOURSE, GLOBAL CAPITAL"]),
    (r"^(je suis (au|en|a|à)\s+)?niger\s*\??$", ["SGI NIGER"]),
    (r"^(je suis (au|en|a|à)\s+)?senegal\s*\??$", ["CGF BOURSE,FGI"]),
    (r"^(je suis (au|en|a|à)\s+)?togo\s*\??$", ["SGI TOGO, CGF BOURSE"]),
    (r"^(je suis (au|en|a|à)\s+)?guinee-?bissau\s*\??$", ["Il y'a pas de SGI agrée pour le moment"]),

    (r"horaire|heure de cotation|quand.*cot",
        ["La BRVM cote du lundi au vendredi, de 9h00 à 15h30 (heure d'Abidjan), hors jours fériés."]),

    (r"merci",
        ["Je vous en prie !", "Avec plaisir !"]),

    (r"au revoir|bye|a bientot|à bientôt",
        ["Au revoir et à bientôt !"]),
]

def trouver_reponse(message: str):
    """Parcourt les règles dans l'ordre et renvoie la première réponse qui matche.
    Renvoie None si aucune règle ne matche (pour déclencher le fallback IA)."""
    message = sans_accents(message.strip().lower())
    for motif, reponses in PAIRS:
        motif_norm = sans_accents(motif)
        if re.fullmatch(motif_norm, message, re.IGNORECASE) or re.search(motif_norm, message, re.IGNORECASE):
            return random.choice(reponses)
    return None


# ─────────────────────────────────────────────
#  LEXIQUE DE DÉFINITIONS BRVM (issu du fichier Word)
# ─────────────────────────────────────────────
def _preparer_index_lexique():
    """Construit une liste de (mots-clés normalisés, terme original, définition),
    triée pour que les termes les plus longs/spécifiques soient testés en premier."""
    index = []
    for terme, definition in DEFINITIONS_BRVM.items():
        cles = {sans_accents(terme.lower())}
        # Sigle entre parenthèses, ex: "FONDS COMMUN DE PLACEMENT (FCP)" -> "fcp"
        m = re.search(r"\(([A-Za-zÀ-ÿ]{2,8})\)", terme)
        if m:
            cles.add(sans_accents(m.group(1).lower()))
        # Sigle placé AVANT la parenthèse, ex: "PER (Price Earning Ratio) – ..." -> "per"
        avant_parenthese = terme.split("(")[0].strip()
        if avant_parenthese and len(avant_parenthese) <= 8 and " " not in avant_parenthese:
            cles.add(sans_accents(avant_parenthese.lower()))
        index.append((cles, terme, definition))
    # Termes les plus longs en premier pour éviter qu'un terme court («action»)
    # n'intercepte une question visant un terme plus spécifique («action privilégiée»)
    index.sort(key=lambda x: max(len(c) for c in x[0]), reverse=True)
    return index

_INDEX_LEXIQUE = _preparer_index_lexique()

def chercher_definition(message: str):
    """Cherche si le message correspond à un terme du lexique BRVM (mot entier, insensible aux accents/casse)."""
    message_norm = sans_accents(message.strip().lower())
    for cles, terme, definition in _INDEX_LEXIQUE:
        for cle in cles:
            if re.search(r"(?<!\w)" + re.escape(cle) + r"(?!\w)", message_norm):
                return f"**{terme}** — {definition}"
    return None


# ─────────────────────────────────────────────
#  FALLBACK CLAUDE API (avec mode test)
# ─────────────────────────────────────────────
MODE_TEST = False  # ⚠️ Passe à True si tu veux retester sans consommer de crédits API
MODE_DEBUG = False  # ⚠️ Passe à True temporairement si tu dois déboguer la détection de la clé API

SYSTEME_PROMPT = (
    "Tu es l'assistant virtuel officiel de la BRVM (Bourse Régionale des "
    "Valeurs Mobilières). Réponds de façon claire, concise et professionnelle "
    "en français, uniquement sur des sujets liés à la bourse, aux marchés "
    "financiers de l'UEMOA, à l'investissement ou à la BRVM."
)

def obtenir_cle_api():
    """Récupère la clé API : d'abord via st.secrets (Streamlit Cloud),
    sinon via la variable d'environnement (test en local)."""
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except (KeyError, FileNotFoundError):
        return os.environ.get("ANTHROPIC_API_KEY")


def appeler_claude_api(question: str) -> str:
    """Appelle l'API Claude en fallback quand le regex ne trouve rien.
    En MODE_TEST, simule la réponse sans consommer de crédits."""
    if MODE_TEST:
        return (f"🤖 [Réponse simulée IA] Voici ce que je répondrais à : "
                f"« {question} » (mode test actif, aucune requête API envoyée)")

    import anthropic

    api_key = obtenir_cle_api()
    if not api_key:
        return "⚠️ Clé API non configurée. Impossible de contacter l'assistant IA."

    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=300,
            system=SYSTEME_PROMPT,
            messages=[{"role": "user", "content": question}]
        )
        return response.content[0].text
    except Exception as e:
        return f"⚠️ Erreur lors de l'appel à l'API Claude : {e}"


def generer_reponse(message: str) -> str:
    """Ordre de priorité : 1) règles regex, 2) lexique de définitions BRVM, 3) fallback Claude."""
    reponse_regex = trouver_reponse(message)
    if reponse_regex:
        return reponse_regex

    reponse_lexique = chercher_definition(message)
    if reponse_lexique:
        return reponse_lexique

    return appeler_claude_api(message)

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
st.caption("Démo — moteur basé sur mots-clés (règles + regex), avec bascule vers l'IA en cas de non-reconnaissance.")

with st.sidebar:
    if MODE_TEST:
        st.warning("🧪 Mode test actif : le fallback IA est simulé (pas d'appel API réel).")

    if MODE_DEBUG:
        cle_debug = obtenir_cle_api()
        if cle_debug:
            st.info(f"🔑 Clé détectée : {cle_debug[:10]}...{cle_debug[-4:]} (longueur {len(cle_debug)})")
        else:
            st.error("🔑 Aucune clé API détectée.")

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

    # Réponse du bot (règles d'abord, puis fallback IA si rien ne matche)
    reponse = generer_reponse(message_a_traiter)
    st.session_state.messages.append({"role": "assistant", "content": reponse})
    with st.chat_message("assistant"):
        st.markdown(reponse)

    st.rerun()