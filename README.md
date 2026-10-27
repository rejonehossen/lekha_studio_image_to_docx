# Lekha Studio

**Bangla & English OCR Book Publishing Studio** — transform images containing handwritten or
printed Bangla and English into professionally organized, editable, publication-quality
Microsoft Word (DOCX) documents.

Local-first. No login. No REST API. One Django app. One custom model.

---

## Quick start

```bash
# 1. Clone
git clone <your-repo-url> lekha_studio
cd lekha_studio

# 2. Virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 3. Dependencies
pip install -r requirements.txt

# 4. System OCR (see OCR setup below)
#    Linux:  sudo apt install tesseract-ocr tesseract-ocr-eng tesseract-ocr-ben
#    macOS:  brew install tesseract tesseract-lang
#    Windows: https://github.com/UB-Mannheim/tesseract/wiki (check Bengali)

# 5. Config
cp .env.example .env
#    Edit .env — set DJANGO_SECRET_KEY to a long random value.

# 6. Database + run
python manage.py migrate
python manage.py check
python manage.py runserver
