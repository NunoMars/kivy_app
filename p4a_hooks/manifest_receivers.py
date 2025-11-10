from pathlib import Path

def _find_manifest_path(toolchain):
  # Most reliable: when hook runs inside dist dir (cwd = .../dists/<name>)
  candidates = [
    Path('src') / 'main' / 'AndroidManifest.xml',
  ]
  # Fallback: relative path via dist name if cwd is python-for-android root
  try:
    dist_name = getattr(toolchain.args, 'dist_name', None) or getattr(toolchain, 'dist_name', None)
    if dist_name:
      candidates.append(Path('dists') / dist_name / 'src' / 'main' / 'AndroidManifest.xml')
  except Exception:
    pass
  # Fallback: toolchain has dist_dir attribute in newer p4a
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


def before_apk_build(toolchain):
  manifest = _find_manifest_path(toolchain)
  if not manifest or not manifest.exists():
    return
  txt = manifest.read_text(encoding='utf-8')
  # Idempotence: if both receivers already present, do nothing
  if 'org.tarot.DailyReminderReceiver' in txt and 'org.tarot.BootCompletedReceiver' in txt:
    return
  inject = (
    '    <!-- Injected receivers (idempotent hook) -->\n'
    '    <receiver android:name="org.tarot.DailyReminderReceiver" android:exported="false" />\n'
    '    <receiver android:name="org.tarot.BootCompletedReceiver" android:enabled="true" android:exported="true">\n'
    '      <intent-filter>\n'
    '        <action android:name="android.intent.action.BOOT_COMPLETED" />\n'
    '        <action android:name="android.intent.action.LOCKED_BOOT_COMPLETED" />\n'
    '      </intent-filter>\n'
    '    </receiver>\n'
  )
  # Insert just before first <activity ... occurrence within <application>
  if '<activity' in txt:
    new_txt = txt.replace('<activity', inject + '\n    <activity', 1)
  else:
    # If no activity tag found, try to insert before </application>
    if '</application>' in txt:
      new_txt = txt.replace('</application>', inject + '  </application>', 1)
    else:
      # As a last resort, append at end (shouldn't happen)
      new_txt = txt + '\n' + inject
  if new_txt != txt:
    manifest.write_text(new_txt, encoding='utf-8')


def after_apk_build(toolchain):
  # Not used for now
  pass

def before_apk_assemble(toolchain):
  # Ensure receivers are present right before Gradle assemble
  try:
    before_apk_build(toolchain)
  except Exception:
    pass
