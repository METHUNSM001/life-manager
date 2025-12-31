import os
import sys

# Ensure project root is on sys.path so 'app' module can be imported when running
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app import app

print('CWD:', os.getcwd())
print('project_root:', project_root)
print('exists templates/header.html:', os.path.exists(os.path.join(project_root,'templates','header.html')))
print('app.template_folder:', app.template_folder)
print('app.root_path:', app.root_path)
loader = app.jinja_loader
print('loader type:', type(loader))
try:
    templates = loader.list_templates()
    print('number of templates found:', len(templates))
    sample = templates[:50]
    print('sample templates:', sample)
except Exception as e:
    print('list_templates error:', e)
