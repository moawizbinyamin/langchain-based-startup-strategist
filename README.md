# 🚀 LangChain-Based Startup Strategist

A **plug-and-play startup strategy generator** that chains **OpenAI (GPT-4o-mini)** and **Gemini (2.5-flash)** with LangChain to create comprehensive startup strategies.

## ✨ What You Get

1. **Master Guidance Prompt** - Structured, exhaustive, niche-aware strategy synthesis
2. **LangChain LCEL Pipeline** - Multi-LLM steps in parallel → single JSON output
3. **Comprehensive Strategy** - 20+ structured sections covering all startup aspects

## 🏗️ Architecture

```
Input → Parallel Analysis → Synthesis → JSON Strategy
   ↓           ↓              ↓           ↓
[8 sub-chains] → [RunnableParallel] → [Master Prompt] → [Structured Output]
```

### Model Strategy
- **GPT-4o-mini** (OpenAI): Reliable structure & synthesis, good at following schemas
- **Gemini-2.5-flash** (Google): Fast ideation/divergence; great complement in parallel steps

### Parallel Steps (A-H)
1. **Problem/JTBD** (A) - Nails what hurts (and how much)
2. **Market scan** (B) - Segments, comps, whitespace ⇒ positioning & focus
3. **Personas** (C) - Who buys, their jobs/outcomes ⇒ feature + GTM alignment
4. **Solution shapes** (D) - 2–3 credible MVP configurations with tradeoffs
5. **GTM** (E) - Channels, hooks, partnerships tailored to geo/stage
6. **Tech notes** (F) - Stack, AI bits, data, compliance, scaling plan
7. **Ops** (G) - People/process/legal/tools ⇒ execution reality check
8. **Risks** (H) - Pre-mortem to steer mitigations early

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/moawizbinyamin/langchain-based-startup-strategist.git
cd langchain-based-startup-strategist
```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Set Up API Keys

Create a `.env` file in your project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

### 4. Run the Strategist

```bash
python run_strategy.py
```

## 📊 Usage Example

```python
from startup_strategist import StartupStrategist

# Initialize
strategist = StartupStrategist()

# Define your startup inputs
inputs = {
    "niche": "AI agents for ecommerce",
    "stage": "MVP",
    "geo": "Pakistan, South Asia",
    "founder_profile": "AI graduate with strong technical skills",
    "constraints": "budget constraints, need to build MVP efficiently",
    "goals": "make a proper working MVP that can be launched in the market"
}

# Generate strategy
strategy = strategist.generate_strategy(inputs)

# Print results
strategist.print_strategy(strategy)

# Save to file
import json
with open("my_strategy.json", "w", encoding="utf-8") as f:
    json.dump(strategy, f, indent=2, ensure_ascii=False)
```

## 📊 Output Schema

The strategy generates a comprehensive JSON with:

```json
{
  "assumptions": ["string", ...],
  "one_liner": "string",
  "problem_statement": "string",
  "target_personas": [
    {
      "name": "string",
      "segment": "string", 
      "primary_jobs": ["string"],
      "top_pains": ["string"],
      "must_have_outcomes": ["string"]
    }
  ],
  "market": {
    "geo": "string",
    "top_down_TAM_estimate": "string",
    "bottom_up_SAM_SOM": {
      "sam_formula": "string",
      "som_formula": "string"
    },
    "competition": [
      {
        "name": "string",
        "type": "direct|indirect|substitute",
        "edge": "string",
        "our_counter": "string"
      }
    ],
    "whitespace": ["string"]
  },
  "solution": {
    "v0_scope": ["string"],
    "v1_scope": ["string"],
    "v2_scope": ["string"],
    "core_features": ["string"],
    "delighters": ["string"],
    "exclusions": ["string"]
  },
  "tech": {
    "architecture": "string",
    "stack_choices": ["string"],
    "ai_components": ["string"],
    "data_sources": ["string"],
    "security_compliance": "string",
    "scaling_plan": "string",
    "build_vs_buy": ["string"]
  },
  "gtm": {
    "positioning": "string",
    "pricing": {
      "model": "string",
      "tiers": ["string"]
    },
    "channels": ["string"],
    "launch_plan": [
      {
        "week": 1,
        "action": "string"
      }
    ],
    "distribution_hacks": ["string"],
    "partnerships": ["string"]
  },
  "ops": {
    "team_plan": [
      {
        "role": "string",
        "seniority": "string",
        "when": "now|later"
      }
    ],
    "processes": ["string"],
    "legal_compliance": ["string"],
    "tooling": ["string"]
  },
  "metrics": {
    "north_star": "string",
    "input_metrics": ["string"],
    "diagnostic_metrics": ["string"],
    "weekly_targets_12w": [
      {
        "week": 1,
        "target": "string"
      }
    ]
  },
  "finance": {
    "budget_ceiling": "string",
    "unit_economics": {
      "cac": "string",
      "ltv": "string", 
      "payback_period": "string"
    },
    "runway_plan": "string",
    "revenue_model": ["string"]
  },
  "risks_and_mitigations": [
    {
      "risk": "string",
      "likelihood": "low|med|high",
      "mitigation": "string",
      "owner": "string"
    }
  ],
  "execution_board": [
    {
      "id": "S-1",
      "type": "spec",
      "title": "string",
      "owner": "string",
      "due": "YYYY-MM-DD"
    }
  ]
}
```

## 🎯 Example Output

**Input**: "AI agents for ecommerce"

**Output Preview**:
```json
{
  "one_liner": "AI agents designed for eCommerce in Pakistan, enhancing customer experience and driving sales through personalization and support.",
  "solution": {
    "v0_scope": ["Basic chatbot functionality", "Product recommendations"]
  },
  "gtm": {
    "channels": ["Social Media Advertising", "WhatsApp Business", "Influencer Marketing"]
  },
  "metrics": {
    "north_star": "Monthly active users engaging with AI agents"
  }
}
```

## 🔧 Customization

### Modify Prompts

Edit the sub-prompts in `startup_strategist.py`:

```python
# Example: Modify the problem prompt
problem_prompt = ChatPromptTemplate.from_template("""
You are a ruthless product discovery expert.
Niche: {niche}; Geo: {geo}; Stage: {stage}; Founder: {founder_profile}; Constraints: {constraints}.
List top 5 concrete problems (pain × frequency × willingness to pay) as JSON:
[{{"problem":"...", "evidence":"(what makes it real)", "current_workaround":"...", "severity":1-5}}]
""")
```

### Add New Analysis Steps

```python
# Add a new chain
custom_prompt = ChatPromptTemplate.from_template("Your custom prompt here")
custom_chain = custom_prompt | gpt | to_str

# Add to parallel map
parallel_map = RunnableParallel(
    problem_map=problem_chain,
    market_scan=market_chain,
    # ... existing chains
    custom_analysis=custom_chain,  # Add your new chain
    passthrough=RunnablePassthrough()
)
```

### Change Models

```python
# Use different models
gpt = ChatOpenAI(model="gpt-4", temperature=0.3)  # More powerful but expensive
gem = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.4)  # Different Gemini model
```

## 📈 Performance Benefits

1. **Parallel Execution**: 8 analysis steps run concurrently, reducing latency
2. **Model Diversity**: OpenAI + Gemini provides different perspectives
3. **Structured Output**: Machine-consumable JSON for dashboards, task boards
4. **Error Handling**: JSON validation and retry logic
5. **Scalable**: Easy to add new analysis steps or modify prompts

## 🔍 Troubleshooting

### Common Issues

1. **JSON Parsing Errors**: The model might not output valid JSON
   - Solution: Check the raw output and adjust prompts
   - Add JSON validation and retry logic

2. **API Rate Limits**: Too many requests
   - Solution: Add delays between requests
   - Use async execution with rate limiting

3. **Model Hallucinations**: Incorrect market data or competitor info
   - Solution: Add fact-checking tools
   - Use web search integration

### Debug Mode

```python
# Enable debug output
import logging
logging.basicConfig(level=logging.DEBUG)

# Check intermediate results
raw_result = final_chain.invoke(inputs)
print("Raw result:", raw_result)
```

## 🎯 Use Cases

- **Startup Founders**: Generate comprehensive strategies for new ideas
- **Accelerators**: Evaluate startup applications systematically
- **Consultants**: Create structured analysis for clients
- **Students**: Learn startup strategy through hands-on examples
- **Investors**: Due diligence and market analysis

## 📋 Project Structure

```
langchain-based-startup-strategist/
├── startup_strategist.py          # Main implementation with LangChain pipeline
├── strategist_master_prompt.txt   # Master guidance prompt for synthesis
├── run_strategy.py                # Example script to run the strategist
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── .env                           # API keys (create this)
├── .gitignore                     # Git ignore file
└── my_startup_strategy.json       # Generated strategy output
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://github.com/langchain-ai/langchain)
- Powered by [OpenAI](https://openai.com/) and [Google Gemini](https://ai.google.dev/)
- Inspired by startup strategy frameworks and methodologies

---

**Built with ❤️ using LangChain, OpenAI, and Google Gemini**

*Repository: [https://github.com/moawizbinyamin/langchain-based-startup-strategist.git](https://github.com/moawizbinyamin/langchain-based-startup-strategist.git)*
