#!/bin/bash
# Script pour injecter les flags 16KB AVANT le build p4a

set -e

echo "================================================================================"
echo "[16KB PRE-BUILD] Injection des flags 16KB pour Android 15+ compatibility"
echo "================================================================================"

# Définir les flags
export LDFLAGS="-Wl,-z,max-page-size=16384 -Wl,-z,common-page-size=16384 ${LDFLAGS}"
export CFLAGS="-Wl,-z,max-page-size=16384 ${CFLAGS}"
export CXXFLAGS="-Wl,-z,max-page-size=16384 ${CXXFLAGS}"

echo "[16KB PRE-BUILD] ✅ LDFLAGS=${LDFLAGS}"
echo "[16KB PRE-BUILD] ✅ CFLAGS=${CFLAGS}"
echo "[16KB PRE-BUILD] ✅ CXXFLAGS=${CXXFLAGS}"

# Patcher Application.mk si le bootstrap existe déjà
APP_MK=".buildozer/android/platform/build-arm64-v8a/build/bootstrap_builds/sdl2/jni/Application.mk"
if [ -f "$APP_MK" ]; then
  if ! grep -q "max-page-size=16384" "$APP_MK"; then
    echo "" >> "$APP_MK"
    echo "# 16KB page size support for Android 15+" >> "$APP_MK"
    echo "APP_LDFLAGS += -Wl,-z,max-page-size=16384 -Wl,-z,common-page-size=16384" >> "$APP_MK"
    echo "[16KB PRE-BUILD] ✅ Patched Application.mk"
  else
    echo "[16KB PRE-BUILD] ℹ️  Application.mk already patched"
  fi
else
  echo "[16KB PRE-BUILD] ⚠️  Application.mk not found (will be created during build)"
fi

echo "================================================================================"

# Lancer buildozer avec les flags
buildozer android release
