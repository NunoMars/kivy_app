from pythonforandroid.recipes.libffi import LibffiRecipe


class LibffiRecipeCustom(LibffiRecipe):
    """Custom libffi recipe forcing pure 16KB alignment (no mixed 4K+16K)"""
    
    def get_recipe_env(self, arch=None):
        """Override to inject 16KB flags before libffi configure script"""
        env = super().get_recipe_env(arch)
        
        # Force 16KB page alignment flags
        flags_16kb = '-Wl,-z,max-page-size=16384 -Wl,-z,common-page-size=16384'
        
        # Inject dans LDFLAGS (libffi ./configure utilise LDFLAGS)
        ldflags = env.get('LDFLAGS', '')
        if flags_16kb not in ldflags:
            env['LDFLAGS'] = f"{ldflags} {flags_16kb}".strip()
            print(f"[LIBFFI-16KB] ✅ LDFLAGS={env['LDFLAGS']}")
        
        # Inject dans CFLAGS également
        cflags = env.get('CFLAGS', '')
        if flags_16kb not in cflags:
            env['CFLAGS'] = f"{cflags} {flags_16kb}".strip()
            print(f"[LIBFFI-16KB] ✅ CFLAGS={env['CFLAGS']}")
        
        return env


recipe = LibffiRecipeCustom()
