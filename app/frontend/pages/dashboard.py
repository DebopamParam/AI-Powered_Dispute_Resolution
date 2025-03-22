# app/frontend/pages/dashboard.py
import streamlit as st
from typing import List, Dict
from utils.api_client import DisputeAPIClient
from components.dispute_card import dispute_card


def display_dashboard():
    """Main dashboard view with dispute overview and filtering"""

    st.title("Dispute Management Dashboard")

    # Metrics Row
    metrics = DisputeAPIClient.get_dashboard_metrics()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Total Disputes",
            metrics.get("total_disputes", 0),
        )
    with col2:
        st.metric(
            "High Priority",
            metrics.get("high_priority_count", 0),
        )
    with col3:
        st.metric(
            "Pending Review",
            metrics.get("pending_count", 0),
        )
    with col4:
        system_healthy = DisputeAPIClient.check_health()
        st.metric("System Status", "✅ Online" if system_healthy else "❌ Offline")

    # Store filter state in session state to persist between refreshes
    if "priority_filter" not in st.session_state:
        st.session_state.priority_filter = []
    if "status_filter" not in st.session_state:
        st.session_state.status_filter = []
    if "sort_option" not in st.session_state:
        st.session_state.sort_option = "Priority"

    # Filters with two columns for better layout
    with st.expander("Filter Disputes", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            # Priority filter with more descriptive labels
            priority_filter = st.multiselect(
                "Priority Level",
                options=[1, 2, 3, 4, 5],
                default=st.session_state.priority_filter,
                format_func=lambda x: f"P{x} - {'Critical' if x >= 4 else 'High' if x == 3 else 'Medium' if x == 2 else 'Low'}",
            )
            st.session_state.priority_filter = priority_filter

            # Status filter with common statuses
            status_filter = st.multiselect(
                "Status",
                options=[
                    "Open",
                    "Under Review",
                    "Info Requested",
                    "Resolved",
                    "Approved",
                    "Rejected",
                ],
                default=st.session_state.status_filter,
            )
            st.session_state.status_filter = status_filter

        with col2:
            # Sort options
            sort_option = st.selectbox(
                "Sort By",
                options=[
                    "Priority",
                    "Date (Newest)",
                    "Date (Oldest)",
                    "Amount (High to Low)",
                ],
                index=[
                    "Priority",
                    "Date (Newest)",
                    "Date (Oldest)",
                    "Amount (High to Low)",
                ].index(st.session_state.sort_option),
            )
            st.session_state.sort_option = sort_option

            # Add a clear filters button
            if st.button("Clear Filters"):
                st.session_state.priority_filter = []
                st.session_state.status_filter = []
                st.session_state.sort_option = "Priority"
                st.rerun()

    # Create New Dispute Button
    col1, col2 = st.columns([3, 1])
    with col2:
        st.button(
            "➕ Create New Dispute",
            on_click=lambda: st.query_params.update({"page": "new_dispute"}),
            type="primary",
            use_container_width=True,
        )

    # Load disputes with filters
    sort_mapping = {
        "Priority": "priority",
        "Date (Newest)": "date_desc",
        "Date (Oldest)": "date_asc",
        "Amount (High to Low)": "amount_desc",
    }

    # Get all disputes
    all_disputes = DisputeAPIClient.get_disputes(
        sort_by=sort_mapping.get(sort_option, "priority")
    )

    # Apply filters manually (since API filter parameters aren't working)
    if all_disputes:
        filtered_disputes = all_disputes

        # Apply priority filter if set
        if priority_filter:
            filtered_disputes = [
                d for d in filtered_disputes if d.get("priority") in priority_filter
            ]

        # Apply status filter if set
        if status_filter:
            filtered_disputes = [
                d for d in filtered_disputes if d.get("status") in status_filter
            ]

        # Apply sorting if needed
        if sort_option == "Date (Newest)":
            filtered_disputes.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        elif sort_option == "Date (Oldest)":
            filtered_disputes.sort(key=lambda x: x.get("created_at", ""))
        elif sort_option == "Amount (High to Low)":
            filtered_disputes.sort(
                key=lambda x: float(x.get("amount", 0)), reverse=True
            )
        elif sort_option == "Priority":
            filtered_disputes.sort(key=lambda x: x.get("priority", 1), reverse=True)

        disputes = filtered_disputes
    else:
        disputes = []

    # Display disputes
    if disputes:
        st.subheader(f"Disputes ({len(disputes)})")

        # Organize disputes in columns (2 per row)
        disputes_per_row = 2
        rows = [
            disputes[i : i + disputes_per_row]
            for i in range(0, len(disputes), disputes_per_row)
        ]

        for row in rows:
            cols = st.columns(disputes_per_row)
            for i, dispute in enumerate(row):
                with cols[i]:
                    with st.container(border=True):
                        dispute_card(dispute)

                        # Show analysis summary if available
                        if dispute.get("analysis"):
                            st.info(
                                f"Priority: P{dispute['analysis'].get('priority', 'N/A')} • Risk: {dispute['analysis'].get('risk_score', 'N/A')}%"
                            )

                        # Action buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            st.button(
                                "View Details",
                                key=f"view_{dispute['id']}",
                                on_click=lambda id=dispute["id"]: st.query_params.update(
                                    {"page": "dispute_details", "id": id}  # Add clear params
                                ),
                                use_container_width=True,
                            )
                        with col2:
                            if dispute.get("customer_id"):
                                st.button(
                                    "Customer Info",
                                    key=f"customer_{dispute['id']}",
                                    on_click=lambda cid=dispute["customer_id"]: st.query_params.update(
                                        {"page": "customer_details", "id": cid}
                                    ),
                                    use_container_width=True,
                                )
    else:
        st.info("No disputes found. Adjust your filters or create a new dispute.")


if __name__ == "__main__":
    display_dashboard()
