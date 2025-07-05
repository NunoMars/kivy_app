#!/usr/bin/env python3
"""
Script de diagnostic pour identifier les problèmes de build Android.
Analyser les logs et proposer des solutions automatiques.
"""

import re
import sys
from typing import List, Dict, Tuple

class AndroidBuildDiagnostic:
    def __init__(self):
        self.common_errors = {
            "ALooper_pollAll": {
                "pattern": r"ALooper_pollAll.*unavailable.*obsoleted",
                "description": "ALooper_pollAll obsolète dans NDK récent",
                "solutions": [
                    "Utiliser NDK 25 au lieu de NDK 27",
                    "Utiliser buildozer au lieu de p4a direct",
                    "Configurer android.ndk = 25b dans buildozer.spec"
                ],
                "severity": "CRITICAL"
            },
            "strict_prototypes": {
                "pattern": r"function declaration without a prototype.*deprecated",
                "description": "Warnings de prototypes manquants dans SDL2",
                "solutions": [
                    "Warnings non-bloquants, ignorables",
                    "Utiliser une version plus récente de SDL2",
                    "Ajouter des flags de compilation pour ignorer"
                ],
                "severity": "WARNING"
            },
            "ndk_version": {
                "pattern": r"ndk.*27\..*toolchains",
                "description": "NDK 27 incompatible avec SDL2 actuel",
                "solutions": [
                    "Forcer NDK 25.2.9519653",
                    "Utiliser buildozer qui gère automatiquement les versions",
                    "Modifier android.ndk dans buildozer.spec"
                ],
                "severity": "CRITICAL"
            },
            "java_version": {
                "pattern": r"java.*version.*21",
                "description": "Java 21 peut causer des incompatibilités",
                "solutions": [
                    "Utiliser Java 17 (LTS recommandé)",
                    "Configurer JAVA_HOME explicitement",
                    "Vérifier la compatibilité avec buildozer"
                ],
                "severity": "MEDIUM"
            },
            "api_target": {
                "pattern": r"android.*api.*34",
                "description": "API 34 peut avoir des incompatibilités",
                "solutions": [
                    "Utiliser API 33 (plus stable)",
                    "Configurer android.api = 33",
                    "Vérifier NDK target compatibility"
                ],
                "severity": "MEDIUM"
            }
        }
    
    def analyze_log(self, log_content: str) -> Dict[str, List]:
        """Analyser le contenu du log pour identifier les erreurs."""
        results = {
            "critical_errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        lines = log_content.split('\n')
        
        for i, line in enumerate(lines):
            for error_name, error_info in self.common_errors.items():
                if re.search(error_info["pattern"], line, re.IGNORECASE):
                    context = self._get_context(lines, i)
                    
                    error_data = {
                        "name": error_name,
                        "line": i + 1,
                        "content": line.strip(),
                        "description": error_info["description"],
                        "solutions": error_info["solutions"],
                        "context": context
                    }
                    
                    if error_info["severity"] == "CRITICAL":
                        results["critical_errors"].append(error_data)
                    elif error_info["severity"] == "WARNING":
                        results["warnings"].append(error_data)
                    else:
                        results["suggestions"].append(error_data)
        
        return results
    
    def _get_context(self, lines: List[str], error_line: int, context_size: int = 3) -> List[str]:
        """Obtenir le contexte autour d'une ligne d'erreur."""
        start = max(0, error_line - context_size)
        end = min(len(lines), error_line + context_size + 1)
        return lines[start:end]
    
    def generate_buildozer_fix(self, errors: Dict) -> str:
        """Générer une configuration buildozer.spec corrigée."""
        fixes = []
        
        # Fixes basés sur les erreurs détectées
        if any("ndk" in err["name"] or "ALooper" in err["name"] for err in errors["critical_errors"]):
            fixes.append("android.ndk = 25b")
            fixes.append("android.ndk_api = 21")
        
        if any("api" in err["name"] for err in errors["critical_errors"] + errors["suggestions"]):
            fixes.append("android.api = 33")
        
        fixes.append("android.accept_sdk_license = True")
        fixes.append("android.skip_update = False")
        
        return "\n".join(f"# FIX: {fix}" for fix in fixes)
    
    def generate_workflow_fix(self, errors: Dict) -> str:
        """Générer des corrections pour le workflow GitHub Actions."""
        fixes = []
        
        if any("java" in err["name"] for err in errors["critical_errors"] + errors["suggestions"]):
            fixes.append("java-version: '17'  # Au lieu de '21'")
        
        if any("ndk" in err["name"] for err in errors["critical_errors"]):
            fixes.append('sdkmanager "ndk;25.2.9519653"  # Au lieu du NDK par défaut')
        
        fixes.append("# Utiliser buildozer au lieu de p4a direct")
        fixes.append("# buildozer android aab")
        
        return "\n".join(f"# FIX: {fix}" for fix in fixes)
    
    def print_report(self, results: Dict):
        """Afficher un rapport détaillé des erreurs et solutions."""
        print("🔍 RAPPORT D'ANALYSE DES ERREURS DE BUILD ANDROID")
        print("=" * 60)
        
        # Erreurs critiques
        if results["critical_errors"]:
            print(f"\n❌ ERREURS CRITIQUES ({len(results['critical_errors'])})")
            print("-" * 40)
            for error in results["critical_errors"]:
                print(f"\n🚨 {error['name'].upper()}")
                print(f"   Ligne {error['line']}: {error['description']}")
                print(f"   Erreur: {error['content']}")
                print("   Solutions:")
                for i, solution in enumerate(error['solutions'], 1):
                    print(f"     {i}. {solution}")
        
        # Warnings
        if results["warnings"]:
            print(f"\n⚠️ WARNINGS ({len(results['warnings'])})")
            print("-" * 40)
            for warning in results["warnings"]:
                print(f"\n🟡 {warning['name']}")
                print(f"   Ligne {warning['line']}: {warning['description']}")
                print(f"   Solutions (optionnelles):")
                for i, solution in enumerate(warning['solutions'], 1):
                    print(f"     {i}. {solution}")
        
        # Suggestions
        if results["suggestions"]:
            print(f"\n💡 SUGGESTIONS ({len(results['suggestions'])})")
            print("-" * 40)
            for suggestion in results["suggestions"]:
                print(f"\n🔧 {suggestion['name']}")
                print(f"   {suggestion['description']}")
        
        # Résumé et recommandations
        print("\n" + "=" * 60)
        print("📋 RÉSUMÉ ET RECOMMANDATIONS")
        print("=" * 60)
        
        if results["critical_errors"]:
            print("\n🚨 ACTIONS IMMÉDIATES REQUISES:")
            critical_fixes = set()
            for error in results["critical_errors"]:
                if "ndk" in error["name"].lower() or "alooper" in error["name"].lower():
                    critical_fixes.add("1. Utiliser NDK 25 au lieu de NDK 27")
                    critical_fixes.add("2. Modifier buildozer.spec: android.ndk = 25b")
                if "java" in error["name"].lower():
                    critical_fixes.add("3. Utiliser Java 17 au lieu de Java 21")
                if "api" in error["name"].lower():
                    critical_fixes.add("4. Utiliser API 33 au lieu de API 34")
            
            for fix in sorted(critical_fixes):
                print(f"   {fix}")
        
        print("\n✅ CONFIGURATION RECOMMANDÉE:")
        print("   - Workflow: Utiliser build-buildozer.yml")
        print("   - Java: Version 17 (LTS)")
        print("   - NDK: Version 25b")
        print("   - Android API: 33")
        print("   - Build tool: Buildozer (au lieu de p4a direct)")
        
        print("\n🔧 FIXES AUTOMATIQUES DISPONIBLES:")
        buildozer_fixes = self.generate_buildozer_fix(results)
        if buildozer_fixes:
            print("\n   Ajouts pour buildozer.spec:")
            for line in buildozer_fixes.split('\n'):
                print(f"   {line}")
        
        workflow_fixes = self.generate_workflow_fix(results)
        if workflow_fixes:
            print("\n   Modifications pour workflow:")
            for line in workflow_fixes.split('\n'):
                print(f"   {line}")


def main():
    """Fonction principale pour analyser les logs."""
    print("🔧 Diagnostic des Erreurs de Build Android")
    print("=" * 50)
    
    # Simuler une analyse avec les erreurs connues
    sample_log = """
/home/runner/.local/share/python-for-android/build/bootstrap_builds/sdl2/jni/SDL/src/joystick/hidapi/SDL_hidapijoystick.c:997:45: warning: a function declaration without a prototype is deprecated in all versions of C [-Wstrict-prototypes]
/home/runner/.local/share/python-for-android/build/bootstrap_builds/sdl2/jni/SDL/src/sensor/android/SDL_androidsensor.c:164:9: error: 'ALooper_pollAll' is unavailable: obsoleted in Android 1 - ALooper_pollAll may ignore wakes. Use ALooper_pollOnce instead.
/usr/local/lib/android/sdk/ndk/27.2.12479018/toolchains/llvm/prebuilt/linux-x86_64/bin/clang
uses: actions/setup-java@v4 with java-version: '21'
android.api = 34
    """
    
    diagnostic = AndroidBuildDiagnostic()
    results = diagnostic.analyze_log(sample_log)
    diagnostic.print_report(results)
    
    # Mode interactif pour analyser un fichier de log
    print("\n" + "=" * 60)
    print("📁 ANALYSE INTERACTIVE")
    print("=" * 60)
    print("Collez votre log d'erreur ci-dessous (tapez END sur une ligne seule pour terminer):")
    
    user_log_lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == "END":
                break
            user_log_lines.append(line)
        except (EOFError, KeyboardInterrupt):
            break
    
    if user_log_lines:
        user_log = '\n'.join(user_log_lines)
        print("\n🔍 Analyse de votre log...")
        user_results = diagnostic.analyze_log(user_log)
        diagnostic.print_report(user_results)
    
    print("\n👋 Diagnostic terminé!")


if __name__ == "__main__":
    main()
