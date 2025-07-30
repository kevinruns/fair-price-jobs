import re
import os

def fix_template_file(filepath):
    """Fix template syntax issues in a file with a more robust approach."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Step 1: Fix {{% -> {%
    content = re.sub(r'\{\{%', '{%', content)
    
    # Step 2: Fix %}} -> %}
    content = re.sub(r'%\}\}', '%}', content)
    
    # Step 3: Fix multiple opening braces before _() calls
    # This will catch any number of { before _(
    content = re.sub(r'\{+\s*_\(', '{{ _(', content)
    
    # Step 4: Fix multiple closing braces after _() calls
    # This will catch any number of } after )
    content = re.sub(r'\)\s*\}+\s*', ') }}', content)
    
    # Step 5: Fix url_for with extra braces
    content = re.sub(r'url_for\(([^)]+)\)\}+\}+\}+\}', r'url_for(\1)', content)
    content = re.sub(r'url_for\(([^)]+)\)\}+\}+\}', r'url_for(\1)', content)
    content = re.sub(r'url_for\(([^)]+)\)\}+\}', r'url_for(\1)', content)
    
    # Step 6: Fix error.message with extra braces
    content = re.sub(r'\{\{\s*error\.message\s*\}\}+\}', '{{ error.message }}', content)
    
    # Step 7: Fix any remaining triple or more braces
    content = re.sub(r'\{\{\{+', '{{', content)
    content = re.sub(r'\}+\}\}', '}}', content)
    
    # Step 8: Fix any remaining double braces that shouldn't be there
    # Look for patterns like {{ _('text') }} that have extra braces
    content = re.sub(r'\{\{\{\{\s*_\(([^)]+)\)\s*\}\}\}\}', r'{{ _(\1) }}', content)
    content = re.sub(r'\{\{\{\s*_\(([^)]+)\)\s*\}\}\}', r'{{ _(\1) }}', content)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Fixed template syntax in {filepath}")

def main():
    """Fix all HTML template files."""
    template_dir = "templates"
    
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith(".html"):
                filepath = os.path.join(root, file)
                fix_template_file(filepath)

if __name__ == "__main__":
    main()
    print("All template files have been fixed!")

import re

def fix_french_translations():
    """Fix French translations by replacing empty msgstr with actual translations."""
    filepath = "translations/fr/LC_MESSAGES/messages.po"
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Dictionary of translations to replace
    translations = {
        'msgid "500"\nmsgstr ""': 'msgid "500"\nmsgstr "500"',
        'msgid "Internal Server Error"\nmsgstr ""': 'msgid "Internal Server Error"\nmsgstr "Erreur Interne du Serveur"',
        'msgid "Something went wrong on our end. Please try again later."\nmsgstr ""': 'msgid "Something went wrong on our end. Please try again later."\nmsgstr "Quelque chose s\'est mal passé de notre côté. Veuillez réessayer plus tard."',
        'msgid "Error:"\nmsgstr ""': 'msgid "Error:"\nmsgstr "Erreur:"',
        'msgid "Return to Home"\nmsgstr ""': 'msgid "Return to Home"\nmsgstr "Retour à l\'Accueil"',
        'msgid "Go Back"\nmsgstr ""': 'msgid "Go Back"\nmsgstr "Retour"',
        'msgid "Fair Price Jobs"\nmsgstr ""': 'msgid "Fair Price Jobs"\nmsgstr "Emplois à Prix Juste"',
        'msgid "Home"\nmsgstr ""': 'msgid "Home"\nmsgstr "Accueil"',
        'msgid "Jobs & Quotes"\nmsgstr ""': 'msgid "Jobs & Quotes"\nmsgstr "Travaux et Devis"',
        'msgid "Tradesmen"\nmsgstr ""': 'msgid "Tradesmen"\nmsgstr "Artisans"',
        'msgid "Groups"\nmsgstr ""': 'msgid "Groups"\nmsgstr "Groupes"',
        'msgid "Log Out"\nmsgstr ""': 'msgid "Log Out"\nmsgstr "Déconnexion"',
        'msgid "Register"\nmsgstr ""': 'msgid "Register"\nmsgstr "S\'inscrire"',
        'msgid "Log In"\nmsgstr ""': 'msgid "Log In"\nmsgstr "Se connecter"',
        'msgid "Top Rated Tradesmen"\nmsgstr ""': 'msgid "Top Rated Tradesmen"\nmsgstr "Artisans les Mieux Notés"',
        'msgid "Search Tradesmen"\nmsgstr ""': 'msgid "Search Tradesmen"\nmsgstr "Rechercher des Artisans"',
        'msgid "Add Tradesman"\nmsgstr ""': 'msgid "Add Tradesman"\nmsgstr "Ajouter un Artisan"',
        'msgid "Name"\nmsgstr ""': 'msgid "Name"\nmsgstr "Nom"',
        'msgid "Trade"\nmsgstr ""': 'msgid "Trade"\nmsgstr "Métier"',
        'msgid "Rating"\nmsgstr ""': 'msgid "Rating"\nmsgstr "Note"',
        'msgid "Jobs"\nmsgstr ""': 'msgid "Jobs"\nmsgstr "Travaux"',
        'msgid "Quotes"\nmsgstr ""': 'msgid "Quotes"\nmsgstr "Devis"',
        'msgid "Added By"\nmsgstr ""': 'msgid "Added By"\nmsgstr "Ajouté par"',
        'msgid "Recent Jobs & Quotes"\nmsgstr ""': 'msgid "Recent Jobs & Quotes"\nmsgstr "Travaux et Devis Récents"',
        'msgid "Search Jobs & Quotes"\nmsgstr ""': 'msgid "Search Jobs & Quotes"\nmsgstr "Rechercher Travaux et Devis"',
        'msgid "Add Job or Quote"\nmsgstr ""': 'msgid "Add Job or Quote"\nmsgstr "Ajouter un Travail ou un Devis"',
        'msgid "Type"\nmsgstr ""': 'msgid "Type"\nmsgstr "Type"',
        'msgid "Title"\nmsgstr ""': 'msgid "Title"\nmsgstr "Titre"',
        'msgid "Tradesman"\nmsgstr ""': 'msgid "Tradesman"\nmsgstr "Artisan"',
        'msgid "Date"\nmsgstr ""': 'msgid "Date"\nmsgstr "Date"',
        'msgid "Cost/Quote"\nmsgstr ""': 'msgid "Cost/Quote"\nmsgstr "Coût/Devis"',
        'msgid "My Groups"\nmsgstr ""': 'msgid "My Groups"\nmsgstr "Mes Groupes"',
        'msgid "Find Group"\nmsgstr ""': 'msgid "Find Group"\nmsgstr "Trouver un Groupe"',
        'msgid "Create Group"\nmsgstr ""': 'msgid "Create Group"\nmsgstr "Créer un Groupe"',
        'msgid "You haven\'t joined any groups yet. Join or create groups to collaborate with others and share tradesmen recommendations."\nmsgstr ""': 'msgid "You haven\'t joined any groups yet. Join or create groups to collaborate with others and share tradesmen recommendations."\nmsgstr "Vous n\'avez pas encore rejoint de groupes. Rejoignez ou créez des groupes pour collaborer avec d\'autres et partager des recommandations d\'artisans."',
        'msgid "No Rating"\nmsgstr ""': 'msgid "No Rating"\nmsgstr "Aucune Note"',
        'msgid "Not set"\nmsgstr ""': 'msgid "Not set"\nmsgstr "Non défini"',
        'msgid "None"\nmsgstr ""': 'msgid "None"\nmsgstr "Aucun"',
        'msgid "Job"\nmsgstr ""': 'msgid "Job"\nmsgstr "Travail"',
        'msgid "Quote"\nmsgstr ""': 'msgid "Quote"\nmsgstr "Devis"',
        'msgid "Cancel"\nmsgstr ""': 'msgid "Cancel"\nmsgstr "Annuler"',
        'msgid "Save Changes"\nmsgstr ""': 'msgid "Save Changes"\nmsgstr "Enregistrer les Modifications"',
        'msgid "Edit Profile"\nmsgstr ""': 'msgid "Edit Profile"\nmsgstr "Modifier le Profil"',
        'msgid "Username:"\nmsgstr ""': 'msgid "Username:"\nmsgstr "Nom d\'utilisateur:"',
        'msgid "First Name:"\nmsgstr ""': 'msgid "First Name:"\nmsgstr "Prénom:"',
        'msgid "Last Name:"\nmsgstr ""': 'msgid "Last Name:"\nmsgstr "Nom de famille:"',
        'msgid "Email:"\nmsgstr ""': 'msgid "Email:"\nmsgstr "Email:"',
        'msgid "Password:"\nmsgstr ""': 'msgid "Password:"\nmsgstr "Mot de passe:"',
        'msgid "Confirm Password:"\nmsgstr ""': 'msgid "Confirm Password:"\nmsgstr "Confirmer le mot de passe:"',
        'msgid "Submit"\nmsgstr ""': 'msgid "Submit"\nmsgstr "Soumettre"',
        'msgid "Search"\nmsgstr ""': 'msgid "Search"\nmsgstr "Rechercher"',
        'msgid "Add"\nmsgstr ""': 'msgid "Add"\nmsgstr "Ajouter"',
        'msgid "Edit"\nmsgstr ""': 'msgid "Edit"\nmsgstr "Modifier"',
        'msgid "Delete"\nmsgstr ""': 'msgid "Delete"\nmsgstr "Supprimer"',
        'msgid "View"\nmsgstr ""': 'msgid "View"\nmsgstr "Voir"',
        'msgid "Back"\nmsgstr ""': 'msgid "Back"\nmsgstr "Retour"',
        'msgid "Next"\nmsgstr ""': 'msgid "Next"\nmsgstr "Suivant"',
        'msgid "Previous"\nmsgstr ""': 'msgid "Previous"\nmsgstr "Précédent"',
        'msgid "Yes"\nmsgstr ""': 'msgid "Yes"\nmsgstr "Oui"',
        'msgid "No"\nmsgstr ""': 'msgid "No"\nmsgstr "Non"',
        'msgid "OK"\nmsgstr ""': 'msgid "OK"\nmsgstr "OK"',
        'msgid "Close"\nmsgstr ""': 'msgid "Close"\nmsgstr "Fermer"',
        'msgid "Loading..."\nmsgstr ""': 'msgid "Loading..."\nmsgstr "Chargement..."',
        'msgid "Success"\nmsgstr ""': 'msgid "Success"\nmsgstr "Succès"',
        'msgid "Error"\nmsgstr ""': 'msgid "Error"\nmsgstr "Erreur"',
        'msgid "Warning"\nmsgstr ""': 'msgid "Warning"\nmsgstr "Avertissement"',
        'msgid "Info"\nmsgstr ""': 'msgid "Info"\nmsgstr "Information"'
    }
    
    # Replace empty msgstr with translations
    for english, french in translations.items():
        content = content.replace(english, french)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    print("Fixed French translations in messages.po")

if __name__ == "__main__":
    fix_french_translations()

import re

def fix_fuzzy_translations():
    """Remove fuzzy flags from translations."""
    filepath = "translations/fr/LC_MESSAGES/messages.po"
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Remove fuzzy flags from specific translations
    translations_to_fix = [
        'msgid "Jobs & Quotes"',
        'msgid "Tradesmen"',
        'msgid "Groups"'
    ]
    
    for translation in translations_to_fix:
        # Find the pattern: #, fuzzy\nmsgid "translation"
        pattern = rf'#, fuzzy\n{re.escape(translation)}'
        replacement = translation
        content = re.sub(pattern, replacement, content)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    print("Removed fuzzy flags from translations")

if __name__ == "__main__":
    fix_fuzzy_translations()
