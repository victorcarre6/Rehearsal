import streamlit as st
import json
import random
from pathlib import Path

# Configuration de la page
st.set_page_config(
    page_title="Rehearsal",
    page_icon="",
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
        background: var(--primary);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }

    .main-header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }

    .main-header p {
        font-size: 1rem;
        opacity: 0.9;
        margin: 0;
    }

    /* Style des cartes */
    .card {
        background: var(--background-main);
        border-radius: 10px;
        padding: 2rem;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
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

    /* Tag filters */
    div[data-testid="stMultiSelect"] {
        margin-bottom: 1rem;
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

    /* Rendre toutes les surfaces non-card blanches */
    .stMarkdown, .stText, .stSelectbox, .stMultiSelect, .stButton, .stNumberInput {
        background-color: #F2F0E3 !important;
    }
</style>
""", unsafe_allow_html=True)

# Fonction pour charger les questions
@st.cache_data
def load_questions():
    """Charge les questions depuis le fichier JSON"""
    questions_file = Path(__file__).parent / "questions.json"
    with open(questions_file, 'r', encoding='utf-8') as f:
        return json.load(f)

# Définition des tags disponibles
AVAILABLE_TAGS = {
    'Data Science': ['data science', 'data scientist', 'analysis', 'analytics'],
    'Machine Learning': ['machine learning', 'ml', 'supervised', 'unsupervised', 'classification', 'regression', 'clustering'],
    'Deep Learning': ['deep learning', 'neural network', 'cnn', 'rnn', 'lstm', 'backpropagation', 'gradient'],
    'Statistics': ['statistics', 'statistical', 'probability', 'distribution', 'hypothesis', 'p-value', 'variance', 'bias'],
    'Python': ['python', 'pandas', 'numpy'],
    'NLP': ['nlp', 'natural language', 'text', 'tf-idf', 'language processing'],
    'Computer Vision': ['cnn', 'convolutional', 'image', 'vision', 'pooling'],
    'SQL': ['sql', 'database', 'query'],
    'Algorithms': ['algorithm', 'svm', 'decision tree', 'naive bayes', 'random forest', 'k-nn']
}

def question_matches_tags(question, selected_tags):
    """Vérifie si une question correspond aux tags sélectionnés"""
    if not selected_tags:
        return True

    q_text = (question['question'] + ' ' + question['answer']).lower()

    for tag_name in selected_tags:
        keywords = AVAILABLE_TAGS.get(tag_name, [])
        if any(keyword.lower() in q_text for keyword in keywords):
            return True
    return False

def filter_questions_by_tags(themes, selected_tags):
    """Filtre les thèmes et questions par tags"""
    if not selected_tags:
        return themes

    filtered_themes = []
    for theme in themes:
        filtered_questions = [q for q in theme['questions'] if question_matches_tags(q, selected_tags)]
        if filtered_questions:
            filtered_themes.append({
                **theme,
                'questions': filtered_questions
            })
    return filtered_themes

# Initialisation de l'état de session
if 'questions_data' not in st.session_state:
    st.session_state.questions_data = load_questions()

if 'current_theme' not in st.session_state:
    st.session_state.current_theme = None

if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0

if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False

if 'current_questions' not in st.session_state:
    st.session_state.current_questions = []

# Header
st.markdown("""
<div class="main-header">
    <h1>Rehearsal</h1>
</div>
""", unsafe_allow_html=True)

# Section des filtres
st.markdown("### Filtrer par domaine")
selected_tags = st.multiselect(
    "Sélectionnez un ou plusieurs domaines",
    options=list(AVAILABLE_TAGS.keys()),
    default=[],
    help="Filtrez les questions par domaine technique"
)

# Filtrer les thèmes selon les tags
filtered_themes = filter_questions_by_tags(
    st.session_state.questions_data['themes'],
    selected_tags
)

# Section de sélection du thème
st.markdown("###Sélectionner un thème")

# Créer des colonnes pour les boutons de thème
cols = st.columns(3)
for idx, theme in enumerate(filtered_themes):
    col = cols[idx % 3]
    with col:
        if st.button(
            f"{theme['name']} ({len(theme['questions'])})",
            key=f"theme_{theme['id']}",
            use_container_width=True
        ):
            st.session_state.current_theme = theme
            st.session_state.current_questions = theme['questions']
            st.session_state.current_question_index = 0
            st.session_state.show_answer = False

# Affichage des questions
if st.session_state.current_theme:
    st.markdown("---")

    questions = st.session_state.current_questions

    if not questions:
        st.info("Aucune question disponible pour ce thème avec les filtres sélectionnés.")
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
            if st.button("Afficher la réponse", use_container_width=True):
                st.session_state.show_answer = True

        with col2:
            if st.button("Question suivante", use_container_width=True, key="next_question"):
                # Sélectionner une question aléatoire différente de l'actuelle
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
else:
    st.info("Sélectionnez un thème pour commencer")

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #6b7280; font-size: 0.9rem;">Rehearsal</p>',
    unsafe_allow_html=True
)
