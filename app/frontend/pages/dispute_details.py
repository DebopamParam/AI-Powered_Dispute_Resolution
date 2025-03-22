# app/frontend/pages/dispute_details.py
import streamlit as st
from datetime import datetime
from utils.api_client import DisputeAPIClient
from components.insights_panel import ai_insights_panel
from components.followup_questions import display_followup_questions


def display_dispute_details():
    """Detailed view of a single dispute"""

    # Get all disputes
    all_disputes = DisputeAPIClient.get_disputes()

    # Get dispute ID from query params
    dispute_id = st.query_params.get("id")


    if not dispute_id:
        st.error("No dispute selected")
        st.button(
            "Return to Dashboard",
            on_click=lambda: st.query_params.update({"page": "dashboard"}),
        )
        return

    # Load dispute data
    dispute = DisputeAPIClient.get_dispute(dispute_id)
    if not dispute:
        st.error("Dispute not found")
        st.button(
            "Return to Dashboard",
            on_click=lambda: st.query_params.update({"page": "dashboard"}),
        )
        return

    # Header Section with return button
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.button(
            "← Back", on_click=lambda: st.query_params.update({"page": "dashboard"})
        )
    with col2:
        st.title(f"Dispute #{dispute['id'][:6]}")
    with col3:
        st.write("")

    # Status bar with styled colors
    status_colors = {
        "Open": "🔵",
        "Under Review": "🟠",
        "Info Requested": "🟡",
        "Resolved": "🟢",
        "Approved": "✅",
        "Rejected": "❌",
    }

    status = dispute.get("status", "Unknown")
    priority = dispute.get("priority", "N/A")

    # Status and Priority Indicators
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### Status: {status_colors.get(status, '⚪')} {status}")
    with col2:
        priority_color = (
            "red"
            if priority >= 4
            else "orange" if priority == 3 else "blue" if priority == 2 else "green"
        )
        st.markdown(
            f"### Priority: <span style='color:{priority_color};'>P{priority}</span>",
            unsafe_allow_html=True,
        )

    # Main Content Tabs
    tab1, tab2, tab3 = st.tabs(["Details", "AI Analysis", "Resolution"])

    with tab1:
        # Basic Info Columns
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.markdown("### Customer Information")
                if "customer" in dispute and dispute["customer"]:
                    customer = dispute["customer"]
                    st.markdown(f"**Name:** {customer.get('name', 'Unknown')}")
                    st.markdown(f"**Email:** {customer.get('email', 'Unknown')}")
                    st.markdown(
                        f"**Account Type:** {customer.get('account_type', 'Unknown')}"
                    )
                    st.markdown(
                        f"**Total Disputes:** {customer.get('dispute_count', 0)}"
                    )

                    # Customer details button
                    st.button(
                        "View Customer Profile",
                        key="view_customer",
                        on_click=lambda: st.query_params.update(
                            {"page": "customer_details", "id": customer["id"]}
                        ),
                        use_container_width=True,
                    )
                else:
                    customer_id = dispute.get("customer_id")
                    st.markdown(f"**Customer ID:** {customer_id}")
                    st.markdown("_Detailed customer information not available_")

        with col2:
            with st.container(border=True):
                st.markdown("### Transaction Information")
                st.markdown(f"**Amount:** ${dispute.get('amount', 0):.2f}")
                st.markdown(f"**Merchant:** {dispute.get('merchant_name', 'Unknown')}")
                st.markdown(
                    f"**Transaction ID:** {dispute.get('transaction_id', 'Unknown')}"
                )
                st.markdown(f"**Category:** {dispute.get('category', 'Unknown')}")
                st.markdown(f"**Created:** {dispute.get('created_at', 'Unknown')}")
                if dispute.get("resolved_at"):
                    st.markdown(f"**Resolved:** {dispute.get('resolved_at')}")

        # Description Section
        st.markdown("### Dispute Description")
        st.write(dispute.get("description", "No description provided"))

    with tab2:
        # AI Insights Section
        st.markdown("## AI Analysis")

        # Get analysis from dedicated insights endpoint
        analysis = DisputeAPIClient.get_insights(dispute_id)

        if analysis:
            ai_insights_panel(analysis, dispute.get("priority", 3))

            # If followup questions exist
            if analysis.get("followup_questions"):
                st.markdown("### Follow-up Interactions")
                display_followup_questions(
                    questions=analysis["followup_questions"],
                    dispute_id=dispute_id,
                )

        else:
            st.warning("No stored analysis found")
            if st.button("Generate New Analysis", type="primary"):
                with st.spinner("Analyzing..."):
                    new_analysis = DisputeAPIClient.analyze_dispute(dispute_id)
                    if new_analysis and DisputeAPIClient.save_insights(
                        dispute_id, new_analysis
                    ):
                        st.rerun()

    with tab3:
        # Resolution Actions
        st.markdown("## Resolution Actions")

        # Different action buttons based on current status
        if status in ["Open", "Under Review", "Info Requested"]:
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(
                    "✅ Approve Dispute", use_container_width=True, type="primary"
                ):
                    if DisputeAPIClient.update_dispute_status(dispute_id, "Approved"):
                        st.session_state.notifications.append(
                            {
                                "type": "success",
                                "message": "Dispute approved successfully!",
                            }
                        )
                        st.rerun()
            with col2:
                if st.button("❌ Reject Dispute", use_container_width=True):
                    if DisputeAPIClient.update_dispute_status(dispute_id, "Rejected"):
                        st.session_state.notifications.append(
                            {"type": "success", "message": "Dispute rejected"}
                        )
                        st.rerun()
            with col3:
                if st.button("📩 Request More Info", use_container_width=True):
                    if DisputeAPIClient.update_dispute_status(
                        dispute_id, "Info Requested"
                    ):
                        st.session_state.notifications.append(
                            {"type": "success", "message": "Information request sent"}
                        )
                        st.rerun()
        else:
            st.info(f"This dispute is already {status}. No further actions available.")

            # Option to reopen the dispute
            if st.button("Reopen Dispute", use_container_width=True):
                if DisputeAPIClient.update_dispute_status(dispute_id, "Open"):
                    st.session_state.notifications.append(
                        {"type": "success", "message": "Dispute reopened successfully!"}
                    )
                    st.rerun()

        # Add notes section
        st.markdown("### Add Resolution Notes")
        with st.form("resolution_notes_form"):
            notes = st.text_area(
                "Notes",
                height=100,
                placeholder="Add additional resolution notes here...",
            )
            submitted = st.form_submit_button("Save Notes")
            if submitted:
                # Add logic to save notes using API
                st.success("Notes saved successfully!")

        # Dangerous Zone
        with st.expander("Advanced Options"):
            st.warning("Danger Zone: These actions cannot be undone!")
            if st.button("Delete Dispute", use_container_width=True):
                confirm = st.checkbox("I understand this action cannot be undone")
                if confirm and DisputeAPIClient.delete_dispute(dispute_id):
                    st.session_state.notifications.append(
                        {"type": "success", "message": "Dispute deleted successfully!"}
                    )
                    st.query_params.update({"page": "dashboard"})
                    st.rerun()


# import streamlit as st
# from datetime import datetime
# from utils.api_client import DisputeAPIClient
# from components.insights_panel import ai_insights_panel
# from components.followup_questions import display_followup_questions


def display_dispute_details_page():
    """Detailed view of a single dispute"""

    # Get all disputes
    all_disputes = DisputeAPIClient.get_disputes()

    # Initialize session state to store selected dispute if not already set
    if "selected_dispute_id" not in st.session_state:
        st.session_state.selected_dispute_id = None

    # Header Section with return button
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.button(
            "← Back", on_click=lambda: st.query_params.update({"page": "dashboard"})
        )
    with col2:
        st.title("Dispute Details")
    with col3:
        st.write("")

    # Display all disputes section for selection
    with st.container(border=True):
        st.markdown("### Dispute List")

        # Create a searchable filter
        search_term = st.text_input(
            "Search disputes by ID, customer_id, or merchant", ""
        )

        # Filter disputes based on search term if provided
        filtered_disputes = all_disputes
        if search_term:
            filtered_disputes = [
                d
                for d in all_disputes
                if (
                    search_term.lower() in str(d.get("id", "")).lower()
                    or search_term.lower() in get_customer_name(d).lower()
                    or search_term.lower() in str(d.get("merchant_name", "")).lower()
                )
            ]

        # Display disputes in a table
        if filtered_disputes:
            dispute_data = {
                "ID": [d.get("id", "")[:6] for d in filtered_disputes],
                "Customer": [get_customer_name(d) for d in filtered_disputes],
                "Amount": [f"${d.get('amount', 0):.2f}" for d in filtered_disputes],
                "Merchant": [
                    d.get("merchant_name", "Unknown") for d in filtered_disputes
                ],
                "Status": [d.get("status", "Unknown") for d in filtered_disputes],
                "Priority": [f"P{d.get('priority', 'N/A')}" for d in filtered_disputes],
            }

            dispute_df = st.dataframe(
                dispute_data,
                use_container_width=True,
                hide_index=True,
            )

            # Add dropdown to select dispute
            selected_idx = 0
            if st.session_state.selected_dispute_id:
                selected_idx = next(
                    (
                        i
                        for i, d in enumerate(filtered_disputes)
                        if d.get("id") == st.session_state.selected_dispute_id
                    ),
                    0,
                )

            selected_dispute_id = st.selectbox(
                "Select a dispute to view details",
                options=[d.get("id") for d in filtered_disputes],
                format_func=lambda x: f"#{x[:6]} - {next((d.get('merchant_name', 'Unknown') for d in filtered_disputes if d.get('id') == x), 'Unknown')}",
                index=selected_idx,
            )

            # Button to select the dispute
            if st.button(
                "View Selected Dispute", type="primary", use_container_width=True
            ):
                st.session_state.selected_dispute_id = selected_dispute_id
                st.rerun()
        else:
            st.info("No disputes found matching your search criteria.")

    # If no dispute is selected, show a prompt
    if not st.session_state.selected_dispute_id:
        st.info("Please select a dispute from the list above to view its details.")
        return

    # Load dispute data
    dispute = DisputeAPIClient.get_dispute(st.session_state.selected_dispute_id)
    if not dispute:
        st.error("Dispute not found")
        st.session_state.selected_dispute_id = (
            None  # Reset selection if dispute not found
        )
        st.rerun()
        return

    # Show the selected dispute title
    st.markdown(f"## Dispute #{dispute['id'][:6]}")

    # Status bar with styled colors
    status_colors = {
        "Open": "🔵",
        "Under Review": "🟠",
        "Info Requested": "🟡",
        "Resolved": "🟢",
        "Approved": "✅",
        "Rejected": "❌",
    }

    status = dispute.get("status", "Unknown")
    priority = dispute.get("priority", "N/A")

    # Status and Priority Indicators
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### Status: {status_colors.get(status, '⚪')} {status}")
    with col2:
        priority_color = (
            "red"
            if priority >= 4
            else "orange" if priority == 3 else "blue" if priority == 2 else "green"
        )
        st.markdown(
            f"### Priority: <span style='color:{priority_color};'>P{priority}</span>",
            unsafe_allow_html=True,
        )

    # Main Content Tabs
    tab1, tab2, tab3 = st.tabs(["Details", "AI Analysis", "Resolution"])

    with tab1:
        # Basic Info Columns
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.markdown("### Customer Information")
                customer_info = dispute.get("customer_id")
                
                # Check if customer_id is a dictionary or a string/other type
                if isinstance(customer_info, dict):
                    st.markdown(f"**Name:** {customer_info.get('name', 'Unknown')}")
                    st.markdown(f"**Email:** {customer_info.get('email', 'Unknown')}")
                    st.markdown(
                        f"**Account Type:** {customer_info.get('account_type', 'Unknown')}"
                    )
                    st.markdown(
                        f"**Total Disputes:** {customer_info.get('dispute_count', 0)}"
                    )

                    # Customer details button
                    if st.button(
                        "View Customer Profile",
                        key="view_customer",
                        use_container_width=True,
                    ):
                        # Update session state instead of query params
                        st.session_state.page = "customer_details"
                        st.session_state.selected_customer_id = customer_info["id"]
                        st.query_params.update({"page": "customer_details"})
                        st.rerun()
                else:
                    st.markdown(f"**Customer ID:** {customer_info}")
                    st.markdown("_Detailed customer information not available_")

        with col2:
            with st.container(border=True):
                st.markdown("### Transaction Information")
                st.markdown(f"**Amount:** ${dispute.get('amount', 0):.2f}")
                st.markdown(f"**Merchant:** {dispute.get('merchant_name', 'Unknown')}")
                st.markdown(
                    f"**Transaction ID:** {dispute.get('transaction_id', 'Unknown')}"
                )
                st.markdown(f"**Category:** {dispute.get('category', 'Unknown')}")
                st.markdown(f"**Created:** {dispute.get('created_at', 'Unknown')}")
                if dispute.get("resolved_at"):
                    st.markdown(f"**Resolved:** {dispute.get('resolved_at')}")

        # Description Section
        st.markdown("### Dispute Description")
        st.write(dispute.get("description", "No description provided"))

    with tab2:
        # AI Insights Section
        st.markdown("## AI Analysis")

        # Get analysis from dedicated insights endpoint
        analysis = DisputeAPIClient.get_insights(st.session_state.selected_dispute_id)

        if analysis:
            ai_insights_panel(analysis, dispute.get("priority", 3))

            # If followup questions exist
            if analysis.get("followup_questions"):
                st.markdown("### Follow-up Interactions")
                display_followup_questions(
                    questions=analysis["followup_questions"],
                    dispute_id=st.session_state.selected_dispute_id,
                )

        else:
            st.warning("No stored analysis found")
            if st.button("Generate New Analysis", type="primary"):
                with st.spinner("Analyzing..."):
                    new_analysis = DisputeAPIClient.analyze_dispute(
                        st.session_state.selected_dispute_id
                    )
                    if new_analysis and DisputeAPIClient.save_insights(
                        st.session_state.selected_dispute_id, new_analysis
                    ):
                        st.rerun()

    with tab3:
        # Resolution Actions
        st.markdown("## Resolution Actions")

        # Different action buttons based on current status
        if status in ["Open", "Under Review", "Info Requested"]:
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(
                    "✅ Approve Dispute", use_container_width=True, type="primary"
                ):
                    if DisputeAPIClient.update_dispute_status(
                        st.session_state.selected_dispute_id, "Approved"
                    ):
                        st.session_state.notifications.append(
                            {
                                "type": "success",
                                "message": "Dispute approved successfully!",
                            }
                        )
                        st.rerun()
            with col2:
                if st.button("❌ Reject Dispute", use_container_width=True):
                    if DisputeAPIClient.update_dispute_status(
                        st.session_state.selected_dispute_id, "Rejected"
                    ):
                        st.session_state.notifications.append(
                            {"type": "success", "message": "Dispute rejected"}
                        )
                        st.rerun()
            with col3:
                if st.button("📩 Request More Info", use_container_width=True):
                    if DisputeAPIClient.update_dispute_status(
                        st.session_state.selected_dispute_id, "Info Requested"
                    ):
                        st.session_state.notifications.append(
                            {"type": "success", "message": "Information request sent"}
                        )
                        st.rerun()
        else:
            st.info(f"This dispute is already {status}. No further actions available.")

            # Option to reopen the dispute
            if st.button("Reopen Dispute", use_container_width=True):
                if DisputeAPIClient.update_dispute_status(
                    st.session_state.selected_dispute_id, "Open"
                ):
                    st.session_state.notifications.append(
                        {"type": "success", "message": "Dispute reopened successfully!"}
                    )
                    st.rerun()

        # Add notes section
        st.markdown("### Add Resolution Notes")
        with st.form("resolution_notes_form"):
            notes = st.text_area(
                "Notes",
                height=100,
                placeholder="Add additional resolution notes here...",
            )
            submitted = st.form_submit_button("Save Notes")
            if submitted:
                # Add logic to save notes using API
                st.success("Notes saved successfully!")

        # Dangerous Zone
        with st.expander("Advanced Options"):
            st.warning("Danger Zone: These actions cannot be undone!")
            if st.button("Delete Dispute", use_container_width=True):
                confirm = st.checkbox("I understand this action cannot be undone")
                if confirm and DisputeAPIClient.delete_dispute(
                    st.session_state.selected_dispute_id
                ):
                    st.session_state.notifications.append(
                        {"type": "success", "message": "Dispute deleted successfully!"}
                    )
                    st.session_state.selected_dispute_id = None
                    st.query_params.update({"page": "dashboard"})
                    st.rerun()


# Helper function to safely get customer name from dispute object
def get_customer_name(dispute):
    customer_id = dispute.get("customer_id")
    if isinstance(customer_id, dict):
        return customer_id.get("name", "Unknown")
    return "Unknown"


if __name__ == "__main__":
    display_dispute_details_page()
