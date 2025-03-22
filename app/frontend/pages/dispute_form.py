# app/frontend/pages/dispute_form.py
import streamlit as st
import uuid
from datetime import datetime
from utils.api_client import DisputeAPIClient
from components.insights_panel import ai_insights_panel


def display_dispute_form():
    st.title("New Dispute Form")
    response = None
    analysis = None
    # Load customers for dropdown
    customers = []
    try:
        customers = DisputeAPIClient.get_customers()
    except Exception as e:
        st.error(f"Failed to load customers: {str(e)}")

    # Initialize variables
    customer_id = st.session_state.get("prefill_customer_id", "")
    customer_name = ""
    customer_email = ""

    col1, col2 = st.columns([3, 1])
    with col2:
        st.button(
            "Back to Dashboard",
            on_click=lambda: st.query_params.update({"page": "dashboard"}),
        )

    with st.form("dispute_form"):
        # Customer Section
        st.subheader("Customer Information")

        # Customer selection method
        customer_method = st.radio(
            "Select Customer Method",
            ["Existing Customer", "New Customer"],
            horizontal=True,
            index=0 if customer_id else 1,
        )

        if customer_method == "Existing Customer" and customers:
            customer_options = {
                f"{c['name']} ({c['email']})": c["id"] for c in customers
            }
            selected_customer = st.selectbox(
                "Select Customer",
                options=list(customer_options.keys()),
                index=(
                    next(
                        (
                            i
                            for i, c_id in enumerate(customer_options.values())
                            if c_id == customer_id
                        ),
                        0,
                    )
                    if customer_id
                    else 0
                ),
            )
            if selected_customer:
                customer_id = customer_options[selected_customer]
                # Find customer details for display
                customer = next((c for c in customers if c["id"] == customer_id), None)
                if customer:
                    st.write(f"Account Type: {customer['account_type']}")
                    st.write(f"Previous Disputes: {customer.get('dispute_count', 0)}")
        else:
            customer_name = st.text_input("Customer Name")
            customer_email = st.text_input("Customer Email")
            account_type = st.selectbox(
                "Account Type", options=["Individual", "Business", "Premium", "VIP"]
            )

        # Transaction Details
        st.subheader("Transaction Details")
        col1, col2 = st.columns(2)
        with col1:
            transaction_id = st.text_input(
                "Transaction ID - Auto Generated",
                value=f"TXN-{uuid.uuid4().hex[:10].upper()}",
                disabled=True,
            )
            amount = st.number_input(
                "Amount ($)", min_value=0.01, step=1.0, value=100.00
            )
        with col2:
            merchant_name = st.text_input("Merchant Name")
            transaction_date = st.date_input("Transaction Date")

        # Dispute Details
        st.subheader("Dispute Information")
        category = st.selectbox(
            "Category",
            [
                "Unauthorized",
                "Fraud",
                "Service Not Rendered",
                "Duplicate",
                "Product Quality",
                "Billing Error",
                "Other",
            ],
        )
        description = st.text_area(
            "Description",
            placeholder="Please provide detailed information about the dispute...",
            height=150,
        )

        # Additional Information
        with st.expander("Additional Information (Optional)"):
            attach_evidence = st.checkbox("I have evidence to attach")
            if attach_evidence:
                st.file_uploader("Upload Evidence", type=["pdf", "jpg", "png"])
            urgency = st.slider(
                "Urgency Level",
                1,
                5,
                2,
                help="Higher urgency may affect prioritization",
            )

        # Add a hidden field to store action after form submission
        view_details = st.checkbox(
            "View complete details after submission", value=True, key="view_details"
        )

        # Form Submission
        submitted = st.form_submit_button("Submit Dispute", use_container_width=True)

    if submitted:
        if customer_method == "New Customer" and (
            not customer_name or not customer_email
        ):
            st.error("Please enter customer name and email")
            return

        if not merchant_name or not description:
            st.error("Please fill in all required fields")
            return

        # If new customer, create customer first
        if customer_method == "New Customer":
            customer_data = {
                "name": customer_name,
                "email": customer_email,
                "account_type": account_type,
            }

            try:
                with st.spinner("Creating new customer..."):
                    new_customer = DisputeAPIClient.create_customer(customer_data)
                if new_customer:
                    customer_id = new_customer["id"]
                else:
                    st.error("Failed to create customer: No data returned from API")
                    return
            except Exception as e:
                st.error(f"Failed to create customer: {str(e)}")
                return

        # Now create the dispute
        dispute_data = {
            "customer_id": customer_id,
            "transaction_id": transaction_id,
            "merchant_name": merchant_name,
            "amount": float(amount),
            "description": description,
            "category": category,
        }

        with st.spinner("Creating dispute and analyzing using AI 🤖..."):
            try:
                # Create dispute
                response = DisputeAPIClient.create_dispute(dispute_data)
                if not response:
                    st.error("Failed to create dispute")
                    return

                # Generate and save analysis
                # If analysis already present, load it
                # analysis = DisputeAPIClient.get_dispute(response["id"])

                # if not analysis:
                #     analysis = DisputeAPIClient.analyze_dispute(response["id"])

                # if analysis and DisputeAPIClient.save_insights(response["id"], analysis):
                #     # Store in session state to maintain UI state
                #     st.session_state.new_dispute_analysis = {
                #         "dispute_id": response["id"],
                #         "analysis": analysis
                #     }
                #     st.success("Dispute created successfully!")
                # else:
                #     st.error("Dispute created but analysis failed")

                analysis = DisputeAPIClient.analyze_dispute(response["id"])
                st.session_state.new_dispute_analysis = {
                    "dispute_id": response["id"],
                    "analysis": analysis,
                }
                st.success("Dispute created successfully!")

            except Exception as e:
                st.error(f"Error: {str(e)}")
                return

    # After form submission, show analysis if available
    if "new_dispute_analysis" in st.session_state:
        st.divider()
        st.subheader("Initial AI Analysis Results")
        print(st.session_state.new_dispute_analysis)
        # Display the analysis panel
        ai_insights_panel(
            st.session_state.new_dispute_analysis["analysis"]["analysis"],
            priority=st.session_state.new_dispute_analysis["analysis"]["analysis"][
                "priority"
            ],
        )

        # Add action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Regenerate Analysis"):
                with st.spinner("Re-analyzing..."):
                    new_analysis = DisputeAPIClient.analyze_dispute(
                        st.session_state.new_dispute_analysis["dispute_id"],
                    )
                    if new_analysis and DisputeAPIClient.save_insights(
                        st.session_state.new_dispute_analysis["dispute_id"],
                        new_analysis,
                    ):
                        st.session_state.new_dispute_analysis["analysis"] = new_analysis
                        st.rerun()

        with col2:
            if st.button("📋 View Full Details"):
                st.query_params.update(
                    {
                        "page": "dispute_details",
                        "id": st.session_state.new_dispute_analysis["dispute_id"],
                    }
                )
                del st.session_state.new_dispute_analysis  # Cleanup
                st.rerun()

        # Add option to create another dispute
        if st.button("➕ Create Another Dispute"):
            del st.session_state.new_dispute_analysis
            st.query_params.update({"page": "new_dispute"})
            st.rerun()


if __name__ == "__main__":
    display_dispute_form()
