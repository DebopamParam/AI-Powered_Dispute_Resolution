from typing import Dict, Any

# app/ai/prompts/dispute_insights.py
def get_insights_prompt_template(dispute_data: Dict[str, Any]) -> str:
    return f"""
    As a senior dispute analyst, provide detailed insights for this case:
    
    Customer Background:
    - Member since: {dispute_data.get('customer_account_age_days')} days
    - Past disputes: {dispute_data.get('previous_disputes_count')}
    - Account type: {dispute_data.get('customer_type')}
    
    Transaction Details:
    - Date: {dispute_data.get('transaction_date')}
    - Merchant: {dispute_data.get('merchant_name')}
    - Amount: ${dispute_data.get('transaction_amount')}
    - Description: {dispute_data.get('dispute_description')}
    
    Analysis Requirements:
    1. Identify 3 key patterns or anomalies
    2. List 5 relevant follow-up questions for the customer
    3. Suggest 3 probable resolution paths
    4. Highlight 2-3 potential systemic issues
    
    Format Requirements:
    - Use bullet points for each section
    - Avoid markdown formatting
    - Keep responses concise and actionable
    """