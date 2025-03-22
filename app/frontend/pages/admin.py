# app/frontend/pages/admin.py
import streamlit as st
from utils.api_client import DisputeAPIClient


def display_admin():
    """Administration panel for system management"""

    st.title("System Administration")

    tab1, tab2, tab3 = st.tabs(["Metrics", "Configuration", "Users"])

    with tab1:
        st.header("System Metrics")
        metrics = DisputeAPIClient.get_dashboard_metrics()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Disputes", metrics.get("total_disputes", 0))
            st.metric("Average Resolution Time", "24h")
        with col2:
            st.metric("API Health", "✅ Operational")
            st.metric("Active Users", 15)

    with tab2:
        st.header("System Configuration")
        with st.form("config_form"):
            st.number_input("Default SLA Days", value=7)
            st.number_input("High Priority Threshold", value=4)
            st.form_submit_button("Save Configuration")

    with tab3:
        st.header("User Management")
        # Placeholder table
        st.dataframe(
            {
                "User": ["admin", "analyst1", "reviewer2"],
                "Role": ["Admin", "Analyst", "Reviewer"],
                "Last Login": ["2h ago", "1d ago", "3d ago"],
            }
        )

if __name__ == "__main__":
    display_admin()
