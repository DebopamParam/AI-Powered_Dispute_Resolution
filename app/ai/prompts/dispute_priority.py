from typing import Dict, Any
# app/ai/prompts/dispute_priority.py
def get_priority_prompt_template(dispute_data: Dict[str, Any]) -> str:
    return f"""
    You are a banking dispute resolution expert. Analyze this dispute and assign a priority level.
    
    Customer Profile:
    - Name: {dispute_data.get('customer_name')}
    - Type: {dispute_data.get('customer_type')}
    - Previous Disputes: {dispute_data.get('previous_disputes_count')}
    - Account Age: {dispute_data.get('customer_account_age_days')} days
    
    Dispute Details:
    - Amount: ${dispute_data.get('transaction_amount')}
    - Category: {dispute_data.get('category')}
    - Description: {dispute_data.get('dispute_description')}
    - Documents Available: {'Yes' if dispute_data.get('has_supporting_documents') else 'No'}
    
    Priority Guidelines:
    1 (Very Low) - Routine inquiry, low amount, established customer
    2 (Low) - Minor discrepancy, medium amount
    3 (Medium) - Significant amount, unclear details
    4 (High) - Potential fraud indicators, large amount
    5 (Critical) - Clear fraud pattern, VIP customer, legal implications
    
    Required Output:
    - Priority level (1-5 integer)
    - Concise reason for priority assignment
    - Key risk factors identified
    """