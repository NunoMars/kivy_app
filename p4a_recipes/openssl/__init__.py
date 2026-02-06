from pythonforandroid.recipes.openssl import OpenSSLRecipe


class OpenSSLRecipeCustom(OpenSSLRecipe):
    """Custom OpenSSL recipe forcing 16KB alignment for libssl + libcrypto"""
    
    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        """Override to inject 16KB flags before OpenSSL Configure script"""
        env = super().get_recipe_env(arch)
        
        # Force 16KB page alignment flags
        flags_16kb = '-Wl,-z,max-page-size=16384 -Wl,-z,common-page-size=16384'
        
        # Inject dans LDFLAGS (OpenSSL Configure utilise LDFLAGS)
        ldflags = env.get('LDFLAGS', '')
        if flags_16kb not in ldflags:
            env['LDFLAGS'] = f"{ldflags} {flags_16kb}".strip()
            print(f"[OPENSSL-16KB] ✅ LDFLAGS={env['LDFLAGS']}")
        
        # Inject aussi dans CFLAGS pour être sûr (OpenSSL peut utiliser)
        cflags = env.get('CFLAGS', '')
        if flags_16kb not in cflags:
            env['CFLAGS'] = f"{cflags} {flags_16kb}".strip()
            print(f"[OPENSSL-16KB] ✅ CFLAGS={env['CFLAGS']}")
        
        return env


recipe = OpenSSLRecipeCustom()
