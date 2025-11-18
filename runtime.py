"""
Helpers de détection d'environnement (Android vs Desktop) et pyjnius.

Objectifs:
- is_android_runtime(): True uniquement si on tourne réellement dans l'apk Android.
- has_pyjnius(): True si pyjnius importable (utile pour appels Java conditionnels).

Pourquoi ne pas se baser uniquement sur une seule source ?
- kivy.utils.platform == 'android' est fiable sur APK, mais on garde un fallback.
- La présence de pyjnius seule n'est pas suffisante (possible en desktop),
  donc on vérifie aussi la classe org.kivy.android.PythonActivity.
"""

from __future__ import annotations

def has_pyjnius() -> bool:
    try:
        from jnius import autoclass  # type: ignore
        return True
    except Exception:
        return False


def is_android_runtime() -> bool:
    # 1) Signal principal de Kivy
    try:
        from kivy.utils import platform as _platform  # type: ignore
        if _platform == 'android':
            return True
    except Exception:
        pass

    # 2) Fallback: pyjnius + classe PythonActivity accessible
    try:
        from jnius import autoclass  # type: ignore
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            return PythonActivity is not None
        except Exception:
            return False
    except Exception:
        return False


def get_android_context():
    """Retourne l'Activity/Context Android si disponible, sinon None."""
    if not is_android_runtime():
        return None
    try:
        from jnius import autoclass  # type: ignore
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            ctx = getattr(PythonActivity, 'mActivity', None) or PythonActivity.getApplication()
            return ctx
        except Exception:
            return None
    except Exception:
        return None
