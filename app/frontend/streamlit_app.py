# app/frontend/streamlit_app.py
import streamlit as st
from components.sidebar import sidebar
from pages.dashboard import display_dashboard
from pages.dispute_details import display_dispute_details
from pages.dispute_form import display_dispute_form
from pages.admin import display_admin
from pages.api_docs import display_api_docs
from pages.customer_details import display_customer_details


def main():
    st.set_page_config(
        page_title="Banking Dispute Resolution",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize session state
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"

    if "notifications" not in st.session_state:
        st.session_state.notifications = []

    # Display sidebar
    sidebar()

    # Handle notifications if any
    if st.session_state.notifications:
        for notification in st.session_state.notifications:
            if notification["type"] == "success":
                st.success(notification["message"])
            elif notification["type"] == "error":
                st.error(notification["message"])
            elif notification["type"] == "warning":
                st.warning(notification["message"])
            elif notification["type"] == "info":
                st.info(notification["message"])
        st.session_state.notifications = []

    # Page routing
    query_params = st.query_params
    page = query_params.get("page", "dashboard")

    if page == "dashboard":
        display_dashboard()
    elif page == "dispute_details":
        display_dispute_details()
    elif page == "new_dispute":
        display_dispute_form()
    elif page == "admin":
        display_admin()
    elif page == "api_docs":
        display_api_docs()
    elif page == "customer_details":
        display_customer_details()
    else:
        st.error("Invalid page specified")


if __name__ == "__main__":
    main()
