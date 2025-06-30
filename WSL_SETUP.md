# Installation WSL2 pour compilation Android

## 1. Installer WSL2
```powershell
# Dans PowerShell en admin:
wsl --install -d Ubuntu
```

## 2. Installer les dépendances dans Ubuntu
```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-8-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

pip3 install buildozer cython
```

## 3. Compiler l'APK
```bash
cd /mnt/e/programmes/projects/kivy_app
buildozer android debug
```

## 4. Récupérer l'APK
L'APK sera dans le dossier `bin/` de votre projet.
