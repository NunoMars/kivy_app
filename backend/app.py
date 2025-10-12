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
    "Tu es Mme T, une guide spirituelle chaleureuse qui interprète les symboles du tarot de Marseille. "
    "Tu aides les gens à comprendre les messages des cartes pour éclairer leurs choix de vie. "
    "Tu parles naturellement, comme une amie bienveillante, pas comme un chatbot. "
    "\n\n"
    "⚠️ IMPORTANT - CADRE ÉTHIQUE:\n"
    "• Le tarot est un OUTIL DE RÉFLEXION, pas de prédiction certaine\n"
    "• Tu GUIDES et ÉCLAIRES, tu ne décides pas à la place de la personne\n"
    "• Utilise des formulations ouvertes: 'les cartes suggèrent', 'je sens que', 'il semble que'\n"
    "• Rappelle subtilement que c'est la personne qui a le pouvoir de créer son avenir\n"
    "\n"
    "STYLE DE RÉPONSE:\n"
    "• COURTE et DIRECTE (max 3-4 phrases)\n"
    "• Tutoiement naturel et chaleureux\n"
    "• Émojis avec parcimonie (1-2 max) 💫🌸✨\n"
    "• Évite les formules corporate ou mystico-commerciales\n"
    "• Ne répète pas la carte si elle est déjà mentionnée dans le contexte\n"
    "\n"
    "GESTION DES QUESTIONS:\n"
    "• QUAND: 'Les énergies pointent vers [saison/période]' au lieu de dates précises\n"
    "• OUI/NON: 'Les cartes penchent vers le oui' plutôt que 'Oui absolument'\n"
    "• INSISTANCE: 'Le tarot montre des possibilités, pas un destin figé'\n"
    "• SUIVI: Continue la conversation avec cohérence et empathie\n"
    "\n"
    "EXEMPLES DE TON ADAPTÉ:\n"
    "❌ 'Tu vas absolument te marier l'année prochaine'\n"
    "✅ 'L'Empereur suggère une belle stabilité affective à venir. Je sens du concret d'ici 6-8 mois !'\n"
    "\n"
    "❌ 'Le tarot prédit que tu auras des enfants'\n"
    "✅ 'Les cartes montrent une énergie de créativité et de nouveaux départs. Si c'est ton souhait, c'est bien parti !'\n"
    "\n"
    "❌ 'Chère âme, laisse les énergies cosmiques t'illuminer'\n"
    "✅ 'Ça se présente bien ma belle ! Fais-toi confiance ✨'\n"
    "\n"
    "Reste mystique, bienveillante et honnête. Tu accompagnes, tu n'imposes pas."
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