from pythonforandroid.recipes.sqlite3 import Sqlite3Recipe
import os


class Sqlite3RecipeCustom(Sqlite3Recipe):
    """Custom SQLite recipe forcing 16KB alignment for libsqlite3.so"""
    
    def build_arch(self, arch):
        """Override to patch Android.mk before build"""
        super().build_arch(arch)
        
        # Patch le fichier Android.mk de sqlite3 pour ajouter les flags 16KB
        android_mk = os.path.join(self.get_build_dir(arch.arch), 'jni', 'Android.mk')
        
        if os.path.exists(android_mk):
            with open(android_mk, 'r') as f:
                content = f.read()
            
            # Ajouter les flags 16KB si pas déjà présents
            flags_16kb = '-Wl,-z,max-page-size=16384 -Wl,-z,common-page-size=16384'
            
            if flags_16kb not in content:
                # Ajouter avant LOCAL_MODULE
                if 'LOCAL_MODULE' in content:
                    content = content.replace(
                        'LOCAL_MODULE',
                        f'LOCAL_LDFLAGS := {flags_16kb}\nLOCAL_MODULE'
                    )
                    
                    with open(android_mk, 'w') as f:
                        f.write(content)
                    
                    print(f"[SQLITE3-16KB] ✅ Patched Android.mk with 16KB flags")
                    
    def prebuild_arch(self, arch):
        """Hook avant le build pour patcher Android.mk"""
        super().prebuild_arch(arch)
        
        android_mk = os.path.join(self.get_build_dir(arch.arch), 'jni', 'Android.mk')
        
        if os.path.exists(android_mk):
            with open(android_mk, 'r') as f:
                content = f.read()
            
            flags_16kb = '-Wl,-z,max-page-size=16384 -Wl,-z,common-page-size=16384'
            
            if flags_16kb not in content and 'LOCAL_MODULE' in content:
                content = content.replace(
                    'LOCAL_MODULE',
                    f'LOCAL_LDFLAGS := {flags_16kb}\nLOCAL_MODULE',
                    1
                )
                
                with open(android_mk, 'w') as f:
                    f.write(content)
                
                print(f"[SQLITE3-16KB] ✅ Patched Android.mk with 16KB flags")


recipe = Sqlite3RecipeCustom()
