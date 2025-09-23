# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
import django

os.environ["SPHINX_BUILD"] = "1"

# Caminho raiz do projeto
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

# Caminho da pasta 'web' (onde estão chatbot, crawler, web/settings.py, etc.)
WEB_DIR = os.path.join(ROOT_DIR, "web")
sys.path.insert(0, WEB_DIR)

# Forçar o app Django (para importar settings, etc.)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
django.setup()

project = 'Pergunta que Respondo'
copyright = '2025, Felipe Toledo, Gustavo Torres, Robson Ricardo e Victor Kauan'
author = 'Felipe Toledo, Gustavo Torres, Robson Ricardo e Victor Kauan'
release = '0.2.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon'
]

templates_path = ['_templates']
exclude_patterns = []

# Mockar bibliotecas pesadas/externas para gerar doc sem rodar código real
autodoc_mock_imports = [
    "pandas",
    "numpy",
    "sklearn",
    "torch",
    "langchain",
    "langchain_core",
    "langchain_google_genai",
    "langchain_huggingface",
    "langchain_community",
    "transformers",
    "safetensors",
    "google",
    "google.generativeai",
    "faiss",
]

language = 'pt'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinxawesome_theme'
html_static_path = ['_static']
