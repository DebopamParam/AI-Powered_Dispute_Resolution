# app/api/services/priority_service.py
from typing import Dict, Any
from app.ai.dispute_analyzer import DisputeAnalyzer
from app.core.ai_config import ai_settings

class PriorityService:
    def __init__(self):
        self.analyzer = DisputeAnalyzer()
        
    def calculate_priority(self, dispute_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate final priority considering both AI and rule-based factors"""
        analysis = self.analyzer.analyze_dispute(dispute_data)
        
        # Combine AI priority with risk-based adjustment
        ai_priority = analysis["priority"]
        risk_priority = self._risk_based_priority(analysis["risk_score"])
        
        # Take the higher of the two priorities
        final_priority = max(ai_priority, risk_priority)
        
        return {
            "final_priority": final_priority,
            "ai_priority": ai_priority,
            "risk_priority": risk_priority,
            "risk_score": analysis["risk_score"],
            "priority_reason": analysis["priority_reason"],
        }
    
    def _risk_based_priority(self, risk_score: float) -> int:
        """Convert risk score to priority level"""
        if risk_score >= 80:
            return 5
        elif risk_score >= 65:
            return 4
        elif risk_score >= 50:
            return 3
        elif risk_score >= 35:
            return 2
        else:
            return 1