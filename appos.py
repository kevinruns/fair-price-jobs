import re
import os

TEMPLATE_DIR = "templates"

def fix_apostrophes(filepath):
    """Fix apostrophes in Jinja2 translation strings."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Fix apostrophes in {{ _('...') }} strings
    content = re.sub(r"{{ _\('([^']*)'\) }}", lambda m: "{{ _('" + m.group(1).replace("'", "\\'") + "') }}", content)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Fixed apostrophes in {filepath}")

def main():
    for root, dirs, files in os.walk(TEMPLATE_DIR):
        for file in files:
            if file.endswith(".html"):
                filepath = os.path.join(root, file)
                fix_apostrophes(filepath)

if __name__ == "__main__":
    main()
