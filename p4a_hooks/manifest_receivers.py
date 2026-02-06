from pathlib import Path
import os
import re
import sys

def _find_manifest_path(toolchain):
  candidates = [
    Path('src') / 'main' / 'AndroidManifest.xml',
  ]
  try:
    dist_name = getattr(toolchain.args, 'dist_name', None) or getattr(toolchain, 'dist_name', None)
    if dist_name:
      candidates.append(Path('dists') / dist_name / 'src' / 'main' / 'AndroidManifest.xml')
  except Exception:
    pass
  try:
    dist_dir = getattr(toolchain, 'dist_dir', None)
    if dist_dir:
      candidates.append(Path(dist_dir) / 'src' / 'main' / 'AndroidManifest.xml')
  except Exception:
    pass
  for p in candidates:
    if p and Path(p).exists():
      return Path(p)
  return None

def _all_bootstrap_files(toolchain, filename_pattern):
  files = []
  search_roots = []

  # 1) dist_dir (primary during build)
  try:
    dist_dir = getattr(toolchain, 'dist_dir', None)
    if dist_dir:
      dist_path = Path(dist_dir)
      if dist_path.exists():
        search_roots.append(dist_path)
        # build root is two levels up from dists/<name>
        build_root = dist_path.parent.parent
        if build_root.exists():
          search_roots.append(build_root)
          search_roots.append(build_root / 'build')
          search_roots.append(build_root / 'build' / 'bootstrap_builds')
  except Exception:
    pass

  # 2) toolchain build_dir (if available)
  try:
    build_dir = getattr(toolchain, 'build_dir', None)
    if build_dir:
      build_path = Path(build_dir)
      if build_path.exists():
        search_roots.append(build_path)
  except Exception:
    pass

  # 3) Fallback to current working directory
  search_roots.append(Path.cwd())

  # De-duplicate search roots
  unique_roots = []
  for root in search_roots:
    if root not in unique_roots:
      unique_roots.append(root)

  for root in unique_roots:
    try:
      if root.exists():
        files.extend(list(root.rglob(filename_pattern)))
    except Exception:
      pass

  return files

def _patch_python_activity(toolchain):
  """Remove setRequestedOrientation calls for Android 16+ large screen support"""  
  print("[HOOK] _patch_python_activity executing...")
  python_activity_files = _all_bootstrap_files(toolchain, 'PythonActivity.java')
  
  if not python_activity_files:
      print("[HOOK] ⚠️ No PythonActivity.java found to patch! Checked dist_dir and CWD.")
      return

  print(f"[HOOK] Found {len(python_activity_files)} PythonActivity.java files.")

  for java_file in python_activity_files:
    try:
        content = java_file.read_text(encoding='utf-8')
        modified_lines = []
        lines = content.splitlines()
        changes_count = 0
        
        for line in lines:
            if 'setRequestedOrientation' in line:
                modified_lines.append('// ' + line + ' // REMOVED FOR LARGE SCREEN SUPPORT')
                changes_count += 1
            else:
                modified_lines.append(line)
        
        if changes_count > 0:
            java_file.write_text('\n'.join(modified_lines), encoding='utf-8')
            print(f"[HOOK] ✅ Patched {changes_count} lines in {java_file}")
        else:
            print(f"[HOOK] No setRequestedOrientation found in {java_file}")
            
    except Exception as e:
        print(f"[HOOK] Error patching {java_file}: {e}")

def _patch_application_mk(toolchain):
    """Inject 16KB page size flags into Application.mk"""
    print("[HOOK] _patch_application_mk executing...")
    # Typically in dist_dir/jni/Application.mk
    mk_files = _all_bootstrap_files(toolchain, 'Application.mk')
    
    if not mk_files:
        print("[HOOK] ⚠️ No Application.mk found to patch! Checked dist_dir and CWD.")
        return

    print(f"[HOOK] Found {len(mk_files)} Application.mk files.")
    
    flags = "APP_LDFLAGS += -Wl,-z,max-page-size=16384 -Wl,-z,common-page-size=16384"
    cpp_fix = "APP_CPPFLAGS += -Wno-error=cast-function-type -Wno-error=cast-function-type-strict"
    c_fix = "APP_CFLAGS += -Wno-error=cast-function-type -Wno-error=cast-function-type-strict"
    
    for mk_file in mk_files:
        try:
            content = mk_file.read_text(encoding='utf-8')
            needs_16kb = 'max-page-size=16384' not in content
            needs_cpp_fix = 'cast-function-type' not in content

            if needs_16kb or needs_cpp_fix:
                additions = []
                if needs_16kb:
                    additions.append(flags)
                if needs_cpp_fix:
                    additions.append(cpp_fix)
                    additions.append(c_fix)
                new_content = content + "\n# 16KB Support\n" + "\n".join(additions) + "\n"
                mk_file.write_text(new_content, encoding='utf-8')
                print(f"[HOOK] ✅ Injected flags in {mk_file}")
            else:
                print(f"[HOOK] ℹ️  Flags already present in {mk_file}")
        except Exception as e:
            print(f"[HOOK] Error patching {mk_file}: {e}")

def _patch_android_mk_flags(toolchain):
    """Inject harfbuzz cast-function-type suppression into Android.mk"""
    print("[HOOK] _patch_android_mk_flags executing...")
    mk_files = _all_bootstrap_files(toolchain, 'Android.mk')
    if not mk_files:
        print("[HOOK] ⚠️ No Android.mk found to patch! Checked dist_dir and CWD.")
        return

    flag_line = "LOCAL_CPPFLAGS += -Wno-error=cast-function-type -Wno-error=cast-function-type-strict"
    c_flag_line = "LOCAL_CFLAGS += -Wno-error=cast-function-type -Wno-error=cast-function-type-strict"
    insert_block = "\n# Harfbuzz strict cast fix\n" + flag_line + "\n" + c_flag_line + "\n"

    for mk_file in mk_files:
        try:
            path_str = str(mk_file)
            if 'harfbuzz/Android.mk' not in path_str.replace('\\', '/'):
                continue
            content = mk_file.read_text(encoding='utf-8')
            if 'cast-function-type' in content:
                print(f"[HOOK] ℹ️  Harfbuzz flags already present in {mk_file}")
                continue

            if 'include $(BUILD_STATIC_LIBRARY)' in content:
                new_content = content.replace('include $(BUILD_STATIC_LIBRARY)', insert_block + 'include $(BUILD_STATIC_LIBRARY)', 1)
            elif 'include $(BUILD_SHARED_LIBRARY)' in content:
                new_content = content.replace('include $(BUILD_SHARED_LIBRARY)', insert_block + 'include $(BUILD_SHARED_LIBRARY)', 1)
            else:
                new_content = content + insert_block

            mk_file.write_text(new_content, encoding='utf-8')
            print(f"[HOOK] ✅ Injected harfbuzz flags in {mk_file}")
        except Exception as e:
            print(f"[HOOK] Error patching {mk_file}: {e}")

def before_apk_build(toolchain):
  print("[HOOK] before_apk_build called")
  
  # 1. Patch Manifest (Orientation & Receivers)
  manifest = _find_manifest_path(toolchain)
  if manifest and manifest.exists():
    txt = manifest.read_text(encoding='utf-8')
    
    if 'org.tarot.DailyReminderReceiver' not in txt:
      inject = (
        '    <receiver android:name="org.tarot.DailyReminderReceiver" android:exported="false" />\n'
        '    <receiver android:name="org.tarot.BootCompletedReceiver" android:enabled="true" android:exported="true">\n'
        '      <intent-filter>\n'
        '        <action android:name="android.intent.action.BOOT_COMPLETED" />\n'
        '        <action android:name="android.intent.action.LOCKED_BOOT_COMPLETED" />\n'
        '      </intent-filter>\n'
        '    </receiver>\n'
      )
      if '<activity' in txt:
        txt = txt.replace('<activity', inject + '    <activity', 1)
      elif '</application>' in txt:
        txt = txt.replace('</application>', inject + '  </application>', 1)
      else:
        txt = txt + '\n' + inject
    
    orientation_pattern = r'\s*android:screenOrientation="[^"]+"'
    if re.search(orientation_pattern, txt, re.IGNORECASE):
      txt = re.sub(orientation_pattern, '', txt, flags=re.IGNORECASE)
      print("[HOOK] ✅ Removed screenOrientation restriction from AndroidManifest.xml")
    
    manifest.write_text(txt, encoding='utf-8')
  else:
      print("[HOOK] ⚠️ AndroidManifest.xml not found")

  # 2. Patch Code (PythonActivity.java)
  _patch_python_activity(toolchain)
  
  # 3. Patch Native Build (Application.mk) for 16KB support
  _patch_application_mk(toolchain)
  _patch_android_mk_flags(toolchain)


def before_apk_assemble(toolchain):
  try:
    before_apk_build(toolchain)
  except Exception:
    pass

def before_build(toolchain):
  """Inject 16KB page size flags into environment for all recipes"""
  print("[HOOK] before_build called (16KB env flags)")
  _patch_application_mk(toolchain)
  _patch_android_mk_flags(toolchain)
  ld_flags = '-Wl,-z,max-page-size=16384 -Wl,-z,common-page-size=16384 -Wl,--no-warn-mismatch'
  strict_cast_fix = '-Wno-error=cast-function-type -Wno-error=cast-function-type-strict'
  app_ld_flags = '-Wl,-z,max-page-size=16384 -Wl,-z,common-page-size=16384'
  for var in ['LDFLAGS', 'CFLAGS', 'CXXFLAGS', 'CPPFLAGS']:
    current = os.environ.get(var, '')
    if 'max-page-size=16384' not in current:
      os.environ[var] = f"{current} {ld_flags}".strip()
      print(f"[HOOK] ✅ {var} = {os.environ[var]}")
  cxx_current = os.environ.get('CXXFLAGS', '')
  if 'cast-function-type' not in cxx_current:
    os.environ['CXXFLAGS'] = f"{cxx_current} {strict_cast_fix}".strip()
    print(f"[HOOK] ✅ CXXFLAGS (harfbuzz fix) = {os.environ['CXXFLAGS']}")

  cpp_current = os.environ.get('CPPFLAGS', '')
  if 'cast-function-type' not in cpp_current:
    os.environ['CPPFLAGS'] = f"{cpp_current} {strict_cast_fix}".strip()
    print(f"[HOOK] ✅ CPPFLAGS (harfbuzz fix) = {os.environ['CPPFLAGS']}")

  app_ld_current = os.environ.get('APP_LDFLAGS', '')
  if 'max-page-size=16384' not in app_ld_current:
    os.environ['APP_LDFLAGS'] = f"{app_ld_current} {app_ld_flags}".strip()
    print(f"[HOOK] ✅ APP_LDFLAGS = {os.environ['APP_LDFLAGS']}")

  app_cpp_current = os.environ.get('APP_CPPFLAGS', '')
  if 'cast-function-type' not in app_cpp_current:
    os.environ['APP_CPPFLAGS'] = f"{app_cpp_current} {strict_cast_fix}".strip()
    print(f"[HOOK] ✅ APP_CPPFLAGS (harfbuzz fix) = {os.environ['APP_CPPFLAGS']}")

  app_c_current = os.environ.get('APP_CFLAGS', '')
  if 'cast-function-type' not in app_c_current:
    os.environ['APP_CFLAGS'] = f"{app_c_current} {strict_cast_fix}".strip()
    print(f"[HOOK] ✅ APP_CFLAGS (harfbuzz fix) = {os.environ['APP_CFLAGS']}")
