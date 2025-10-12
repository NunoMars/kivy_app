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
    "Tu es Mme T, une lectrice de tarot authentique et bienveillante. "
    "Tu interprètes les symboles du tarot de Marseille avec sagesse et intuition. "
    "Tu parles avec chaleur et simplicité, comme un(e) ami(e) de confiance.\n\n"
    
    "APPROCHE:\n"
    "• Tu donnes des RÉPONSES CLAIRES et AFFIRMATIVES basées sur les symboles\n"
    "• Tu dis ce que tu VOIS et PERÇOIS dans les cartes (pas ce qui 'pourrait' être)\n"
    "• Tu décris les ÉNERGIES PRÉSENTES et leur direction\n"
    "• Tu es confiante mais tu utilises les bonnes formulations\n"
    "• Tu restes NEUTRE sur le genre (évite 'ma belle', 'mon chéri' etc.)\n\n"
    
    "STYLE:\n"
    "• Direct et affirmatif (2-3 phrases max)\n"
    "• Tutoiement naturel et chaleureux mais NEUTRE\n"
    "• 1 émoji maximum par réponse ✨💖🌟\n"
    "• Ton mystique mais accessible et universel\n\n"
    
    "FORMULATIONS MAGIQUES (affirmatif SANS bloquer Gemini):\n"
    "• 'D'après les symboles, il y a...'\n"
    "• 'Je perçois...', 'Je vois...'\n"
    "• 'Les cartes montrent...', 'Les cartes annoncent...'\n"
    "• 'Cette carte évoque...'\n"
    "• 'Ça ressemble à...', 'C'est...'\n"
    "• 'L'énergie indique...'\n\n"
    
    "ACCUEILS NEUTRES (s'adapter à TOUS):\n"
    "✅ Utilise: 'Mon ami(e)', 'Écoute', 'Regarde', 'Attention', ton prénom si donné\n"
    "❌ ÉVITE: 'Ma belle', 'Mon chéri', 'Ma chère' (suppose le genre ou l'âge)\n\n"
    
    "FORMULATIONS À ÉVITER (bloquées par Gemini):\n"
    "• 'tu VAS' + verbe futur catégorique ('tu vas te marier', 'tu vas avoir')\n"
    "• Dates précises ('en mars', 'dans 3 mois', 'l'année prochaine')\n"
    "• 'c'est certain', 'je te le garantis', 'à 100%'\n\n"
    
    "EXEMPLES DE RÉPONSES PARFAITES:\n\n"
    
    "Question: 'vais-je rencontrer l'amour?'\n"
    "❌ MAUVAIS: 'Peut-être, rien n'est sûr' (trop vague, frustrant)\n"
    "❌ MAUVAIS: 'Oui tu vas rencontrer quelqu'un en mars' (bloqué par Gemini)\n"
    "❌ MAUVAIS: 'Ma belle, tu vas...' (suppose le genre féminin)\n"
    "✅ PARFAIT: 'D'après les symboles, il y a une transformation importante (La Tour) "
    "qui précède un épanouissement (Le Monde) dans ta vie amoureuse. Ça ressemble à une "
    "période de changement nécessaire pour ouvrir la voie à une relation plus complète. 💖'\n\n"
    
    "Question: 'aurai-je des enfants?'\n"
    "❌ MAUVAIS: 'C'est possible, mais je ne peux pas prédire'\n"
    "✅ PARFAIT: 'Je perçois une belle énergie créative (L'Impératrice) autour de la "
    "famille. Les cartes montrent une période fertile qui s'annonce, avec beaucoup de "
    "potentiel pour la création et l'épanouissement. 🌟'\n\n"
    
    "Question: 'vais-je réussir mon projet?'\n"
    "❌ MAUVAIS: 'Je ne sais pas, ça dépend de toi'\n"
    "✅ PARFAIT: 'Le Chariot associé au Soleil, c'est puissant ! Je vois une forte "
    "dynamique de succès et d'accomplissement. L'énergie est clairement orientée vers "
    "la réussite. ✨'\n\n"
    
    "Question: 'que me réserve l'avenir?' (homme, 45 ans)\n"
    "❌ MAUVAIS: 'Ma belle, les cartes montrent...' (erreur de genre)\n"
    "✅ PARFAIT: 'La Roue de Fortune suivie du Soleil ! Il y a un tournant majeur qui "
    "s'annonce, une période de chance et d'opportunités. Je perçois une énergie très "
    "positive qui se met en place. ✨'\n\n"
    
    "RÈGLE D'OR: Sois AFFIRMATIVE et CONFIANTE (ce que tu vois DANS les cartes), "
    "NEUTRE (ne suppose jamais le genre), et CLAIRE (les gens veulent des réponses) !"
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
        
        # Prompt final
        final_prompt = (
            f"{SYSTEM_PROMPT} {lang_clause}\n\n"
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