from os.path import exists, join
import os
import re

from pythonforandroid.recipe import BootstrapNDKRecipe
from pythonforandroid.toolchain import current_directory, shprint
import sh


class LibSDL2Recipe(BootstrapNDKRecipe):
    version = "2.28.5"
    url = "https://github.com/libsdl-org/SDL/releases/download/release-{version}/SDL2-{version}.tar.gz"
    md5sum = 'a344eb827a03045c9b399e99af4af13d'

    dir_name = 'SDL'

    depends = ['sdl2_image', 'sdl2_mixer', 'sdl2_ttf']

    def _append_flag(self, env, key, flag):
        current = env.get(key, '')
        if flag in current:
            return
        env[key] = (current + ' ' + flag).strip()
    
    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        
        # Le bootstrap SDL2 est copié dans build/bootstrap_builds/sdl2
        # On doit patcher Application.mk APRÈS la copie du bootstrap
        # mais AVANT l'appel à ndk-build
        
        import os.path
        
        # Trouver le répertoire du bootstrap
        bootstrap_dir = self.ctx.bootstrap.build_dir
        app_mk_path = os.path.join(bootstrap_dir, 'jni', 'Application.mk')
        
        if os.path.exists(app_mk_path):
            with open(app_mk_path, 'r') as f:
                content = f.read()
            
            flags_16kb = '-Wl,-z,max-page-size=16384 -Wl,-z,common-page-size=16384'
            
            if 'max-page-size=16384' not in content:
                # Ajouter APP_LDFLAGS à la fin du fichier
                content += f'\n# 16KB page size alignment for Android 15+ compatibility\n'
                content += f'APP_LDFLAGS := {flags_16kb}\n'
                
                with open(app_mk_path, 'w') as f:
                    f.write(content)
                
                print(f"[SDL2] ✅ Injected 16KB flags in {app_mk_path}")
            else:
                print(f"[SDL2] ℹ️  16KB flags already present in {app_mk_path}")

    def get_recipe_env(self, arch=None, with_flags_in_cc=True, with_python=True):
        env = super().get_recipe_env(
            arch=arch, with_flags_in_cc=with_flags_in_cc, with_python=with_python)
        env['APP_ALLOW_MISSING_DEPS'] = 'true'

        ld_flags = '-Wl,-z,max-page-size=16384 -Wl,-z,common-page-size=16384'
        strict_cast_fix = '-Wno-error=cast-function-type -Wno-error=cast-function-type-strict'

        self._append_flag(env, 'LDFLAGS', ld_flags)
        self._append_flag(env, 'CFLAGS', ld_flags)
        self._append_flag(env, 'CXXFLAGS', ld_flags)
        self._append_flag(env, 'CPPFLAGS', strict_cast_fix)
        self._append_flag(env, 'CXXFLAGS', strict_cast_fix)

        self._append_flag(env, 'APP_LDFLAGS', ld_flags)
        self._append_flag(env, 'APP_CPPFLAGS', strict_cast_fix)
        self._append_flag(env, 'APP_CFLAGS', strict_cast_fix)

        return env

    def should_build(self, arch):
        libdir = join(self.get_build_dir(arch.arch), "../..", "libs", arch.arch)
        libs = ['libmain.so', 'libSDL2.so', 'libSDL2_image.so', 'libSDL2_mixer.so', 'libSDL2_ttf.so']
        return not all(exists(join(libdir, x)) for x in libs)

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)

        with current_directory(self.get_jni_dir()):
            shprint(
                sh.Command(join(self.ctx.ndk_dir, "ndk-build")),
                "V=1",
                "NDK_DEBUG=" + ("1" if self.ctx.build_as_debuggable else "0"),
                _env=env
            )


recipe = LibSDL2Recipe()
