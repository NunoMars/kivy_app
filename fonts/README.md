Placez ici vos fichiers de police (.ttf/.otf) si vous souhaitez les embarquer dans l'APK/AAB.

Exemple :

fonts/DejaVuSans.ttf
fonts/NotoColorEmoji.ttf

Le projet `main.py` essaye d'enregistrer automatiquement `DejaVuSans.ttf` s'il est présent dans ce dossier. Si vous ne mettez pas de police, Kivy utilisera sa police par défaut.

Après avoir ajouté une police :

buildozer android clean
buildozer -v android release

Remarque : vérifier que `buildozer.spec` contient `ttf,otf` dans `source.include_exts` (c'est déjà fait).