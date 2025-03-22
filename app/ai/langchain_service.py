# app/ai/langchain_service.py
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from typing import Dict, Any, List
import json

from app.ai.schemas.priority_schema import PrioritySchema
from app.ai.schemas.insights_schema import InsightsSchema
from app.core.ai_config import ai_settings


class DisputeAIService:
    """Service for AI-powered dispute analysis using Langchain and Gemini"""

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=ai_settings.GEMINI_MODEL,
            temperature=ai_settings.TEMPERATURE,
            max_tokens=ai_settings.MAX_TOKENS,
            timeout=None,
            max_retries=ai_settings.MAX_RETRIES,
            # google_api_key=os.environ.get("GOOGLE_API_KEY", ai_settings.GOOGLE_API_KEY),
            google_api_key="AIzaSyBeC3D_rxPbaLyQjgeqCB3PZRQL7kT4mrE",
        )

    def analyze_dispute(self, dispute_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a dispute and return AI-generated insights

        Returns:
            Dict with priority, insights, followup_questions,
            probable_solutions, and possible_reasons
        """
        # Get structured output for priority
        priority_model = self.llm.with_structured_output(PrioritySchema)
        priority_result = priority_model.invoke(
            self._build_priority_prompt(dispute_data)
        )

        print(self._build_priority_prompt(dispute_data))
        print(type(priority_result))
        print(priority_result)

        # Get structured output for insights
        insights_model = self.llm.with_structured_output(InsightsSchema)
        insights_result = insights_model.invoke(
            self._build_insights_prompt(dispute_data)
        )

        print(self._build_insights_prompt(dispute_data))
        print(type(insights_result))
        print(insights_result)

        # Combine results
        return {
            "priority": (
                priority_result.priority_level if priority_result.priority_level else 0
            ),
            "priority_reason": (
                priority_result.priority_reason
                if priority_result.priority_reason
                else ""
            ),
            "insights": insights_result.insights if insights_result.insights else "",
            "followup_questions": (
                insights_result.followup_questions
                if insights_result.followup_questions
                else ""
            ),
            "probable_solutions": (
                insights_result.probable_solutions
                if insights_result.probable_solutions
                else ""
            ),
            "possible_reasons": (
                insights_result.possible_reasons
                if insights_result.possible_reasons
                else ""
            ),
            "risk_score": (
                insights_result.risk_score if insights_result.risk_score else 0
            ),
            "risk_factors": (
                insights_result.risk_factors if insights_result.risk_factors else ""
            ),
        }

    def _build_priority_prompt(self, dispute_data: Dict[str, Any]) -> str:
        """Create prompt for priority assignment"""
        return f"""
        You are a banking dispute resolution expert. Analyze this dispute and assign a priority level.
        
        Customer profile:
        - Customer name: {dispute_data.get('customer_name')}
        - Customer type: {dispute_data.get('customer_type')}
        - Previous disputes: {dispute_data.get('previous_disputes_count')}
        - Account age (days): {dispute_data.get('customer_account_age_days')}
        
        Dispute details:
        - Transaction amount: ${dispute_data.get('transaction_amount')}
        - Description: {dispute_data.get('dispute_description')}
        - Category: {dispute_data.get('category')}
        - Has supporting documents: {dispute_data.get('has_supporting_documents')}
        
        Based on this information, assign a priority level (1-5) where:
        1 = Very Low, 2 = Low, 3 = Medium, 4 = High, 5 = Critical
        
        Provide the priority level and a brief explanation for this decision.
        """

    def _build_insights_prompt(self, dispute_data: Dict[str, Any]) -> str:
        """Create prompt for generating insights"""
        return f"""
        You are a banking dispute resolution expert. Analyze this dispute and provide insights.
        
        Customer profile:
        - Customer name: {dispute_data.get('customer_name')}
        - Customer type: {dispute_data.get('customer_type')}
        - Previous disputes: {dispute_data.get('previous_disputes_count')}
        
        Dispute details:
        - Transaction amount: ${dispute_data.get('transaction_amount')}
        - Description: {dispute_data.get('dispute_description')}
        - Category: {dispute_data.get('category')}
        - Transaction date: {dispute_data.get('transaction_date')}
        
        Provide:
        1. Key insights about this dispute
        2. Follow-up questions to ask the customer
        3. Probable solutions to resolve this dispute
        4. Possible underlying reasons for this dispute
        """
