# app/frontend/components/sidebar.py
import streamlit as st
from utils.api_client import DisputeAPIClient


def sidebar():
    with st.sidebar:
        st.title("Dispute Resolution")
        st.button(
            "🏠 Dashboard",
            on_click=lambda: st.query_params.update({"page": "dashboard"}),
        )
        st.button(
            "➕ New Dispute",
            on_click=lambda: st.query_params.update({"page": "new_dispute"}),
        )

        # Quick stats
        st.divider()
        st.markdown("### System Status")
        try:
            metrics = DisputeAPIClient.get_dashboard_metrics()
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Disputes", metrics.get("total_disputes", 0))
            with col2:
                st.metric("High Priority", metrics.get("high_priority_count", 0))

            st.metric("Pending Review", metrics.get("pending_count", 0))
        except Exception as e:
            st.error(f"Error loading metrics: {str(e)}")

        # Admin section
        st.divider()
        st.button(
            "⚙️ Admin Panel", on_click=lambda: st.query_params.update({"page": "admin"})
        )
