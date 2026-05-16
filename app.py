import streamlit as st
import json
import random
import re
from collections import OrderedDict
from pathlib import Path

import markdown as md_lib


def preprocess_inline_numbered(text: str) -> str:
    """Convert inline '(1) ... (2) ... (3) ...' patterns into a real markdown numbered list."""
    if not text:
        return ''
    paragraphs = re.split(r'\n{2,}', text)
    out = []
    for paragraph in paragraphs:
        marker_re = re.compile(r'(^|\s)\((\d+)\)\s+')
        markers = [(m.start() + len(m.group(1)), m.end(), int(m.group(2))) for m in marker_re.finditer(paragraph)]
        if len(markers) < 2 or any(m[2] != i + 1 for i, m in enumerate(markers)):
            out.append(paragraph)
            continue
        head = paragraph[:markers[0][0]].strip()
        items = []
        for i, (_, item_start, num) in enumerate(markers):
            item_end = markers[i + 1][0] if i + 1 < len(markers) else len(paragraph)
            item = paragraph[item_start:item_end].strip().rstrip('.;,')
            items.append(f'{num}. {item}')
        block = ((head + '\n\n') if head else '') + '\n'.join(items)
        out.append(block)
    return '\n\n'.join(out)


def render_markdown(text: str) -> str:
    """Convert markdown text to HTML, preprocessing inline numbered lists."""
    if not text:
        return ''
    processed = preprocess_inline_numbered(text)
    return md_lib.markdown(
        processed,
        extensions=['fenced_code', 'tables', 'nl2br', 'sane_lists'],
    )

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

    .answer-box p,
    .justification-box p {
        margin: 0 0 0.75rem 0;
    }

    .answer-box p:last-child,
    .justification-box p:last-child {
        margin-bottom: 0;
    }

    .answer-box ol,
    .answer-box ul,
    .justification-box ol,
    .justification-box ul {
        margin: 0.5rem 0 0.75rem 1.5rem;
        padding-left: 0.5rem;
    }

    .answer-box li,
    .justification-box li {
        margin-bottom: 0.4rem;
    }

    .answer-box strong,
    .justification-box strong {
        color: #000;
        font-weight: 600;
    }

    .answer-box code,
    .justification-box code {
        background: #e5e2cf;
        color: #b91c1c !important;
        padding: 0.15rem 0.4rem;
        border-radius: 4px;
        font-size: 0.9em;
    }

    .answer-box pre,
    .justification-box pre {
        background: #1f2937 !important;
        color: #f9fafb !important;
        padding: 1rem;
        border-radius: 6px;
        overflow-x: auto;
        margin: 0.75rem 0;
        line-height: 1.5;
    }

    .answer-box pre code,
    .justification-box pre code {
        background: transparent !important;
        color: #f9fafb !important;
        padding: 0;
    }

    .answer-box h1, .answer-box h2, .answer-box h3, .answer-box h4,
    .justification-box h1, .justification-box h2, .justification-box h3, .justification-box h4 {
        color: #000 !important;
        margin: 0.75rem 0 0.5rem;
    }

    .answer-box table,
    .justification-box table {
        border-collapse: collapse;
        margin: 0.75rem 0;
        width: 100%;
    }

    .answer-box th, .answer-box td,
    .justification-box th, .justification-box td {
        border: 1px solid #d1d5db;
        padding: 0.5rem 0.75rem;
        text-align: left;
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

if 'recent_questions' not in st.session_state:
    # Liste de dicts {set_id, theme_name, index, question, qid}, plus récent en tête
    st.session_state.recent_questions = []


def record_recent_question(set_id, theme_name, index, question_obj):
    """Ajoute la question courante en tête de la liste récente (dédoublonne, cap à 10)."""
    qid = question_obj.get("id")
    entry = {
        "set_id": set_id,
        "theme_name": theme_name,
        "index": index,
        "question": question_obj.get("question", ""),
        "qid": qid,
    }
    recent = st.session_state.recent_questions
    # Dédoublonne par qid (fallback sur tuple identifiant)
    def same(e):
        if qid is not None:
            return e.get("qid") == qid
        return (e["set_id"], e["theme_name"], e["index"]) == (set_id, theme_name, index)

    recent = [e for e in recent if not same(e)]
    recent.insert(0, entry)
    st.session_state.recent_questions = recent[:10]

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

ALL_SETS_KEY = "all"
ALL_SETS_LABEL = "Tous les sets"


def merge_all_sets(sets_dict):
    """Fusionne les thèmes de tous les sets en un seul dict {theme_name: [questions...]}."""
    merged = OrderedDict()
    for set_id in SET_LABELS:
        for theme_name, qs in sets_dict.get(set_id, {}).items():
            merged.setdefault(theme_name, []).extend(qs)
    return merged


def get_themes_for_set(set_id):
    if set_id == ALL_SETS_KEY:
        return merge_all_sets(st.session_state.sets)
    return st.session_state.sets.get(set_id, {})


# Sélection du set
st.markdown("### Sélectionnez un set")
set_entries = list(SET_LABELS.items()) + [(ALL_SETS_KEY, ALL_SETS_LABEL)]
set_cols = st.columns(len(set_entries))
for idx, (set_id, set_label) in enumerate(set_entries):
    themes_for_count = get_themes_for_set(set_id)
    total = sum(len(qs) for qs in themes_for_count.values())
    with set_cols[idx]:
        if st.button(
            f"{set_label}\n({total})",
            key=f"set_{set_id}",
            use_container_width=True,
            type="primary" if st.session_state.current_set == set_id else "secondary",
        ):
            st.session_state.current_set = set_id
            st.session_state.current_theme = None
            st.session_state.current_questions = []
            st.session_state.current_question_index = 0
            st.session_state.show_answer = False

# Sélection du thème (filtré par set)
if st.session_state.current_set is not None:
    st.markdown("---")
    if st.session_state.current_set == ALL_SETS_KEY:
        set_label = ALL_SETS_LABEL
    else:
        set_label = SET_LABELS.get(st.session_state.current_set, "")
    st.markdown(f"### Thèmes — {set_label}")

    themes_dict = get_themes_for_set(st.session_state.current_set)
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
                    use_container_width=True,
                    type="primary" if st.session_state.current_theme == theme_name else "secondary",
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

        # Enregistre la question courante dans l'historique récent.
        # Si on est en vue "Tous les sets", on remonte au set d'origine via le champ `set` de la question.
        recent_set_id = current_q.get("set", st.session_state.current_set)
        recent_theme_name = current_q.get("name", st.session_state.current_theme)
        # Index dans la liste du set/theme d'origine (pas dans la liste fusionnée)
        original_theme_qs = st.session_state.sets.get(recent_set_id, {}).get(recent_theme_name, [])
        try:
            recent_index = original_theme_qs.index(current_q)
        except ValueError:
            recent_index = st.session_state.current_question_index
        record_recent_question(
            recent_set_id,
            recent_theme_name,
            recent_index,
            current_q,
        )

        # Compteur
        st.markdown(
            f'<div class="counter">Question {st.session_state.current_question_index + 1} sur {len(questions)}</div>',
            unsafe_allow_html=True
        )

        # Navigation rapide entre questions
        nav_key_prefix = f"navq_{st.session_state.current_set}_{st.session_state.current_theme}"
        total_q = len(questions)
        per_row = 10
        for row_start in range(0, total_q, per_row):
            row_count = min(per_row, total_q - row_start)
            nav_cols = st.columns(per_row)
            for offset in range(row_count):
                idx = row_start + offset
                with nav_cols[offset]:
                    is_active = idx == st.session_state.current_question_index
                    if st.button(
                        f"{idx + 1}",
                        key=f"{nav_key_prefix}_{idx}",
                        use_container_width=True,
                        type="primary" if is_active else "secondary",
                    ):
                        st.session_state.current_question_index = idx
                        st.session_state.show_answer = False
                        st.rerun()

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
                f'<div class="answer-box">{render_markdown(current_q["answer"])}</div>',
                unsafe_allow_html=True
            )

        # Justification (toujours affichée en bas)
        justification = current_q.get("justification")
        if justification:
            st.markdown(
                f'<div class="justification-box">'
                f'<div class="justification-title">Justification</div>'
                f'{render_markdown(justification)}'
                f'</div>',
                unsafe_allow_html=True
            )
elif st.session_state.current_set is None:
    st.info("👆 Sélectionnez un set pour commencer")
else:
    st.info("👆 Sélectionnez un thème pour commencer")


# Questions récentes
st.markdown("---")
st.markdown("### 🕘 Questions récentes")

# La question courante (si affichée) est toujours en tête de la liste car enregistrée à chaque rerun.
# On l'exclut pour ne montrer que les questions précédentes.
recent_all = st.session_state.recent_questions
if st.session_state.current_theme and recent_all:
    recent_to_show = recent_all[1:4]
else:
    recent_to_show = recent_all[:3]

if not recent_to_show:
    st.caption("Aucune question récente. Navigue dans les sets pour remplir l'historique.")
else:
    for i, r in enumerate(recent_to_show):
        # Résoudre le label du set (peut venir d'un set fusionné: ignorer "all")
        set_label = SET_LABELS.get(r["set_id"], "?")
        btn_label = f"[{set_label} • {r['theme_name']}] {r['question']}"
        if st.button(
            btn_label,
            key=f"recent_{i}_{r['set_id']}_{r['theme_name']}_{r['index']}",
            use_container_width=True,
        ):
            # Jump direct vers la question via le set original (pas "all")
            target_set = r["set_id"] if r["set_id"] in st.session_state.sets else st.session_state.current_set
            theme_questions = st.session_state.sets.get(target_set, {}).get(r["theme_name"], [])
            if theme_questions:
                st.session_state.current_set = target_set
                st.session_state.current_theme = r["theme_name"]
                st.session_state.current_questions = theme_questions
                # Resécuriser l'index si la liste a changé
                st.session_state.current_question_index = min(r["index"], len(theme_questions) - 1)
                st.session_state.show_answer = False
                st.rerun()


# Recherche mot-clef dans les titres de questions
st.markdown("---")
st.markdown("### 🔎 Rechercher dans les questions")

search_query = st.text_input(
    "Mots-clefs",
    key="search_query",
    placeholder="Tape un ou plusieurs mots-clefs...",
    label_visibility="collapsed",
)

if search_query and search_query.strip():
    terms = [t.lower() for t in search_query.split() if t.strip()]

    # Recompose un index plat de toutes les questions avec leur set/theme
    all_results = []
    for set_id, themes in st.session_state.sets.items():
        for theme_name, qs in themes.items():
            for idx_in_theme, q in enumerate(qs):
                title = (q.get("question") or "").lower()
                if all(t in title for t in terms):
                    all_results.append({
                        "set_id": set_id,
                        "theme_name": theme_name,
                        "index": idx_in_theme,
                        "question": q.get("question", ""),
                    })

    st.markdown(f"**{len(all_results)} résultat(s)**")

    if all_results:
        for i, r in enumerate(all_results):
            set_label = SET_LABELS.get(r["set_id"], "?")
            btn_label = f"[{set_label} • {r['theme_name']}] {r['question']}"
            if st.button(
                btn_label,
                key=f"search_result_{i}_{r['set_id']}_{r['theme_name']}_{r['index']}",
                use_container_width=True,
            ):
                st.session_state.current_set = r["set_id"]
                st.session_state.current_theme = r["theme_name"]
                st.session_state.current_questions = st.session_state.sets[r["set_id"]][r["theme_name"]]
                st.session_state.current_question_index = r["index"]
                st.session_state.show_answer = False
                st.rerun()
