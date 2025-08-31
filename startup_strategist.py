# --------------------  IMPORTS  --------------------
import os
import json
import warnings
from datetime import datetime, timedelta
from typing import Dict, Any, List
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Suppress warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL 1.1.1+')

# --------------------  ENV  --------------------
load_dotenv()  # loads OPENAI_API_KEY and GEMINI_API_KEY (or GOOGLE_API_KEY)

# --------------------  MODELS  --------------------
# Model choices: gpt-4o-mini = fast/cheap synthesizer; gemini-2.5-flash = fast idea expander
gpt = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
gem = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.4)

# --------------------  PROMPTS (SUB-STEPS)  --------------------
# A) Problem/JTBD decomposition (OpenAI)
problem_prompt = ChatPromptTemplate.from_template("""
You are a ruthless product discovery expert.
Niche: {niche}; Geo: {geo}; Stage: {stage}; Founder: {founder_profile}; Constraints: {constraints}.
List top 5 concrete problems (pain × frequency × willingness to pay) as JSON:
[{{"problem":"...", "evidence":"(what makes it real)", "current_workaround":"...", "severity":1-5}}]
""")

# B) Market scan (Gemini) — comps/whitespace (no browsing; reasoning-only scan)
market_prompt = ChatPromptTemplate.from_template("""
You are a market mapper. Niche: {niche}; Geo: {geo}.
Produce JSON with keys: segments (3-5), competitors (5-8, direct/indirect/substitute), whitespace (bullets).
""")

# C) Personas (OpenAI)
personas_prompt = ChatPromptTemplate.from_template("""
Design 2-3 buyer/user personas for {niche} in {geo}.
Return JSON: [{{ "name": "...", "segment": "...", "primary_jobs":[], "top_pains":[], "must_have_outcomes":[] }}]
""")

# D) Solution shapes (Gemini)
solutions_prompt = ChatPromptTemplate.from_template("""
Propose 3 candidate solution shapes for {niche} given constraints: {constraints}.
Return JSON: [{{"name":"...", "v0_scope":["..."], "tradeoffs":["..."]}}]
""")

# E) GTM ideas (OpenAI)
gtm_prompt = ChatPromptTemplate.from_template("""
GTM for {niche} in {geo}. Constraints: {constraints}. Stage: {stage}.
Return JSON: {{"positioning":"...", "channels":["..."], "hooks":["..."], "partnerships":["..."]}}
""")

# F) Tech notes (OpenAI) — mention AI bits if relevant
tech_prompt = ChatPromptTemplate.from_template("""
Propose an MVP-first architecture for {niche} considering founder skills: {founder_profile}.
Return JSON: {{"architecture":"...", "stack_choices":["..."], "ai_components":["..."], "data_sources":["..."], "security_compliance":"...", "scaling_plan":"...", "build_vs_buy":["..."]}}
""")

# G) Ops/Legal (Gemini)
ops_prompt = ChatPromptTemplate.from_template("""
Outline ops & compliance for {niche} in {geo}. Stage: {stage}.
Return JSON: {{"team_plan":[{{"role":"...","seniority":"...","when":"now|later"}}], "processes":["..."], "legal_compliance":["..."], "tooling":["..."]}}
""")

# H) Risks (OpenAI)
risks_prompt = ChatPromptTemplate.from_template("""
List top 8 risks for {niche} with likelihood and mitigation. JSON:
[{{"risk":"...", "likelihood":"low|med|high", "mitigation":"...", "owner":"founder|eng|ops|growth"}}]
""")

# --------------------  FINAL SYNTHESIS PROMPT  --------------------
def load_synthesis_prompt():
    """Load the master guidance prompt from file"""
    try:
        with open("strategist_master_prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        # Fallback if file doesn't exist
        return """
        You are a startup strategist. Synthesize all inputs into a comprehensive strategy.
        Output valid JSON with: assumptions, one_liner, problem_statement, target_personas, market, solution, tech, gtm, ops, metrics, finance, risks_and_mitigations, execution_board.
        """

synthesis_prompt = ChatPromptTemplate.from_template(load_synthesis_prompt())

# --------------------  BUILD CHAINS  --------------------
to_str = StrOutputParser()

problem_chain   = problem_prompt   | gpt | to_str
market_chain    = market_prompt    | gem | to_str
personas_chain  = personas_prompt  | gpt | to_str
solutions_chain = solutions_prompt | gem | to_str
gtm_chain       = gtm_prompt       | gpt | to_str
tech_chain      = tech_prompt      | gpt | to_str
ops_chain       = ops_prompt       | gem | to_str
risks_chain     = risks_prompt     | gpt | to_str

# Run several steps in PARALLEL to save time.
parallel_map = RunnableParallel(
    problem_map=problem_chain,
    market_scan=market_chain,
    personas=personas_chain,
    solution_shapes=solutions_chain,
    gtm_ideas=gtm_chain,
    tech_notes=tech_chain,
    ops_notes=ops_chain,
    risks_list=risks_chain,
    passthrough=RunnablePassthrough()  # carries the original input forward
)

# Final merge: feed all partials + original knobs into the synthesizer (OpenAI)
final_chain = (
    parallel_map
    | (
        # map keys into the final prompt variables
        lambda x: {
            "niche": x["passthrough"]["niche"],
            "stage": x["passthrough"]["stage"],
            "geo": x["passthrough"]["geo"],
            "founder_profile": x["passthrough"]["founder_profile"],
            "constraints": x["passthrough"]["constraints"],
            "goals": x["passthrough"]["goals"],
            "problem_map": x["problem_map"],
            "market_scan": x["market_scan"],
            "personas": x["personas"],
            "solution_shapes": x["solution_shapes"],
            "gtm_ideas": x["gtm_ideas"],
            "tech_notes": x["tech_notes"],
            "ops_notes": x["ops_notes"],
            "risks_list": x["risks_list"],
        }
    )
    | synthesis_prompt
    | gpt
    | to_str
)

# --------------------  STARTUP STRATEGIST CLASS  --------------------
class StartupStrategist:
    def __init__(self):
        """Initialize the startup strategist with models and chains"""
        self.final_chain = final_chain
        
    def generate_strategy(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive startup strategy
        
        Args:
            inputs: Dictionary with keys:
                - niche: The business niche/idea
                - stage: idea | discovery | MVP | PMF | scale
                - geo: Geography (e.g., Pakistan, GCC, Global)
                - founder_profile: Skills, network, unfair advantages
                - constraints: Budget, timeline, compliance, hiring limits
                - goals: 12-week goals
        
        Returns:
            Dict containing the complete strategy
        """
        print("🚀 Starting Startup Strategy Generation...")
        print(f"📊 Niche: {inputs['niche']}")
        print(f"🌍 Geography: {inputs['geo']}")
        print(f"📈 Stage: {inputs['stage']}")
        
        try:
            # Execute the complete chain
            raw_result = self.final_chain.invoke(inputs)
            
            # Clean up the response - remove markdown formatting if present
            cleaned_result = raw_result.strip()
            if cleaned_result.startswith('```json'):
                cleaned_result = cleaned_result[7:]  # Remove ```json
            if cleaned_result.endswith('```'):
                cleaned_result = cleaned_result[:-3]  # Remove ```
            cleaned_result = cleaned_result.strip()
            
            # Parse JSON result
            strategy = json.loads(cleaned_result)
            
            print("✅ Strategy generated successfully!")
            return strategy
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print("Raw result:", raw_result[:500] + "..." if len(raw_result) > 500 else raw_result)
            return {"error": "Failed to parse JSON response", "raw": raw_result}
        except Exception as e:
            print(f"❌ Error generating strategy: {e}")
            return {"error": str(e)}
    
    def print_strategy(self, strategy: Dict[str, Any]):
        """Pretty print the strategy results"""
        if "error" in strategy:
            print(f"❌ Error: {strategy['error']}")
            return
            
        print("\n" + "="*80)
        print("🎯 STARTUP STRATEGY RESULTS")
        print("="*80)
        
        # One-liner
        print(f"\n💡 ONE-LINER: {strategy.get('one_liner', 'N/A')}")
        
        # Problem Statement
        print(f"\n🎯 PROBLEM: {strategy.get('problem_statement', 'N/A')}")
        
        # Target Personas
        print("\n👥 TARGET PERSONAS:")
        personas = strategy.get('target_personas', [])
        for i, persona in enumerate(personas, 1):
            print(f"   {i}. {persona.get('name', 'N/A')} ({persona.get('segment', 'N/A')})")
            print(f"      Jobs: {', '.join(persona.get('primary_jobs', []))}")
            print(f"      Pains: {', '.join(persona.get('top_pains', []))}")
        
        # Market
        market = strategy.get('market', {})
        print(f"\n📊 MARKET:")
        print(f"   Geography: {market.get('geo', 'N/A')}")
        print(f"   TAM Estimate: {market.get('top_down_TAM_estimate', 'N/A')}")
        
        # Solution
        solution = strategy.get('solution', {})
        print(f"\n🛠️  SOLUTION:")
        print(f"   V0 Scope (Weeks 1-4): {', '.join(solution.get('v0_scope', []))}")
        print(f"   V1 Scope (Weeks 5-8): {', '.join(solution.get('v1_scope', []))}")
        print(f"   V2 Scope (Weeks 9-12): {', '.join(solution.get('v2_scope', []))}")
        
        # GTM
        gtm = strategy.get('gtm', {})
        print(f"\n🚀 GTM:")
        print(f"   Positioning: {gtm.get('positioning', 'N/A')}")
        print(f"   Channels: {', '.join(gtm.get('channels', []))}")
        
        # Tech
        tech = strategy.get('tech', {})
        print(f"\n⚙️  TECH:")
        print(f"   Architecture: {tech.get('architecture', 'N/A')}")
        print(f"   Stack: {', '.join(tech.get('stack_choices', []))}")
        
        # Finance
        finance = strategy.get('finance', {})
        print(f"\n💰 FINANCE:")
        print(f"   Budget Ceiling: {finance.get('budget_ceiling', 'N/A')}")
        unit_economics = finance.get('unit_economics', {})
        print(f"   CAC: {unit_economics.get('cac', 'N/A')}")
        print(f"   LTV: {unit_economics.get('ltv', 'N/A')}")
        
        # Metrics
        metrics = strategy.get('metrics', {})
        print(f"\n📈 METRICS:")
        print(f"   North Star: {metrics.get('north_star', 'N/A')}")
        
        # Execution Board
        print(f"\n📋 EXECUTION BOARD:")
        execution_board = strategy.get('execution_board', [])
        for item in execution_board[:5]:  # Show first 5 items
            print(f"   {item.get('id', 'N/A')}: {item.get('title', 'N/A')} (Due: {item.get('due', 'N/A')})")
        
        # Assumptions
        assumptions = strategy.get('assumptions', [])
        if assumptions:
            print(f"\n⚠️  ASSUMPTIONS:")
            for assumption in assumptions:
                print(f"   • {assumption}")

# --------------------  EXAMPLE USAGE  --------------------
def run_example():
    """Run an example strategy generation"""
    
    # Check if API keys are available
    if not os.environ.get("OPENAI_API_KEY"):
        import getpass
        os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter OpenAI API key: ")
    
    if not os.environ.get("GOOGLE_API_KEY"):
        import getpass
        os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter Google API key: ")
    
    # Initialize strategist
    strategist = StartupStrategist()
    
    # Example inputs
    inputs = {
        "niche": "AI career pathway builder for Pakistani graduates",
        "stage": "idea",
        "geo": "Pakistan",
        "founder_profile": "full-stack engineer with MERN/Next.js, Firebase, LangChain; strong student communities",
        "constraints": "budget <$1k/mo, timeline 12 weeks, 2 devs, must support rupee payments",
        "goals": "ship MVP in 8 weeks; 500 WAU; 50 paid signups"
    }
    
    # Generate strategy
    strategy = strategist.generate_strategy(inputs)
    
    # Print results
    strategist.print_strategy(strategy)
    
    # Save to file
    with open("startup_strategy.json", "w", encoding="utf-8") as f:
        json.dump(strategy, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Strategy saved to startup_strategy.json")

if __name__ == "__main__":
    run_example()
