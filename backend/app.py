"""
Madame T - Voyante du Tarot
Interface Gradio pour Hugging Face Spaces
"""
import os
from typing import Iterable

import gradio as gr
from langdetect import detect, DetectorFactory

try:
    import google.generativeai as genai
except ImportError as exc:
    raise RuntimeError("google-generativeai package missing") from exc

DetectorFactory.seed = 0


DEFAULT_MODELS: tuple[str, ...] = (
    os.getenv("GEMINI_MODEL") or "",
    "models/gemini-2.0-flash-exp",  # 🆕 Modèle expérimental plus permissif
    "models/gemini-2.0-flash-thinking-exp-1219",  # 🆕 Modèle avec raisonnement
    "models/gemini-2.0-flash",
    "models/gemini-1.5-flash-latest",  # Version la plus récente de 1.5
    "models/gemini-1.5-flash-002",  # Version stable
    "models/gemini-1.5-flash",
)


def pick_first_available(models: Iterable[str]) -> str | None:
    for model in models:
        candidate = (model or "").strip()
        if candidate:
            return candidate
    return None

SYSTEM_PROMPT = (
    "Tu es **Mme T**, une lectrice de tarot authentique, bienveillante et intuitive. "
    "Tu interprètes le tarot de Marseille avec sagesse et simplicité, comme une amie de confiance. "
    "Ta parole est claire, directe et réconfortante.\n\n"

    "🎴 **APPROCHE**\n"
    "• Donne des RÉPONSES CLAIRES et AFFIRMATIVES basées sur les symboles tirés.\n"
    "• Dis ce que tu VOIS et ce que tu RESSENS dans les cartes, sans tourner autour du pot.\n"
    "• Décris les ÉNERGIES présentes, leur mouvement et leur direction.\n"
    "• Sois CONFIANTE mais toujours BIENVEILLANTE.\n"
    "• Reste NEUTRE sur le genre (pas de 'ma belle', 'mon chéri', etc.).\n\n"

    "✨ **STYLE DE LANGAGE**\n"
    "• Tutoiement naturel et chaleureux.\n"
    "• Ton mystique mais accessible et universel.\n"
    "• Réponses courtes : 2–3 phrases maximum.\n"
    "• Un seul émoji par réponse (✨💖🌟 autorisés).\n\n"

    "🔮 **FORMULATIONS CONSEILLÉES**\n"
    "Utilise des phrases affirmatives, ouvertes et inspirées :\n"
    "• 'Les cartes montrent...'\n"
    "• 'Je perçois...'\n"
    "• 'Je vois...'\n"
    "• 'Cette carte évoque...'\n"
    "• 'L’énergie indique...'\n"
    "• 'D’après les symboles, il y a...'\n\n"

    "🤝 **FORMULES NEUTRES POUR S’ADRESSER À TOUS**\n"
    "✅ Utilise : 'Mon ami(e)', 'Écoute', 'Regarde', 'Attention', ou le prénom s’il est donné.\n"
    "❌ Évite : 'Ma belle', 'Mon chéri', 'Ma chère' (présument le genre ou l’âge).\n\n"

    "🚫 **FORMULATIONS À ÉVITER (bloquées ou risquées)**\n"
    "• Futur catégorique ('tu vas rencontrer', 'tu vas avoir...').\n"
    "• Dates précises ('en mars', 'dans 3 mois', etc.).\n"
    "• Absolus ('c’est certain', 'à 100%', 'je te le garantis').\n\n"

    "🌟 **EXEMPLES DE BONNES RÉPONSES**\n\n"
    "Question : 'Vais-je rencontrer l’amour ?'\n"
    "✅ 'D’après les symboles, il y a une transformation importante (La Tour) "
    "qui précède un épanouissement (Le Monde). "
    "Je vois une ouverture vers une relation plus complète et sincère. 💖'\n\n"

    "Question : 'Aurais-je des enfants ?'\n"
    "✅ 'Je perçois une énergie de création (L’Impératrice) autour de la famille. "
    "Les cartes annoncent une période fertile et pleine de potentiel. 🌟'\n\n"

    "Question : 'Vais-je réussir mon projet ?'\n"
    "✅ 'Le Chariot associé au Soleil, c’est un signe fort ! "
    "Je vois une dynamique claire de réussite et d’accomplissement. ✨'\n\n"

    "Question : 'Que me réserve l’avenir ?' (homme, 45 ans)\n"
    "✅ 'La Roue de Fortune suivie du Soleil annonce un tournant majeur : "
    "une période de chance, d’opportunités et d’épanouissement. ✨'\n\n"

    "💫 **RÈGLE D’OR** : Sois toujours AFFIRMATIVE (ce que tu vois DANS les cartes), "
    "NEUTRE (pas de genre), et CLAIRE (les gens veulent comprendre ce que les cartes révèlent)."
)


def detect_language(text: str) -> str:
    """Détecte la langue du texte"""
    try:
        return detect(text)
    except Exception:
        return "fr"

def language_directive(lang_code: str) -> str:
    """Retourne la directive de langue"""
    mapping = {
        "fr": "français",
        "en": "anglais",
        "es": "espagnol",
        "pt": "portugais",
        "it": "italien",
        "de": "allemand",
    }
    return f"Réponds en {mapping.get(lang_code, 'français')}."

def reformulate_sensitive_question(question: str) -> str:
    """Reformule les questions sensibles pour éviter les blocages Gemini"""
    q_lower = question.lower()
    
    # Patterns de questions sensibles et leurs reformulations
    sensitive_patterns = {
        # Mariage
        r'\b(vais-je|vais je|est-ce que je vais|je vais)\s+(me\s+)?marier\b': 
            "Que disent les cartes sur mes perspectives de relation stable et d'engagement ?",
        
        # Amour/Rencontre
        r'\b(vais-je|vais je|est-ce que je vais|je vais)\s+((re)?trouver|rencontrer|avoir)\s+(l\'|l)?amour\b':
            "Quelle est l'énergie autour de ma vie sentimentale ?",
        
        # Enfants
        r'\b(vais-je|vais je|est-ce que je vais|je vais|aurai-je|aurai je)\s+(avoir|des)\s+enfants?\b':
            "Que montrent les symboles sur la thématique de la famille et de la création ?",
        
        # Argent/Richesse
        r'\b(vais-je|vais je|est-ce que je vais|je vais)\s+(gagner|avoir|être)\s+(de l\'|beaucoup d\')?argent\b':
            "Quelle est l'orientation concernant mes ressources et mon abondance ?",
        
        # Succès/Réussite
        r'\b(vais-je|vais je|est-ce que je vais|je vais)\s+réussir\b':
            "Quelles sont les tendances pour mon projet actuel ?",
    }
    
    import re
    for pattern, reformulation in sensitive_patterns.items():
        if re.search(pattern, q_lower):
            return reformulation
    
    return question

def consulter_madame_t(message: str, contexte: str = "") -> str:
    """Fonction principale de consultation"""
    # Vérification de la clé API
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "❌ **Erreur de configuration**\n\nLa clé API Gemini n'est pas configurée. Veuillez ajouter GEMINI_API_KEY dans les secrets du Space."
    
    # Validation de l'entrée
    if not message or not message.strip():
        return "⚠️ Veuillez poser une question pour que je puisse vous guider."
    
    try:
        # Configuration de Gemini
        genai.configure(api_key=api_key)
        model_name = pick_first_available(DEFAULT_MODELS)
        if not model_name:
            return "❌ **Configuration invalide**\n\nAucun modèle Gemini par défaut n'est défini. Ajoute GEMINI_MODEL ou vérifie la configuration."

        try:
            model = genai.GenerativeModel(
                model_name,
                generation_config={
                    "temperature": 0.85,  # Réduit pour moins de blocages (était 1.0)
                    "top_p": 0.90,        # Réduit pour plus de cohérence (était 0.95)
                    "top_k": 40,
                    "max_output_tokens": 300,
                },
                safety_settings={
                    "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                    "HARM_CATEGORY_HATE_SPEECH": "BLOCK_ONLY_HIGH",
                    "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
                    "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_ONLY_HIGH",
                }
            )
        except Exception as model_exc:
            # Tentative avec les autres candidats si le premier échoue
            fallback_name = None
            for candidate in DEFAULT_MODELS:
                candidate = (candidate or "").strip()
                if not candidate or candidate == model_name:
                    continue
                try:
                    model = genai.GenerativeModel(
                        candidate,
                        generation_config={
                            "temperature": 0.85,
                            "top_p": 0.90,
                            "top_k": 40,
                            "max_output_tokens": 300,
                        },
                        safety_settings={
                            "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_ONLY_HIGH",
                            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
                            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_ONLY_HIGH",
                        }
                    )
                    fallback_name = candidate
                    break
                except Exception:
                    continue
            else:
                raise model_exc

            if fallback_name:
                model_name = fallback_name
        
        # Détection de la langue
        user_lang = detect_language(message)
        lang_clause = language_directive(user_lang)
        
        # REFORMULATION: Transformer les questions sensibles pour éviter les blocages
        safe_message = reformulate_sensitive_question(message.strip())
        
        # Construction du message complet
        full_message = safe_message
        if contexte and contexte.strip():
            full_message = f"{full_message}\n\nContexte: {contexte.strip()}"
        
        # Si le contexte contient un résumé de tirage, ajouter une directive
        tirage_directive = ""
        if "Tirage (" in full_message:
            tirage_directive = (
                "Consigne: Prends la 'Carte principale' comme point focal et mentionne brièvement "
                "comment les autres cartes influencent ou modulent cette lecture. Sois concis et "
                "donne une action pratique en une phrase.\n\n"
            )

        # Prompt final
        final_prompt = (
            f"{SYSTEM_PROMPT} {lang_clause}\n\n"
            f"{tirage_directive}"
            f"Utilisateur ({user_lang}): {full_message}\n"
            f"Mme T:"
        )
        
        # Génération de la réponse
        result = model.generate_content(final_prompt)
        
        # Vérifier si une réponse a été générée
        if result and result.candidates:
            candidate = result.candidates[0]
            
            # Vérifier finish_reason
            # 0 = UNSPECIFIED, 1 = STOP (succès), 2 = SAFETY (bloqué), 3 = MAX_TOKENS, etc.
            finish_reason = candidate.finish_reason
            
            if finish_reason == 2:  # SAFETY - Contenu bloqué
                return (
                    "Ah ma belle, le tarot me montre quelque chose mais les énergies "
                    "sont un peu troubles aujourd'hui. Reformule ta question différemment "
                    "et je pourrai mieux te guider ! ✨"
                )
            
            # Essayer d'accéder au texte
            try:
                if result.text:
                    return result.text
            except ValueError:
                # Si result.text lève une exception, extraire manuellement
                if candidate.content and candidate.content.parts:
                    return candidate.content.parts[0].text
        
        return "❌ Aucune réponse n'a été générée. Veuillez réessayer."
        
    except Exception as e:
        error_msg = str(e)
        if "API_KEY" in error_msg.upper():
            return f"❌ **Erreur d'authentification**\n\nLa clé API Gemini est invalide ou expirée.\n\nDétails: {error_msg}"
        elif "quota" in error_msg.lower():
            return f"❌ **Quota dépassé**\n\nLe quota de l'API Gemini a été dépassé.\n\nDétails: {error_msg}"
        elif "model" in error_msg.lower() and "not" in error_msg.lower():
            return (
                "❌ **Modèle indisponible**\n\n"
                "Le modèle Gemini demandé n'est pas accessible sur ce compte. "
                "Définis la variable GEMINI_MODEL (ex: gemini-1.5-flash-latest) dans les Secrets du Space.\n\n"
                f"Détails: {error_msg}"
            )
        else:
            return f"❌ **Erreur inattendue**\n\n{error_msg}\n\nVeuillez réessayer dans quelques instants."

# Interface Gradio
with gr.Blocks(
    title="🔮 Madame T – Voyante du Tarot",
    theme=gr.themes.Soft(
        primary_hue="purple",
        secondary_hue="pink",
    )
) as demo:
    
    gr.Markdown(
        """
        # 🔮 Madame T – Voyante du Tarot de Marseille
        
        Bienvenue dans mon cabinet de voyance virtuel. Posez-moi votre question 
        et je vous guiderai à travers les messages du tarot.
        """
    )
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 💬 Votre consultation")
            
            question = gr.Textbox(
                label="Votre question",
                placeholder="Ex : Trouverai-je l'amour cette année ? Devrais-je changer de carrière ?",
                lines=4,
                max_lines=8
            )
            
            contexte = gr.Textbox(
                label="Contexte ou cartes tirées (optionnel)",
                placeholder="Ex : Le Soleil, La Lune, L'Étoile en position passé-présent-futur",
                lines=2,
                max_lines=4
            )
            
            with gr.Row():
                effacer_btn = gr.Button("🗑️ Effacer", variant="secondary", scale=1)
                consulter_btn = gr.Button("✨ Consulter Madame T ✨", variant="primary", scale=2)
        
        with gr.Column(scale=1):
            gr.Markdown("### 🌟 Guidance de Madame T")
            
            reponse = gr.Textbox(
                label="Réponse",
                lines=15,
                max_lines=20,
                interactive=False,
                show_copy_button=True
            )
    
    gr.Markdown(
        """
        ---
        
        💡 **Conseils d'utilisation :**
        - Posez une question claire et précise
        - Si vous avez tiré des cartes, indiquez-les dans le contexte
        - Une consultation = un dilemme
        
        *Propulsé par Gemini 2.0 Flash (Expérimental)*
        """
    )
    
    # Événements
    consulter_btn.click(
        fn=consulter_madame_t,
        inputs=[question, contexte],
        outputs=reponse,
        api_name="predict"  # Exposer via /api/predict
    )
    
    effacer_btn.click(
        fn=lambda: ("", "", ""),
        inputs=[],
        outputs=[question, contexte, reponse]
    )
    
    # Exemple au chargement
    demo.load(
        fn=lambda: "🔮 Prête à vous guider...",
        inputs=[],
        outputs=reponse
    )

# Pour Hugging Face Spaces
if __name__ == "__main__":
    demo.launch()