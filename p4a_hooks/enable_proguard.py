#!/usr/bin/env python3
"""
Hook p4a pour activer ProGuard/R8 et symboles de débogage natifs
Ce hook modifie le build.gradle généré pour activer:
- minifyEnabled true (ProGuard/R8)
- debugSymbolLevel 'FULL' (symboles natifs)
"""

from pythonforandroid.toolchain import hook
from pythonforandroid.logger import info, warning
import os


@hook("before_apk_assemble")
def enable_proguard_and_debug_symbols(ctx):
    """
    Modifie le build.gradle pour activer ProGuard et les symboles de débogage.
    """
    info("🔧 Hook: Activation de ProGuard/R8 et symboles natifs...")
    
    # Chemin vers build.gradle de l'app
    gradle_file = os.path.join(ctx.dist_dir, "build.gradle")
    
    if not os.path.exists(gradle_file):
        warning(f"⚠️  build.gradle introuvable : {gradle_file}")
        return
    
    # Lire le contenu actuel
    with open(gradle_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si déjà modifié
    if 'minifyEnabled true' in content and 'debugSymbolLevel' in content:
        info("✅ ProGuard et symboles déjà activés")
        return
    
    # Trouver le bloc buildTypes { release {
    if 'buildTypes' not in content:
        warning("⚠️  Bloc buildTypes non trouvé dans build.gradle")
        return
    
    # Ajouter minifyEnabled et debugSymbolLevel dans le bloc release
    lines = content.split('\n')
    modified_lines = []
    in_release_block = False
    added_minify = False
    added_ndk = False
    
    for i, line in enumerate(lines):
        modified_lines.append(line)
        
        # Détecter le début du bloc release
        if 'release {' in line or 'release{' in line:
            in_release_block = True
            info("📍 Bloc 'release' trouvé à la ligne {i+1}")
        
        # Ajouter nos configurations dans le bloc release
        if in_release_block and not added_minify:
            # Ajouter minifyEnabled après la ligne suivante
            indent = ' ' * 12  # Indentation typique
            
            # Ajouter minifyEnabled
            if 'minifyEnabled' not in line:
                modified_lines.append(f"{indent}minifyEnabled true")
                modified_lines.append(f"{indent}shrinkResources true")
                modified_lines.append(f"{indent}proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'")
                added_minify = True
                info("✅ Ajout de minifyEnabled true")
            
            # Ajouter ndk { debugSymbolLevel }
            if not added_ndk:
                modified_lines.append(f"{indent}ndk {{")
                modified_lines.append(f"{indent}    debugSymbolLevel 'FULL'")
                modified_lines.append(f"{indent}}}")
                added_ndk = True
                info("✅ Ajout de debugSymbolLevel 'FULL'")
            
            in_release_block = False
    
    # Sauvegarder le fichier modifié
    if added_minify or added_ndk:
        with open(gradle_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(modified_lines))
        info("✅ build.gradle modifié avec succès")
    else:
        warning("⚠️  Impossible d'ajouter les configurations")


@hook("after_apk_assemble")
def copy_debug_symbols(ctx):
    """
    Copie les fichiers de débogage générés vers un emplacement accessible.
    """
    info("📦 Hook: Copie des fichiers de débogage...")
    
    import shutil
    
    # Répertoire de build
    build_dir = os.path.join(ctx.dist_dir, "build", "outputs")
    
    # Fichier de mapping ProGuard
    mapping_src = os.path.join(build_dir, "mapping", "release", "mapping.txt")
    
    # Symboles natifs
    symbols_src = os.path.join(build_dir, "native-debug-symbols", "release", "native-debug-symbols.zip")
    
    # Destination
    debug_dir = os.path.join(ctx.root_dir, "debug_symbols", f"v{ctx.buildozer.config.getdefault('app', 'version', '2.1')}")
    os.makedirs(debug_dir, exist_ok=True)
    
    # Copier mapping.txt
    if os.path.exists(mapping_src):
        shutil.copy2(mapping_src, debug_dir)
        info(f"✅ Mapping copié : {debug_dir}/mapping.txt")
    else:
        warning(f"⚠️  mapping.txt introuvable : {mapping_src}")
    
    # Copier symboles natifs
    if os.path.exists(symbols_src):
        shutil.copy2(symbols_src, debug_dir)
        info(f"✅ Symboles natifs copiés : {debug_dir}/native-debug-symbols.zip")
    else:
        warning(f"⚠️  native-debug-symbols.zip introuvable : {symbols_src}")
