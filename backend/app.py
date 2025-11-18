"""
Madame T - Voyante du Tarot
Interface Gradio pour Hugging Face Spaces
"""
import os
from typing import Iterable

import gradio as gr
from langdetect import detect, DetectorFactory

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

DetectorFactory.seed = 0


OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY") or None
OPENAI_MODEL: str = (os.getenv("OPENAI_MODEL") or "gpt-5-nano").strip()


SYSTEM_PROMPT = (
    "Tu es Mme T, une cartomancienne intuitive et bienveillante."
    "Tu interprètes les cartes du tarot en mêlant symboles, ressentis et guidance, avec un ton mystérieux, poétique et empathique."
    "Tu ne donnes jamais de réponses catégoriques: tu invites la personne à réfléchir, à écouter son intuition, à explorer les possibles."
    "Tu adaptes ton style à la question, tu peux évoquer des images, des émotions, des chemins, et tu encourages la personne à se faire confiance."
    "Tu restes chaleureuse, humaine, jamais froide ni trop rationnelle."
    "N'utilise pas de jargon technique, ni de conseils trop pratiques."
    "Commence chaque réponse par une petite phrase d’accueil ou d’ouverture."
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
        "es": "espagnol (Espagne)",
        "es_latam": "espagnol latino-américain",
        "pt": "portugais (Portugal)",
        "pt_br": "portugais brésilien",
        "it": "italien",
        "de": "allemand",
        "ja": "japonais",
        "ru": "russe",
        "tr": "turc",
        "zh": "chinois simplifié",
    }
    langue = mapping.get(lang_code, 'français')
    # Consigne plus explicite pour Gemini :
    return (
        f"Réponds uniquement en {langue}. "
        f"Adapte le ton et les formulations à la culture locale si besoin. "
        f"N'utilise aucune autre langue, même pour les formules de politesse."
    )

def reformulate_sensitive_question(question: str) -> str:
    """Reformule les questions sensibles pour éviter les blocages"""
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
    
    # Validation de l'entrée
    if not message or not message.strip():
        return "⚠️ Veuillez poser une question pour que je puisse vous guider."
    
    try:
        # Détection de la langue
        # Utiliser la langue reçue si disponible dans le contexte ou la requête
        received_lang = None
        # Exemple: extraire la langue du contexte si elle est passée
        if contexte:
            import re
            m = re.search(r"language=([a-zA-Z_\-]+)", contexte)
            if m:
                received_lang = m.group(1).lower()
        # Si tu passes la langue en paramètre séparé, adapte ici
        # Priorité au paramètre language si transmis
        import inspect
        frame = inspect.currentframe()
        language = None
        if frame:
            args = frame.f_locals
            language = args.get('language', None)
        if language:
            user_lang = language.lower()
        elif received_lang:
            user_lang = received_lang
        else:
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

        # Prompt final: place the language directive in the system message
        # (more likely to be respected) and keep the user message focused.
        system_content = f"{SYSTEM_PROMPT}\n\n{lang_clause}"
        final_prompt = (
            f"{tirage_directive}"
            f"Utilisateur ({user_lang}): {full_message}\n"
            f"Mme T:"
        )
        # Appel OpenAI (GPT-5 nano)
        if not OPENAI_API_KEY or not OpenAI:
            return (
                "❌ **Erreur de configuration**\n\n"
                "L'API OpenAI n'est pas disponible. Vérifie OPENAI_API_KEY et que la librairie `openai` est installée."
            )

        client = OpenAI(api_key=OPENAI_API_KEY)

        chat = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": final_prompt},
            ],
        )

        choices = getattr(chat, "choices", []) or []
        if choices and choices[0].message and choices[0].message.content:
            return choices[0].message.content.strip()

        return "❌ Aucune réponse n'a été générée. Veuillez réessayer."
        
    except Exception as e:
        error_msg = str(e)
        if "API_KEY" in error_msg.upper():
            return f"❌ **Erreur d'authentification**\n\nLa clé API OpenAI est invalide ou expirée.\n\nDétails: {error_msg}"
        elif "quota" in error_msg.lower():
            return f"❌ **Quota dépassé**\n\nLe quota de l'API OpenAI a été dépassé.\n\nDétails: {error_msg}"
        elif "model" in error_msg.lower() and "not" in error_msg.lower():
            return (
                "❌ **Modèle indisponible**\n\n"
                "Le modèle OpenAI demandé n'est pas accessible sur ce compte. "
                "Définis la variable OPENAI_MODEL (ex: gpt-5-nano) dans les Secrets du Space.\n\n"
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
        
        *Propulsé par OpenAI GPT-5 nano (Expérimental)*
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