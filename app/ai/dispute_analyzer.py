# app/ai/dispute_analyzer.py
from typing import Dict, Any, List, Tuple
import json
from datetime import datetime, timedelta

from app.ai.langchain_service import DisputeAIService
from app.core.ai_config import ai_settings


class DisputeAnalyzer:
    """Class for analyzing banking disputes using AI and rule-based approaches"""

    def __init__(self):
        self.ai_service = DisputeAIService()

    def analyze_dispute(self, dispute_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive analysis of a dispute combining AI and rule-based approaches

        Returns:
            Dict with analysis results including priority, risk score, insights,
            recommended actions, etc.
        """
        # Get AI analysis
        ai_analysis = self.ai_service.analyze_dispute(dispute_data)

        # Add rule-based risk scoring
        risk_score, risk_factors = self._calculate_risk_score(dispute_data)

        # Add recommended next actions
        recommended_actions = self._generate_recommended_actions(
            dispute_data, ai_analysis, risk_score
        )

        # Combine all analysis
        return {
            **ai_analysis,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "recommended_actions": recommended_actions,
            "sla_target": self._calculate_sla_target(
                dispute_data, ai_analysis["priority"]
            ),
            "similar_cases_count": 0,  # Placeholder for future implementation
        }

    def _calculate_risk_score(
        self, dispute_data: Dict[str, Any]
    ) -> Tuple[float, List[str]]:
        """Calculate a risk score (0-100) based on dispute characteristics"""
        risk_factors = []
        score = 50

        # Transaction amount risk
        amount = dispute_data.get("transaction_amount", 0)
        if amount > 10000:
            score += 25
            risk_factors.append("High transaction amount (>$10k)")
        elif amount > 5000:
            score += 15
            risk_factors.append("Medium-high transaction amount (>$5k)")
        elif amount > 1000:
            score += 5
            risk_factors.append("Moderate transaction amount (>$1k)")

        # Customer history risk
        previous_disputes = dispute_data.get("previous_disputes_count", 0)
        if previous_disputes > 5:
            score += 20
            risk_factors.append("Frequent disputer (>5 disputes)")
        elif previous_disputes > 2:
            score += 10
            risk_factors.append("Multiple previous disputes (>2)")

        # Account age risk
        account_age = dispute_data.get("customer_account_age_days", 0)
        if account_age < 30:
            score += 15
            risk_factors.append("New account (<30 days)")
        elif account_age < 365:
            score += 5
            risk_factors.append("Relatively new account (<1 year)")

        # Category risk
        category = dispute_data.get("category", "").lower()
        if "fraud" in category:
            score += 30
            risk_factors.append("Fraud-related category")
        elif "unauthorized" in category:
            score += 20
            risk_factors.append("Unauthorized transaction")

        # Document status
        if not dispute_data.get("has_supporting_documents"):
            score += 10
            risk_factors.append("Missing supporting documents")

        # Cap score between 0-100
        score = max(0, min(100, score))

        return round(score, 2), risk_factors

    def _generate_recommended_actions(
        self,
        dispute_data: Dict[str, Any],
        ai_analysis: Dict[str, Any],
        risk_score: float,
    ) -> List[str]:
        """Generate recommended actions based on analysis results"""
        actions = []

        # High priority actions
        if ai_analysis["priority"] >= 4:
            actions.extend(
                [
                    "Escalate to senior analyst",
                    "Request urgent documentation",
                    "Initiate fraud investigation",
                ]
            )

        # Medium priority actions
        elif ai_analysis["priority"] >= 3:
            actions.extend(
                [
                    "Schedule customer interview",
                    "Verify transaction details with merchant",
                    "Review account history",
                ]
            )

        # General actions based on risk
        if risk_score > 70:
            actions.append("Flag account for enhanced monitoring")
        if risk_score > 80:
            actions.append("Notify compliance department")

        # Add AI recommendations
        actions.extend(ai_analysis.get("probable_solutions", []))

        return list(set(actions))[:5]  # Return top 5 unique actions

    def _calculate_sla_target(
        self, dispute_data: Dict[str, Any], priority: int
    ) -> datetime:
        """Calculate SLA target date based on priority"""
        base_date = datetime.utcnow()

        sla_days = {1: 14, 2: 10, 3: 7, 4: 3, 5: 1}

        return base_date + timedelta(days=sla_days.get(priority, 14))
