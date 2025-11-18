import os

from openai import OpenAI



api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("Erreur: la variable d'environnement OPENAI_API_KEY n'est pas définie.")
    print("Exportez votre clé avant de lancer ce script.")
    exit(1)

client = OpenAI(api_key=api_key)

print("Modèles accessibles avec cette clé:\n")
models = client.models.list()
print(models)
# l'attribut .data contient la liste des modèles
for m in models.data:
    print(m.id)


