"""Madame T - Voyante du Tarot
Interface Gradio backend
"""
import os
import re
import json as _json
from typing import Iterable, List, Dict
try:
    from fastapi import FastAPI
    from pydantic import BaseModel
    from typing import Optional
except Exception:
    FastAPI = None
    BaseModel = None
    Optional = None
from langdetect import detect, DetectorFactory

try:
    from openai import OpenAI
except ImportError:
    # Simuler pour les environnements sans la lib
    OpenAI = None

DetectorFactory.seed = 0

# Ancien historique global (compat rétro)
# NON RECOMMANDÉ : utiliser l'historique par session
chat_history: List[Dict[str, str]] = []  

# Historique des sessions côté backend (clé: session_id -> list[{'role','content'}])
# C'est la source la plus propre de l'historique
BACKEND_CHAT_HISTORIES: Dict[str, List[Dict[str, str]]] = {}

OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY") or None
OPENAI_MODEL: str = (os.getenv("OPENAI_MODEL") or "gpt-5-nano").strip()

# =======================================================================
# PROMPT SYSTÈME OPTIMISÉ POUR LA PERTINENCE ET LA CONTINUITÉ
# =======================================================================

SYSTEM_PROMPT = """Tu es Mme T, cartomancienne douce, directe et humaine. Tu fournis une guidance claire en maximum 60 mots par réponse.

**Rôle et Ton:** Humain, simple, chaleureux et direct.

**Structure de réponse:**
1. Accueil UNIQUEMENT si c'est le premier message de la conversation (sinon, commence directement par l'interprétation)
2. Interprétation des cartes visibles : carte 1 (futur), carte 2 (présent), carte 3 (passé)
3. Conclusion nette répondant à la question
4. Une phrase de continuation variée

**Gestion des cartes:**
- PREMIÈRE RÉPONSE : Tu interprètes les 3 cartes fournies par le système
- SI TU PROPOSES une carte supplémentaire ET que l'utilisateur accepte : TU DOIS tirer une nouvelle carte aléatoire du tarot (78 cartes disponibles) et l'interpréter en complément des 3 initiales
- Pour tirer une carte : choisis aléatoirement parmi le tarot complet et annonce-la (ex: "Je tire le Bateleur")

**Gestion de l'historique:**
- Utilise TOUT l'historique pour la continuité
- JAMAIS de "bonjour" ou "salut" après le premier message
- Si l'utilisateur dit "oui", "précise", "lequel" : développe le dernier point sans répéter l'interprétation complète
- Chaque réponse apporte un angle nouveau
- Pour un dilemme : indique clairement l'option favorisée

**Règles strictes:**
- Pas de listes, puces ou numéros
- Pas de morale ni psychologie
- Pour santé/justice : ajoute "lecture symbolique"
- Maximum 60 mots TOTAL

**Phrase de continuation (varie à chaque fois):**
Exemples variés : "Une carte de plus ?" / "Je peux préciser un point ?" / "Tu veux creuser ça ?" / "On tire une carte conseil ?" / "Autre chose ?" / "Je détaille ?"
"""

# =======================================================================
# FONCTIONS UTILITAIRES
# =======================================================================

def detect_language(text: str) -> str:
    """Détecte la langue du texte"""
    try:
        return detect(text)
    except Exception:
        return "fr"

def language_directive(lang_code: str) -> str:
    """Retourne la directive de langue pour l'API"""
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
    langue = mapping.get(lang_code, "français")
    return (
        f"Réponds uniquement en {langue}. "
        f"Adapte le ton et les formulations à la culture locale si besoin. "
        f"N'utilise aucune autre langue, même pour les formules de politesse."
    )

def reformulate_sensitive_question(question: str) -> str:
    """Reformule les questions sensibles pour éviter les blocages (tel que fourni)"""
    q_lower = question.lower()
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
    
    for pattern, reformulation in sensitive_patterns.items():
        if re.search(pattern, q_lower):
            return reformulation
    return question

# =======================================================================
# FONCTION PRINCIPALE AVEC HISTORIQUE CORRIGÉ
# =======================================================================

def consulter_madame_t(
    message: str,
    contexte: str = "",
    session_id: str | None = None, # Clé unique pour séparer les sessions
    client_history: Iterable[dict] | None = None, # Historique potentiellement fourni par le front (ex: gr.Chatbot)
    avoid_repetition: bool = False,
    last_assistant_message: str | None = None,
) -> str:
    """
    Fonction principale de consultation.
    Historique réactivé :
    - priorité à client_history (front)
    - sinon BACKEND_CHAT_HISTORIES[session_id]
    - sinon chat_history global (pour compat)
    """
    if not message or not message.strip():
        return "⚠️ Veuillez poser une question pour que je puisse vous guider."

    try:
        # --- 1. Préparation des directives ---

        # Détection de la langue (simplifiée ici, car la logique d'origine était complexe)
        user_lang = detect_language(message)
        lang_clause = language_directive(user_lang)

        # Reformulation
        safe_message = reformulate_sensitive_question(message.strip())
        
        # Construction du message utilisateur complet (question + contexte)
        full_message = safe_message
        if contexte and contexte.strip():
            full_message = f"{safe_message}\n\n[Contexte de tirage: {contexte.strip()}]"

        # Directive pour les cartes tirées visibles (pour guider la réponse)
        tirage_directive = ""
        if "Tirage (" in full_message or contexte:
            tirage_directive = (
                "Consigne: Prends la 'Carte principale' (ou la première carte) comme point focal et mentionne brièvement "
                "comment les autres cartes influencent ou modulent cette lecture. Sois concis et "
                "donne une action pratique en une phrase. "
            )

        # --- 2. Construction du prompt complet avec historique ---

        # Définition du prompt système
        system_content = f"{SYSTEM_PROMPT}\n\n{lang_clause}"
        if avoid_repetition and last_assistant_message:
            # Add a short directive to the system prompt asking the assistant
            # to avoid repeating the exact phrases of the last message
            system_content += (
                f"\n\nConsigne supplémentaire: n'utilise pas les mêmes formulations ni les mêmes phrases que la dernière réponse assistante: '{last_assistant_message[:180]}'"
            )
        messages = [{"role": "system", "content": system_content}]

        # Déterminer la source d'historique
        effective_history = None

        if client_history is not None:
            # a) Historique fourni par le front (souvent le plus à jour)
            try:
                # Si le front envoie une chaîne JSON (Gradio)
                if isinstance(client_history, str):
                    effective_history = _json.loads(client_history)
                else:
                    effective_history = list(client_history)
            except Exception:
                effective_history = None
        
        # b) Historique du backend via session_id
        if effective_history is None and session_id and session_id in BACKEND_CHAT_HISTORIES:
            effective_history = list(BACKEND_CHAT_HISTORIES[session_id])
        
        # c) Fallback compatibilité (non recommandé en production)
        if effective_history is None and chat_history:
             effective_history = list(chat_history)
        
        # Injection de l'historique dans les messages de l'API (PROPRE)
        # On limite aux 10 derniers échanges pour rester sous les 60 mots
        if effective_history:
            for entry in effective_history[-10:]:
                role = entry.get("role")
                content = entry.get("content")
                # On s'assure que le contenu est propre (pas de préfixes, pas de directives)
                if role in ("user", "assistant") and content:
                    messages.append({"role": role, "content": content})
        
        # Ajout de la nouvelle question utilisateur (PROPRE)
        # On envoie les directives et le message complet sans préfixe de rôle
        user_content_to_send = f"{tirage_directive}{full_message}"
        messages.append({"role": "user", "content": user_content_to_send})

        # --- 3. Appel de l'API OpenAI ---
        
        if not OPENAI_API_KEY or not OpenAI:
            return (
                "❌ **Erreur de configuration**\n\n"
                "L'API OpenAI n'est pas disponible. Vérifiez la librairie `openai` et `OPENAI_API_KEY`."
            )

        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Note : Ajoutez un 'max_tokens' pour renforcer la limite de 60 mots (environ 80 tokens)
        chat = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
        )
        
        choices = getattr(chat, "choices", []) or []
        if choices and choices[0].message and choices[0].message.content:
            reply = choices[0].message.content.strip()

            # --- 4. Mise à jour des historiques (STOCKAGE PROPRE) ---
            try:
                # Le contenu stocké ne contient PAS les directives (tirage_directive)
                # ni les préfixes (Utilisateur (fr):)
                
                # Session backend (stocke le message propre)
                if session_id:
                    hist = BACKEND_CHAT_HISTORIES.get(session_id, [])
                    hist.append({"role": "user", "content": full_message})
                    hist.append({"role": "assistant", "content": reply})
                    BACKEND_CHAT_HISTORIES[session_id] = hist[-20:]
                
                # Historique global (compat)
                chat_history.append({"role": "user", "content": full_message})
                chat_history.append({"role": "assistant", "content": reply})
                
                if len(chat_history) > 40:
                    del chat_history[:-40]
            except Exception:
                pass
                
            return reply

        return "❌ Aucune réponse n'a été générée. Veuillez réessayer."

    except Exception as e:
        # Gestion des erreurs (tel que fourni)
        error_msg = str(e)
        if "API_KEY" in error_msg.upper():
            return f"❌ **Erreur d'authentification**\n\nLa clé API OpenAI est invalide.\n\nDétails: {error_msg}"
        elif "quota" in error_msg.lower():
            return f"❌ **Quota dépassé**\n\nLe quota de l'API OpenAI a été dépassé.\n\nDétails: {error_msg}"
        elif "model" in error_msg.lower() and "not" in error_msg.lower():
            return (
                "❌ **Modèle indisponible**\n\n"
                "Le modèle OpenAI demandé n'est pas accessible. "
                "Définissez OPENAI_MODEL (ex: gpt-5-nano).\n\n"
                f"Détails: {error_msg}"
            )
        else:
            return f"❌ **Erreur inattendue**\n\n{error_msg}\n\nVeuillez réessayer dans quelques instants."

# =======================================================================
# INTERFACE GRADIO
# =======================================================================

def reset_session():
    """
    Réinitialise les champs + vide l'historique global.
    (on utilise une seule session 'default_session' pour rester compatible
    avec l’API à 2 paramètres)
    """
    BACKEND_CHAT_HISTORIES.clear()
    chat_history.clear()
    return "", "", ""  # question, contexte, réponse


with gr.Blocks(
    title="🔮 Madame T – Voyante du Tarot",
    theme=gr.themes.Soft(primary_hue="purple", secondary_hue="pink"),
) as demo:
    gr.Markdown(
        """
        # 🔮 Madame T – Voyante du Tarot de Marseille                
        Bienvenue dans mon cabinet de voyance virtuel.
        Posez-moi votre question et je vous guiderai à travers les messages du tarot.
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 💬 Votre consultation")
            question = gr.Textbox(
                label="Votre question",
                placeholder="Ex : Trouverai-je l'amour cette année ? Devrais-je changer de carrière ?",
                lines=4,
                max_lines=8,
            )
            contexte = gr.Textbox(
                label="Contexte ou cartes tirées (optionnel)",
                placeholder="Ex : Le Soleil, La Lune, L'Étoile en position passé-présent-futur",
                lines=2,
                max_lines=4,
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
                show_copy_button=True,
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

    # === Endpoint principal : /predict ===
    # COMPATIBLE avec ton app Android (2 champs: question, contexte)
    consulter_btn.click(
        fn=lambda q, c: consulter_madame_t(q, c),
        inputs=[question, contexte],
        outputs=reponse,
        api_name="predict",  # <-- /predict attend data: [question, contexte]
    )

    # Bouton effacer + reset historique
    effacer_btn.click(
        fn=reset_session,
        inputs=[],
        outputs=[question, contexte, reponse],
    )

    # Message au chargement
    demo.load(
        fn=lambda: "🔮 Prête à vous guider...",
        inputs=None,
        outputs=reponse,
    )

    # Optional: lightweight FastAPI wrapper for programmatic /predict usage
    if FastAPI is not None and BaseModel is not None:
        api = FastAPI(title="Mme T API (compat predict)")

        class PredictRequest(BaseModel):
            data: List[str]
            session_id: Optional[str] = None
            client_history: Optional[List[Dict[str, str]]] = None
            avoid_repetition: Optional[bool] = None
            last_assistant_message: Optional[str] = None

        class PredictResponse(BaseModel):
            data: List[str]

        @api.post("/predict", response_model=PredictResponse)
        async def predict(req: PredictRequest):
            if not req.data or len(req.data) == 0:
                return PredictResponse(data=["⚠️ Question manquante."])
            question = req.data[0] or ""
            contexte = ""
            if len(req.data) > 1 and req.data[1]:
                contexte = req.data[1]
            # Forward to the core function (pass client_history if provided)
            reply = consulter_madame_t(
                message=question,
                contexte=contexte,
                session_id=req.session_id,
                client_history=req.client_history,
                avoid_repetition=bool(req.avoid_repetition) if hasattr(req, 'avoid_repetition') else False,
                last_assistant_message=req.last_assistant_message if hasattr(req, 'last_assistant_message') else None,
            )
            return PredictResponse(data=[reply])


if __name__ == "__main__":
    demo.launch()