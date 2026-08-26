import os
import json
from groq import Groq

def get_llm():
    return Groq(
        api_key=os.getenv("GROQ_API_KEY")
    )

def ask_agent_to_vote(agent_role: str, context_data: str) -> dict:
    """
    Asks the LLM to review context data (e.g. tool output) and cast a vote.
    Returns a dict with 'vote' (proceed/block/rollback/monitor) and 'reason'.
    """
    client = get_llm()
    prompt = f"""You are the {agent_role} in the DevSwarm CI/CD pipeline.
Review the following context data from your tools and decide on the next action for the pipeline.
You must vote exactly one of: [proceed, block, rollback, monitor].
Output ONLY a raw JSON object with keys 'vote' and 'reason'. Do not include markdown blocks or other text.

Context Data:
{context_data}
"""
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "You are a strict CI/CD agent. Respond only with raw JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        
        # Clean up any potential markdown formatting
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
            
        result = json.loads(content.strip())
        return {
            "vote": result.get("vote", "block").lower(),
            "reason": result.get("reason", "No reason provided")
        }
    except Exception as e:
        return {
            "vote": "block",
            "reason": f"LLM error: {str(e)}"
        }
