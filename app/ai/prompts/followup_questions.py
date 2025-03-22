from typing import Dict, Any
# app/ai/prompts/followup_questions.py
def get_followup_prompt_template(dispute_data: Dict[str, Any]) -> str:
    return f"""
    Generate targeted follow-up questions for this dispute:
    
    Context:
    - Customer: {dispute_data.get('customer_name')}
    - Transaction ID: {dispute_data.get('transaction_id')}
    - Dispute Type: {dispute_data.get('category')}
    
    Current Information:
    {dispute_data.get('dispute_description')}
    
    Requirements:
    - Generate 5-7 specific questions
    - Prioritize questions that help verify transaction legitimacy
    - Include questions about timeline, location, and verification methods
    - Phrase questions in neutral, non-accusatory language
    """