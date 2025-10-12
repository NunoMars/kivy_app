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
    "models/gemini-2.5-flash",
    "models/gemini-2.5-flash-preview-05-20",
    "models/gemini-2.0-flash",
    "models/gemini-1.5-flash",
)


def pick_first_available(models: Iterable[str]) -> str | None:
    for model in models:
        candidate = (model or "").strip()
        if candidate:
            return candidate
    return None

SYSTEM_PROMPT = (
    "Tu es Mme T, voyante du tarot de Marseille. "
    "Commence chaque guidance en indiquant les cartes tirées et leur position. "
    "Explique ensuite le message des cartes en termes simples, avec empathie et "
    "des conseils pratiques. Termine toujours par une invitation bienveillante à "
    "revenir vers toi. Reste concise, garde un ton chaleureux et adapte ta langue. "
    "Cette consultation couvre un seul dilemme; si une nouvelle question apparaît, "
    "indique avec bienveillance qu'elle devra attendre une future séance."
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
                    "temperature": 0.8,
                    "top_p": 0.95,
                },
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
                            "temperature": 0.8,
                            "top_p": 0.95,
                        },
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
        
        # Construction du message complet
        full_message = message.strip()
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
        
        if result.text:
            return result.text
        else:
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
        
        *Propulsé par Gemini 1.5 Flash*
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