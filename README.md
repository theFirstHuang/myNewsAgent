# 🤖 LLM News Digest Agent

> **Automated research paper digest system that sends you beautiful email reports of relevant LLM research papers, tailored to your interests.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 📚 **Multi-Source Fetching**: Aggregates papers from arXiv, HuggingFace Daily Papers
- 🎯 **AI-Powered Relevance Filtering**: Uses LLM to analyze which papers match your research interests
- 📥 **PDF Processing**: Downloads papers and converts them to Markdown using MinerU
- 🧠 **Detailed Summaries**: Generates comprehensive, technical summaries of each paper
- 📊 **Beautiful HTML Reports**: Three email template styles to choose from
- 📎 **Zotero Integration**: Exports RIS files for easy import into your reference manager
- ⏰ **Scheduled Execution**: Set up cron jobs for daily or weekly digests
- 🔒 **Privacy**: Runs entirely on your machine/server

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10 - 3.13**
- **OpenAI API Key** (for GPT-4o-mini)
- **Gmail Account** with App Password
- *Optional*: **MinerU** for PDF → Markdown conversion

### 30-Second Setup

```bash
# 1. Clone repository
cd myNewsAgent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
cp config.yaml.example config.yaml
cp my_research.md.example my_research.md

# Edit .env with your API keys
# Edit config.yaml with your preferences
# Edit my_research.md with your research interests

# 4. Test email configuration
python scripts/test_email.py

# 5. Run digest
python scripts/run_digest.py
```

---

## 📦 Installation

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: Install MinerU for PDF processing
pip install mineru
```

---

## ⚙️ Configuration

### Step 1: Environment Variables (`.env`)

Copy `.env.example` to `.env` and fill in:

```bash
# OpenAI API Key
OPENAI_API_KEY=sk-proj-your-api-key-here

# Gmail App Password (NOT your regular password!)
# Generate at: https://myaccount.google.com/apppasswords
GMAIL_APP_PASSWORD=your-16-char-app-password
```

### Step 2: Configuration File (`config.yaml`)

Copy `config.yaml.example` to `config.yaml` and customize:

```yaml
research_profile:
  profile_file: "my_research.md"

sources:
  arxiv:
    enabled: true
    categories: ["cs.CL", "cs.AI", "cs.LG"]
    max_results: 30
    days_lookback: 7

llm:
  model: "gpt-4o-mini"  # Fast and cheap
  temperature: 0.3

email:
  sender_email: "your-email@gmail.com"
  recipient_email: "your-email@gmail.com"
  template: "modern"  # Options: modern, academic, minimal

processing:
  relevance_threshold: 0.7
  max_papers_to_process: 10
```

### Step 3: Research Profile (`my_research.md`)

Copy `my_research.md.example` to `my_research.md` and describe your interests:

```markdown
# My Research Interests

## Primary Areas
- Large Language Models
- Retrieval-Augmented Generation
- Model Efficiency

## Keywords
LLM, GPT, Transformer, Fine-tuning, RAG, ...
```

---

## 🎯 Usage

### Run Once

```bash
python scripts/run_digest.py
```

### Test Email

```bash
python scripts/test_email.py
```

### Schedule with Cron (Mac/Linux)

```bash
./scripts/setup_cron.sh
```

Or manually:

```bash
crontab -e

# Add: Every Monday at 9 AM
0 9 * * 1 cd /path/to/myNewsAgent && python scripts/run_digest.py >> logs/cron.log 2>&1
```

---

## 🎨 Email Templates

Three styles available:

1. **Modern**: Card-based, gradients, modern UI
2. **Academic**: Journal-style, serif fonts, traditional
3. **Minimal**: Terminal-inspired, monospace, plain

Preview: Open `templates/preview.html` in browser

Change: Set `email.template` in `config.yaml`

---

## 📂 Project Structure

```
myNewsAgent/
├── src/                  # Source code
│   ├── analyzers/        # Relevance analysis
│   ├── fetchers/         # Data sources
│   ├── generators/       # HTML/RIS generation
│   ├── processors/       # PDF processing
│   ├── summarizers/      # LLM summaries
│   └── main.py           # Main workflow
├── templates/            # Email templates
├── scripts/              # Utility scripts
├── config.yaml           # Configuration
├── .env                  # Secrets
└── my_research.md        # Your interests
```

---

## 🔧 Troubleshooting

### Gmail Authentication Failed

1. Enable 2-Step Verification: https://myaccount.google.com/security
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use 16-char app password in `.env`

### No Papers Found

- Check `days_lookback` (try 14 days)
- Verify arXiv categories are valid
- Check internet connection

### All Papers Filtered Out

- Lower `relevance_threshold` to 0.5
- Make `my_research.md` more detailed
- Check logs: `logs/digest.log`

### MinerU Not Found

Optional. To disable:
```yaml
processing:
  pdf_to_markdown:
    enabled: false
```

---

## 🛠️ Advanced

### Use Claude Instead

```yaml
llm:
  provider: "anthropic"
  model: "claude-3-5-sonnet-20241022"
```

Add to `.env`:
```
ANTHROPIC_API_KEY=sk-ant-your-key
```

---

## 📝 License

MIT License

---

## 🙏 Acknowledgments

- [arXiv](https://arxiv.org/)
- [MinerU](https://github.com/opendatalab/MinerU)
- [HuggingFace](https://huggingface.co/papers)

---

**Made with ❤️ for researchers**
