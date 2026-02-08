# Aquila-R: Autonomous Bilingual Research Intelligence

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Aquila-R is a specialized AI agent designed for high-stakes academic research in English and Arabic. It prioritizes methodology, critical analysis, and research integrity over speed and fluency.

## 🦅 Core Mission

> **"Prioritize thinking over speed, analysis over fluency, and research integrity over convenience."**

Aquila-R is not a chatbot. It is a research intelligence system that:
1.  **Refuses hallucinations**: Never invents citations or data.
2.  **Analyzes critically**: Evaluates arguments for bias, logical fallacies, and strength.
3.  **Respects methodology**: Understands and applies diverse research paradigms (positivist, interpretivist, critical, etc.).
4.  **Operates bilingually**: Treats English and Arabic as epistemically equal languages.

---

## 🏗️ Architecture

Aquila-R is built on a modular architecture:

-   **Core**: Identity, Memory, Configuration, Agent Orchestration.
-   **Modules**:
    -   `Literature`: Source evaluation, gap identification.
    -   `Critical`: Argument analysis, bias detection.
    -   `Synthesis`: Theme identification, conceptual mapping.
    -   `Evidence`: Data analysis, causal claim verification.
    -   `Writing`: Human-in-the-loop writing support.
-   **Language**: Bilingual detection, conceptual translation, technical glossary.
-   **Methodology**: Paradigm frameworks, assumption tracking, claim validation.
-   **Tools**: Retrieval (arXiv, Scholar), Parsing (PDF, Text).

---

## 🚀 Installation

### Prerequisites

-   Python 3.10+
-   API keys for LLM providers (OpenAI, Anthropic, or Google)

### Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/hassanupf24/Aquila-R.git
    cd Aquila-R
    ```

2.  **Install dependencies:**
    ```bash
    pip install -e .
    ```

3.  **Configure environment:**
    Copy `.env.example` to `.env` and add your API keys:
    ```bash
    cp .env.example .env
    ```

---

## 💻 Usage

### CLI Commands

Aquila-R provides a rich command-line interface:

**1. Perform Analysis:**
```bash
aquila-r analyze "How does rentier state theory explain political dynamics in the Gulf?" --methodology interpretivist --language en
```

**2. Check Agent Identity:**
```bash
aquila-r identity --language ar
```

**3. Consult Technical Glossary:**
```bash
aquila-r glossary --term "civil society"
```

**4. Check System Status:**
```bash
aquila-r status
```

### Python API

You can also use Aquila-R as a library:

```python
from aquila_r import AquilaR, MethodologyParadigm

# Initialize agent
agent = AquilaR()

# Run analysis
result = agent.analyze(
    query="What are the main theoretical debates on state formation?",
    methodology=MethodologyParadigm.CRITICAL,
)

# Output results
print(result.to_markdown())
```

See `examples/basic_usage.py` for comprehensive examples.

---

## 🛡️ Research Integrity

Aquila-R enforces strict integrity rules:

-   **Citation Verification**: All citations must be verified against real sources.
-   **Uncertainty Flagging**: Claims without strong evidence are flagged or hedged.
-   **Assumption Declaration**: Methodological and theoretical assumptions are explicitly stated.
-   **Casual Interaction Prohibition**: The agent refuses to engage in casual "chatbot" conversation.

---

## 🌍 Bilingual Capabilities

-   **Language Equality**: Native processing of both English and Arabic.
-   **Conceptual Translation**: Focuses on meaning and disciplinary context rather than literal translation.
-   **Technical Glossary**: Manages specialized terminology across domains.

---

## 🤝 Contributing

Contributions are welcome! Please ensure you:
1.  Follow the code of ethics .
2.  Add tests for new functionality.
3.  Respect the bilingual nature of the project.

## 📄 License

MIT License. See `LICENSE` for details.
