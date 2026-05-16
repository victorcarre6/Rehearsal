import streamlit as st
import json
import random
from collections import OrderedDict
from pathlib import Path

# Configuration de la page
st.set_page_config(
    page_title="Rehearsal",
    layout="wide"
)

# CSS personnalisé
st.markdown("""
<style>
    :root {
        --primary: #707C42;
        --background-main: #F2F0E3;
    }

    body {
        background: var(--background-main);
    }

    /* Style du header */
    .main-header {
        padding: 2rem;
        margin-bottom: 2rem;
        text-align: center;
    }

    .main-header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
        color: var(--primary);
    }

    .main-header p {
        font-size: 1rem;
        opacity: 0.9;
        margin: 0;
    }

    /* Forcer le texte Streamlit en noir */
    h1, h2, h3, h4, h5, h6,
    .stMarkdown, .stText, label, p, span {
        color: #000000 !important;
    }

    /* Style des questions */
    .question-box {
        background: var(--background-main);
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667236;
        margin: 1rem 0;
    }

    .question-text {
        font-size: 1.3rem;
        font-weight: 600;
        color: black;
        line-height: 1.6;
    }

    .answer-box {
        background: var(--background-main);
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        margin-top: 1rem;
        line-height: 1.7;
        color: black;
    }

    .justification-box {
        background: #ECE9D4;
        padding: 1.25rem;
        border-radius: 8px;
        border-left: 4px solid #B5A642;
        margin-top: 1.5rem;
        line-height: 1.6;
        color: black;
        font-size: 0.95rem;
    }

    .justification-title {
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: #6B5E20;
    }

    .counter {
        font-size: 0.9rem;
        color: black;
        font-weight: 500;
        margin-bottom: 1rem;
    }

    /* Boutons */
    .stButton button {
        background: var(--primary);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.2s;
    }

    .stButton button:hover {
        background: #5F6A37;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(102, 114, 54, 0.2);
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Espacement */
    .block-container {
        padding-top: 2rem;
        max-width: 1000px;
    }

    /* Fond principal de l'application */
    .stApp {
        background-color: #F2F0E3 !important;
    }

    /* Fond de la zone principale */
    [data-testid="stAppViewContainer"] {
        background-color: #F2F0E3 !important;
    }

    /* Fond du bloc central */
    .block-container {
        background-color: #F2F0E3 !important;
    }

    /* Fond de la sidebar */
    [data-testid="stSidebar"] {
        background-color: #F2F0E3 !important;
    }

    /* Couleur du texte dans les codeblocks et callouts */
    pre, code, pre * , code * {
        color: white !important;
    }

    /* Fond des codeblocks pour contraste */
    pre {
        background-color: #707C42 !important;
    }
</style>
""", unsafe_allow_html=True)

# Mapping des sets vers leur libellé
SET_LABELS = OrderedDict([
    (1, "Générales"),
    (2, "Spécifiques"),
    (3, "Avancées"),
    (4, "Programmation"),
])


@st.cache_data
def load_questions():
    """Charge les questions et les regroupe par set puis par thème (champ `name`)."""
    questions_file = Path(__file__).parent / "questions.json"
    with open(questions_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    sets = OrderedDict()
    for set_id in SET_LABELS:
        sets[set_id] = OrderedDict()

    for q in data['questions']:
        set_id = q.get('set')
        theme_name = q.get('name', 'Autres')
        if set_id not in sets:
            sets[set_id] = OrderedDict()
        sets[set_id].setdefault(theme_name, []).append(q)

    return sets


# Initialisation de l'état de session
if 'sets' not in st.session_state:
    st.session_state.sets = load_questions()

if 'current_set' not in st.session_state:
    st.session_state.current_set = None

if 'current_theme' not in st.session_state:
    st.session_state.current_theme = None

if 'current_questions' not in st.session_state:
    st.session_state.current_questions = []

if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0

if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False

# Header
st.markdown("""
<div class="main-header">
    <h1>Rehearsal</h1>
</div>
""", unsafe_allow_html=True)

# GIF sous le titre
st.markdown("""
<div style="text-align: center; margin: 1rem 0 2rem 0;">
    <img src="https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExdzl5NzRlY3R3ajdqdDRyeXVrOGh6OG5zNWIxYzRpdjNyZ2k1eG5nYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/XbJYBCi69nyVOffLIU/giphy.gif"
         alt="Study animation"
         style="max-width: 400px; width: 100%; border-radius: 10px;"/>
</div>
""", unsafe_allow_html=True)

###

# Sélection du set
st.markdown("### Sélectionnez un set")
set_cols = st.columns(len(SET_LABELS))
for idx, (set_id, set_label) in enumerate(SET_LABELS.items()):
    total = sum(len(qs) for qs in st.session_state.sets.get(set_id, {}).values())
    with set_cols[idx]:
        if st.button(
            f"{set_label}\n({total})",
            key=f"set_{set_id}",
            use_container_width=True
        ):
            st.session_state.current_set = set_id
            st.session_state.current_theme = None
            st.session_state.current_questions = []
            st.session_state.current_question_index = 0
            st.session_state.show_answer = False

# Sélection du thème (filtré par set)
if st.session_state.current_set is not None:
    st.markdown("---")
    set_label = SET_LABELS.get(st.session_state.current_set, "")
    st.markdown(f"### Thèmes — {set_label}")

    themes_dict = st.session_state.sets.get(st.session_state.current_set, {})
    if not themes_dict:
        st.info("Aucun thème disponible pour ce set.")
    else:
        theme_names = list(themes_dict.keys())
        cols = st.columns(3)
        for idx, theme_name in enumerate(theme_names):
            col = cols[idx % 3]
            with col:
                if st.button(
                    f"{theme_name}\n({len(themes_dict[theme_name])})",
                    key=f"theme_{st.session_state.current_set}_{theme_name}",
                    use_container_width=True
                ):
                    st.session_state.current_theme = theme_name
                    st.session_state.current_questions = themes_dict[theme_name]
                    st.session_state.current_question_index = 0
                    st.session_state.show_answer = False

# Affichage des questions
if st.session_state.current_theme:
    st.markdown("---")
    questions = st.session_state.current_questions

    if not questions:
        st.info("Aucune question disponible pour ce thème.")
    else:
        current_q = questions[st.session_state.current_question_index]

        # Compteur
        st.markdown(
            f'<div class="counter">Question {st.session_state.current_question_index + 1} sur {len(questions)}</div>',
            unsafe_allow_html=True
        )

        # Question
        st.markdown(
            f'<div class="question-box"><div class="question-text">{current_q["question"]}</div></div>',
            unsafe_allow_html=True
        )

        # Boutons de contrôle
        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button("💡 Afficher la réponse", use_container_width=True):
                st.session_state.show_answer = True

        with col2:
            if st.button("➡️ Question suivante", use_container_width=True, key="next_question"):
                if len(questions) > 1:
                    new_index = st.session_state.current_question_index
                    while new_index == st.session_state.current_question_index:
                        new_index = random.randint(0, len(questions) - 1)
                    st.session_state.current_question_index = new_index
                else:
                    st.session_state.current_question_index = 0
                st.session_state.show_answer = False
                st.rerun()

        # Afficher la réponse si demandé
        if st.session_state.show_answer:
            st.markdown(
                f'<div class="answer-box">{current_q["answer"]}</div>',
                unsafe_allow_html=True
            )

        # Justification (toujours affichée en bas)
        justification = current_q.get("justification")
        if justification:
            st.markdown(
                f'<div class="justification-box">'
                f'<div class="justification-title">Justification</div>'
                f'{justification}'
                f'</div>',
                unsafe_allow_html=True
            )
elif st.session_state.current_set is None:
    st.info("👆 Sélectionnez un set pour commencer")
else:
    st.info("👆 Sélectionnez un thème pour commencer")
