# app/frontend/utils/api_client.py
import requests
import streamlit as st
from typing import List, Dict, Optional, Any, Union
import time
from datetime import datetime, timedelta
import random
import uuid


class DisputeAPIClient:
    BASE_URL = "http://localhost:8000/api/v1"

    @classmethod
    def _handle_response(cls, response):
        try:
            response.raise_for_status()  # This will raise an exception for 4xx and 5xx errors
            return response.json()
        except requests.exceptions.RequestException as e:
            # Use mock data for prototype instead of failing
            st.error(f"API Error: {e}")
            return None
        except ValueError:
            st.error(
                f"Invalid JSON response from API. Status Code: {response.status_code}"
            )
            return None

    @classmethod
    def get_disputes(cls, sort_by="priority") -> List[Dict]:
        params = {"priority_sort": True}  # Add other params as needed
        response = requests.get(f"{cls.BASE_URL}/disputes/", params=params)
        return cls._handle_response(response)

    @classmethod
    def get_dispute(cls, dispute_id: str) -> Optional[Dict]:
        response = requests.get(f"{cls.BASE_URL}/disputes/{dispute_id}")
        return cls._handle_response(response)

    @classmethod
    def analyze_dispute(cls, dispute_id: str) -> Optional[Dict]:
        response = requests.post(f"{cls.BASE_URL}/disputes/{dispute_id}/analyze")
        return cls._handle_response(response)

    @classmethod
    def create_dispute(cls, dispute_data: Dict) -> Optional[Dict]:
        response = requests.post(f"{cls.BASE_URL}/disputes/", json=dispute_data)
        return cls._handle_response(response)

    @classmethod
    def update_dispute(cls, dispute_id: str, update_data: Dict) -> bool:
        response = requests.put(
            f"{cls.BASE_URL}/disputes/{dispute_id}", json=update_data
        )
        return response.status_code == 200

    @classmethod
    def get_customers(cls) -> List[Dict]:
        response = requests.get(f"{cls.BASE_URL}/customers/")
        return cls._handle_response(response)

    @classmethod
    def get_customer(cls, customer_id: str) -> Optional[Dict]:
        response = requests.get(f"{cls.BASE_URL}/customers/{customer_id}")
        return cls._handle_response(response)

    @classmethod
    def create_customer(cls, customer_data: Dict) -> Optional[Dict]:
        response = requests.post(f"{cls.BASE_URL}/customers/", json=customer_data)
        return cls._handle_response(response)

    @classmethod
    def get_dashboard_metrics(cls) -> Dict:
        """Calculate metrics locally using existing endpoints"""
        try:
            disputes = cls.get_disputes() or []
            customers = cls.get_customers() or []

            high_priority = len([d for d in disputes if d.get("priority", 0) >= 4])
            pending_statuses = ["Open", "Under Review", "Info Requested"]
            pending = len([d for d in disputes if d.get("status") in pending_statuses])

            return {
                "total_disputes": len(disputes),
                "high_priority_count": high_priority,
                "pending_count": pending,
                "total_customers": len(customers),
                "avg_resolution_time": "24h",  # Mocked value
            }
        except Exception as e:
            st.error(f"Metrics calculation failed: {e}")
            return {
                "total_disputes": 0,
                "high_priority_count": 0,
                "pending_count": 0,
                "total_customers": 0,
                "avg_resolution_time": "N/A",
            }

    @classmethod
    def check_health(cls) -> bool:
        """Simple health check that verifies API connectivity"""
        try:
            response = requests.get(f"http://localhost:8000/health", timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    @classmethod
    def get_customer_disputes(cls, customer_id: str) -> List[Dict]:
        response = requests.get(f"{cls.BASE_URL}/customers/{customer_id}/disputes")
        return cls._handle_response(response)

    @classmethod
    def get_insights(cls, dispute_id: str) -> Optional[Dict]:
        response = requests.get(f"{cls.BASE_URL}/disputes/{dispute_id}/insights")
        return cls._handle_response(response)

    @classmethod
    def save_insights(cls, dispute_id: str, insights: Dict) -> bool:
        response = requests.post(
            f"{cls.BASE_URL}/disputes/{dispute_id}/insights", json=insights
        )
        return response.status_code == 200

    # update customer
    @classmethod
    def update_customer(cls, customer_id: str, update_data: Dict) -> bool:
        response = requests.put(
            f"{cls.BASE_URL}/customers/{customer_id}", json=update_data
        )
        return response.status_code == 200
    
    # Delete customer
    @classmethod
    def delete_customer(cls, customer_id: str) -> bool:
        response = requests.delete(f"{cls.BASE_URL}/customers/{customer_id}")
        return response.status_code == 204