from src.core.action_verbs import ActionVerbEngine

# Create instance of the engine
engine = ActionVerbEngine()

# Test sample text with weak verbs
text = "I did backend development and worked on APIs. I helped build a chatbot."

print("=== Action Verb Analysis ===")
result = engine.suggest(text)

print(f"Total Weak Verbs Found: {len(result['found'])}")
for weak, suggestion in zip(result["found"], result["suggestions"]):
    print(f"- '{weak}' → Suggested: '{suggestion}'")
