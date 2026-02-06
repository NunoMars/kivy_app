from pythonforandroid.recipes.python3 import Python3Recipe


class Python3RecipeCustom(Python3Recipe):
    """Custom Python3 recipe forcing 16KB alignment for libpython3.11.so"""
    
    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        """Override to inject 16KB flags in environment"""
        env = super().get_recipe_env(arch, with_flags_in_cc)
        
        flags_16kb = '-Wl,-z,max-page-size=16384 -Wl,-z,common-page-size=16384'
        
        # Injecter dans LDFLAGS seulement (utilisé lors du link de libpython.so)
        ldflags = env.get('LDFLAGS', '')
        if flags_16kb not in ldflags:
            env['LDFLAGS'] = f"{ldflags} {flags_16kb}".strip()
            print(f"[PYTHON3-16KB] ✅ LDFLAGS={env['LDFLAGS']}")
        
        return env


recipe = Python3RecipeCustom()
