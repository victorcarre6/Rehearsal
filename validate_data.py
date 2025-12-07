#!/usr/bin/env python3
"""
Script de validation du fichier questions.json
Vérifie l'intégrité des données et affiche des statistiques
"""

import json
import sys
from collections import Counter

def validate_questions_json(filepath='questions.json'):
    """Valide la structure du fichier questions.json"""
    
    print("🔍 Validation de questions.json...\n")
    
    # Charger le JSON
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Erreur lors du chargement: {e}")
        return False
    
    errors = []
    warnings = []
    
    # Vérifier la structure principale
    if 'questions' not in data:
        errors.append("Clé 'questions' manquante")
    if 'themes' not in data:
        errors.append("Clé 'themes' manquante")
    
    if errors:
        for error in errors:
            print(f"❌ {error}")
        return False
    
    # Créer un mapping des questions
    questions_by_id = {}
    duplicate_ids = []
    
    for q in data['questions']:
        if 'id' not in q:
            errors.append(f"Question sans ID: {q.get('question', 'unknown')[:50]}")
            continue
        
        qid = q['id']
        if qid in questions_by_id:
            duplicate_ids.append(qid)
        questions_by_id[qid] = q
        
        if 'question' not in q:
            errors.append(f"Question {qid} sans champ 'question'")
        if 'answer' not in q:
            errors.append(f"Question {qid} sans champ 'answer'")
    
    if duplicate_ids:
        errors.append(f"IDs dupliqués: {duplicate_ids}")
    
    # Vérifier les thèmes
    theme_ids = set()
    all_question_refs = []
    
    for theme in data['themes']:
        if 'id' not in theme:
            errors.append(f"Thème sans ID: {theme.get('name', 'unknown')}")
            continue
        
        theme_id = theme['id']
        if theme_id in theme_ids:
            errors.append(f"ID de thème dupliqué: {theme_id}")
        theme_ids.add(theme_id)
        
        if 'name' not in theme:
            errors.append(f"Thème {theme_id} sans nom")
        if 'question_ids' not in theme:
            errors.append(f"Thème {theme_id} sans question_ids")
            continue
        
        # Vérifier que tous les question_ids existent
        for qid in theme['question_ids']:
            all_question_refs.append(qid)
            if qid not in questions_by_id:
                errors.append(f"Thème '{theme.get('name')}': question_id {qid} introuvable")
    
    # Vérifier les questions orphelines
    referenced_questions = set(all_question_refs)
    all_questions = set(questions_by_id.keys())
    orphan_questions = all_questions - referenced_questions
    
    if orphan_questions:
        warnings.append(f"Questions non utilisées: {sorted(orphan_questions)}")
    
    # Afficher les résultats
    if errors:
        print("❌ ERREURS DÉTECTÉES:\n")
        for error in errors:
            print(f"  • {error}")
        print()
        return False
    
    if warnings:
        print("⚠️  AVERTISSEMENTS:\n")
        for warning in warnings:
            print(f"  • {warning}")
        print()
    
    # Statistiques
    print("✅ VALIDATION RÉUSSIE!\n")
    print("📊 STATISTIQUES:")
    print(f"  • {len(questions_by_id)} questions uniques")
    print(f"  • {len(data['themes'])} thèmes")
    print(f"  • {len(all_question_refs)} références totales")
    print(f"  • {len(all_question_refs) - len(questions_by_id)} questions partagées entre thèmes")
    
    # Distribution
    print("\n📚 DISTRIBUTION PAR THÈME:")
    for theme in data['themes']:
        print(f"  • {len(theme['question_ids']):3d} questions - {theme['name']}")
    
    # Questions les plus partagées
    question_counts = Counter(all_question_refs)
    most_shared = question_counts.most_common(5)
    
    print("\n🔗 QUESTIONS LES PLUS PARTAGÉES:")
    for qid, count in most_shared:
        if count > 1:
            q = questions_by_id[qid]
            preview = q['question'][:50] + "..."
            print(f"  • [{count} thèmes] Q{qid}: {preview}")
    
    return True

if __name__ == '__main__':
    success = validate_questions_json()
    sys.exit(0 if success else 1)
