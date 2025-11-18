import sys
import os
from dotenv import load_dotenv

# Підключаємо проєкт
sys.path.insert(0, os.path.abspath(".."))

# Підвантажуємо змінні середовища з .env
load_dotenv(dotenv_path=os.path.abspath("..") + "/.env")

# -- Project information -----------------------------------------------------
project = "web14hm"
copyright = "2025, Taras"
author = "Taras"

# -- General configuration ---------------------------------------------------
extensions = ["sphinx.ext.autodoc"]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
html_theme = "nature"
html_static_path = ["_static"]
