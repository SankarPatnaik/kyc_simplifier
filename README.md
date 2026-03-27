Here is a clean, professional **README.md** for your GitHub repository.
You can copy–paste this directly into your repo.

---

# **KYC Email Simplifier**

A fully rule-based (non-GenAI) engine that converts technical KYC requirement descriptions into clear, client-friendly language. Designed for organizations that cannot use GenAI in production but still want human-readable emails for customers during KYC Renewals, Reviews, and Client Refresh processes.

This package includes:

* 🔹 YAML-driven configuration (easy to customize)
* 🔹 Rule-based jargon simplification
* 🔹 Tone softening for client communication
* 🔹 Document name rewriting (passport → “clear copy of your passport”)
* 🔹 Sentence simplification engine
* 🔹 Bulk converter to process template folders
* 🔹 FastAPI REST wrapper to integrate with internal systems

---

# **📦 Project Structure**

```
kyc_simplifier/
│── config.yaml                # Configurable rewriting rules
│── simplifier.py             # Core rule-based simplifier
│── bulk_convert.py           # Script to convert template folders
└── api.py                    # FastAPI-based REST API
```

---

# **🚀 Getting Started**

## **1. Install Dependencies**

```bash
pip install fastapi uvicorn pyyaml python-multipart
pip install "ebcdic>=1.1.1,<2" extract-msg
```

If `extract-msg` fails to install (common resolver issues around `ebcdic` on some Python 3.12 environments), use a clean virtualenv and install with explicit pins:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install "ebcdic>=1.1.1,<2" "extract-msg"
```

If your platform still cannot resolve `extract-msg` on Python 3.12, run `.msg` conversion on Python 3.11 for now.

(Optional) Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

---

# **🧠 How It Works**

The engine does NOT use AI or machine learning.
It relies on:

* Dictionary replacements
* Phrase-level patterns
* Tone adjustments
* Document restructuring
* Sentence rewriting

All driven by `config.yaml`, so you can update rules without touching the code.

Example:

```yaml
jargon_map:
  "Periodic Review": "regular review"
tone_map:
  "submit": "share"
kyc_documents:
  "certificate of incorporation": "a copy of your Certificate of Incorporation"
```

---

# **📝 Usage**

## **2. Use Simplifier in Python**

```python
from simplifier import EmailSimplifier

simplifier = EmailSimplifier("config.yaml")

text = """
During Periodic Review/Client Refresh, the KYC Maker compares the data attributes...
"""

output = simplifier.simplify_text(text)
print(output)
```

---

## **📨 Convert Outlook `.msg` Emails**

Convert a Microsoft Outlook message file into a structured, customer-friendly
email payload:

```bash
python msg_convert.py --input ./raw_email.msg --output ./raw_email.simplified.json
```

The output JSON includes:

* `subject`, `sender`, `to`, `cc`, `date`
* `original_body`
* `simplified_body` (ready for KYC Renewal/Review/Client Refresh communication)

---

# **📚 Bulk Convert Templates**

Convert all `.txt`, `.md`, `.html` files in a folder:

```bash
python bulk_convert.py --input ./raw_templates --output ./client_ready_templates
```

This will rewrite all templates using the rule engine.

## **📄 Convert JSON Template Payloads**

If your template generator emits JSON instead of loose text files, you can rewrite
the payload end-to-end without changing its structure:

```bash
python json_convert.py --input ./templates.json --output ./templates.simplified.json
```

Key options:

* `--text-field` — name of the field that contains the template text (default: `text`)
* `--output-field` — where to store the simplified text (default: `simplified_text`)
* `--config` — path to the YAML ruleset (default: `config.yaml`)

The converter walks any lists or nested objects, rewrites the configured text
field, and writes a JSON file with the new field added alongside the original
content.

---

# **🌐 Run the FastAPI Service**

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Test the API

```bash
curl -X POST http://localhost:8000/simplify-text \
     -H "Content-Type: application/json" \
     -d '{"text": "your technical content here"}'
```

You can also upload Outlook `.msg` files directly to the API:

```bash
curl -X POST http://localhost:8000/simplify-msg \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@./raw_email.msg"
```


---

# **🧩 Integrating With Your Existing KYC Template Generator**

If your KYC system already builds email templates (from Confluence or internal tools):

1. Generate your technical template as usual
2. Pass the generated text through the simplifier
3. Send the edited version to clients

Example:

```python
technical = render_template(data)
client_friendly = simplifier.simplify_text(technical)
send_email(client_friendly)
```

---

# **📁 Configuration (config.yaml)**

All rewriting behavior lives in `config.yaml`.
You can tune:

* Jargon mapping
* KYC document name mapping
* Tone conversion rules
* Phrase patterns
* Sentence length thresholds
* Boilerplate pieces

This makes the system adaptable to:

* Global KYC teams
* Country-specific legal wording
* Risk document requirements
* Entity type (Corp, Partnership, Trust, etc.)

---

# **🛠 Customization**

You can easily extend this engine:

* Add new KYC document types
* Add per-country language rules
* Add complex pattern rewriting
* Add more sections for tone control
* Add table/grid generators for your emails

If needed, you can request a full enterprise-grade version.

---

# **📄 License**

Internal use only — please update with your organization’s licensing policy.

---

If you'd like, I can also generate:

* A **Dockerfile**
* A **GitHub Actions CI/CD pipeline**
* A **Confluence exporter → Simplifier pipeline script**
* A **template grid/table generator** for the KYC email body

Just tell me!
# kyc_simplifier
