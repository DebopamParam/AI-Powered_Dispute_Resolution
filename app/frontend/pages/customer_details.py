# app/frontend/pages/customer_details.py
import streamlit as st
from utils.api_client import DisputeAPIClient
from components.dispute_card import dispute_card


def display_customer_details():
    """Display details for a specific customer"""

    # Get all customer details
    all_customers = DisputeAPIClient.get_customers()

    # Get customer ID from query params
    customer_id = st.query_params.get("id")
    if customer := DisputeAPIClient.get_customer(customer_id):
        st.title(f"Customer Profile: {customer.get('name', 'Unknown')}")

    # Load customer data
    customer = DisputeAPIClient.get_customer(customer_id)
    if not customer:
        st.error("Customer not found")
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
        st.title(f"Customer Profile: {customer.get('name', 'Unknown')}")
    with col3:
        st.write("")

    # Customer Information
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("### Profile Information")
            st.markdown(f"**Name:** {customer.get('name', 'Unknown')}")
            st.markdown(f"**Email:** {customer.get('email', 'Unknown')}")
            st.markdown(f"**Account Type:** {customer.get('account_type', 'Unknown')}")
            st.markdown(f"**Member Since:** {customer.get('created_at', 'Unknown')}")

    with col2:
        with st.container(border=True):
            st.markdown("### Disputes Summary")
            st.markdown(f"**Total Disputes:** {customer.get('dispute_count', 0)}")

            # Create button to file new dispute for this customer
            st.button(
                "➕ File New Dispute for This Customer",
                key="new_dispute_for_customer",
                on_click=lambda: st.query_params.update(
                    {"page": "new_dispute", "customer_id": customer_id}
                ),
                type="primary",
            )

    # Load customer disputes
    st.markdown("### Customer Disputes")
    disputes = DisputeAPIClient.get_customer_disputes(customer_id)

    if disputes:
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
                        st.button(
                            "View Details",
                            key=f"view_{dispute['id']}",
                            on_click=lambda id=dispute["id"]: st.query_params.update(
                                {"page": "dispute_details", "id": id}
                            ),
                            use_container_width=True,
                        )
    else:
        st.info("This customer has no disputes on record.")

    # Customer Management Tab
    with st.expander("Customer Management", expanded=False):
        st.markdown("### Update Customer Information")
        with st.form("update_customer_form"):
            updated_name = st.text_input("Name", value=customer.get("name", ""))
            updated_email = st.text_input("Email", value=customer.get("email", ""))
            updated_account_type = st.selectbox(
                "Account Type",
                options=["Individual", "Business", "Premium", "VIP"],
                index=["Individual", "Business", "Premium", "VIP"].index(
                    customer.get("account_type", "Individual")
                ),
            )

            if st.form_submit_button("Update Customer"):
                update_data = {
                    "name": updated_name,
                    "email": updated_email,
                    "account_type": updated_account_type,
                }

                if DisputeAPIClient.update_customer(customer_id, update_data):
                    st.session_state.notifications.append(
                        {"type": "success", "message": "Customer updated successfully!"}
                    )
                    st.rerun()
                else:
                    st.error("Failed to update customer information")

        # Dangerous Zone
        st.markdown("### Dangerous Zone")
        st.warning("These actions are permanent and cannot be undone!")

        col1, col2 = st.columns(2)
        with col1:
            with st.form("delete_customer_form"):
                st.markdown("**Delete Customer Account**")
                st.markdown(
                    "This will remove all customer information and associated disputes"
                )
                confirm_delete = st.checkbox("I understand this cannot be undone")

                if st.form_submit_button(
                    "🚨 Delete Customer", use_container_width=True
                ):
                    if confirm_delete:
                        if DisputeAPIClient.delete_customer(customer_id):
                            st.session_state.notifications.append(
                                {
                                    "type": "success",
                                    "message": "Customer deleted successfully!",
                                }
                            )
                            st.query_params.update({"page": "dashboard"})
                            st.rerun()
                        else:
                            st.error("Failed to delete customer")
                    else:
                        st.error("Please confirm deletion")

        with col2:
            with st.form("merge_customer_form"):
                st.markdown("**Merge Customer Accounts**")
                target_customer = st.selectbox(
                    "Select target customer",
                    options=[
                        c["id"]
                        for c in DisputeAPIClient.get_customers()
                        if c["id"] != customer_id
                    ],
                )
                confirm_merge = st.checkbox("Confirm account merge")

                if st.form_submit_button("🔀 Merge Accounts", use_container_width=True):
                    if confirm_merge:
                        st.info("Account merging functionality coming soon!")
                    else:
                        st.error("Please confirm merge")



def display_customer_details_page():
    """Display details for a specific customer and a list of all customers"""

    # Get all customer details
    all_customers = DisputeAPIClient.get_customers()
    
    # Initialize session state to store selected customer if not already set
    if 'selected_customer_id' not in st.session_state:
        st.session_state.selected_customer_id = None
    
    # Header Section with return button
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.button(
            "← Back", on_click=lambda: st.query_params.update({"page": "dashboard"})
        )
    with col2:
        st.title("Customer Details")
    with col3:
        st.write("")
        
    # Display all customers section
    with st.container(border=True):
        st.markdown("### Customer List")
        
        # Create a searchable filter
        search_term = st.text_input("Search customers by name or email", "")
        
        # Filter customers based on search term if provided
        filtered_customers = all_customers
        if search_term:
            filtered_customers = [
                c for c in all_customers 
                if search_term.lower() in c.get('name', '').lower() 
                or search_term.lower() in c.get('email', '').lower()
            ]
        
        # Display customers in a table
        if filtered_customers:
            customer_data = {
                "ID": [c.get('id') for c in filtered_customers],
                "Name": [c.get('name', 'Unknown') for c in filtered_customers],
                "Email": [c.get('email', 'Unknown') for c in filtered_customers],
                "Account Type": [c.get('account_type', 'Unknown') for c in filtered_customers],
                "Disputes": [c.get('dispute_count', 0) for c in filtered_customers]
            }
            
            customer_df = st.dataframe(
                customer_data,
                use_container_width=True,
                column_config={
                    "ID": st.column_config.TextColumn(
                        "ID",
                        width="small",
                    ),
                    "Disputes": st.column_config.NumberColumn(
                        "Disputes",
                        format="%d",
                        width="small",
                    ),
                },
                hide_index=True,
            )
            
            # Add dropdown to select customer
            selected_idx = 0
            if st.session_state.selected_customer_id:
                selected_idx = next(
                    (i for i, c in enumerate(filtered_customers) if c.get('id') == st.session_state.selected_customer_id), 
                    0
                )
            
            selected_customer_id = st.selectbox(
                "Select a customer to view details",
                options=[c.get('id') for c in filtered_customers],
                format_func=lambda x: next((c.get('name', 'Unknown') for c in filtered_customers if c.get('id') == x), 'Unknown'),
                index=selected_idx
            )
            
            # Button to select the customer
            if st.button(
                "View Selected Customer",
                type="primary",
                use_container_width=True
            ):
                st.session_state.selected_customer_id = selected_customer_id
                st.rerun()
        else:
            st.info("No customers found matching your search criteria.")

    # If customer is selected, show detailed view
    if st.session_state.selected_customer_id:
        customer = DisputeAPIClient.get_customer(st.session_state.selected_customer_id)
        if not customer:
            st.error("Customer not found")
            st.session_state.selected_customer_id = None  # Reset selection if customer not found
            st.rerun()
        else:
            # Display detailed customer information
            st.markdown(f"## Customer Profile: {customer.get('name', 'Unknown')}")
            
            # Customer Information
            col1, col2 = st.columns(2)
            with col1:
                with st.container(border=True):
                    st.markdown("### Profile Information")
                    st.markdown(f"**Name:** {customer.get('name', 'Unknown')}")
                    st.markdown(f"**Email:** {customer.get('email', 'Unknown')}")
                    st.markdown(f"**Account Type:** {customer.get('account_type', 'Unknown')}")
                    st.markdown(f"**Member Since:** {customer.get('created_at', 'Unknown')}")

            with col2:
                with st.container(border=True):
                    st.markdown("### Disputes Summary")
                    st.markdown(f"**Total Disputes:** {customer.get('dispute_count', 0)}")

                    # Create button to file new dispute for this customer
                    st.button(
                        "➕ File New Dispute for This Customer",
                        key="new_dispute_for_customer",
                        on_click=lambda: st.query_params.update(
                            {"page": "new_dispute", "customer_id": st.session_state.selected_customer_id}
                        ),
                        type="primary",
                    )

            # Load customer disputes
            st.markdown("### Customer Disputes")
            disputes = DisputeAPIClient.get_customer_disputes(st.session_state.selected_customer_id)

            if disputes:
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
                                st.button(
                                    "View Details",
                                    key=f"view_{dispute['id']}",
                                    on_click=lambda id=dispute["id"]: st.query_params.update(
                                        {"page": "dispute_details", "id": id}
                                    ),
                                    use_container_width=True,
                                )
            else:
                st.info("This customer has no disputes on record.")

            # Customer Management Tab
            with st.expander("Customer Management", expanded=False):
                st.markdown("### Update Customer Information")
                with st.form("update_customer_form"):
                    updated_name = st.text_input("Name", value=customer.get("name", ""))
                    updated_email = st.text_input("Email", value=customer.get("email", ""))
                    updated_account_type = st.selectbox(
                        "Account Type",
                        options=["Individual", "Business", "Premium", "VIP"],
                        index=["Individual", "Business", "Premium", "VIP"].index(
                            customer.get("account_type", "Individual")
                        ),
                    )

                    if st.form_submit_button("Update Customer"):
                        update_data = {
                            "name": updated_name,
                            "email": updated_email,
                            "account_type": updated_account_type,
                        }

                        if DisputeAPIClient.update_customer(st.session_state.selected_customer_id, update_data):
                            st.session_state.notifications.append(
                                {"type": "success", "message": "Customer updated successfully!"}
                            )
                            st.rerun()
                        else:
                            st.error("Failed to update customer information")

                # Dangerous Zone
                st.markdown("### Dangerous Zone")
                st.warning("These actions are permanent and cannot be undone!")

                col1, col2 = st.columns(2)
                with col1:
                    with st.form("delete_customer_form"):
                        st.markdown("**Delete Customer Account**")
                        st.markdown(
                            "This will remove all customer information and associated disputes"
                        )
                        confirm_delete = st.checkbox("I understand this cannot be undone")

                        if st.form_submit_button(
                            "🚨 Delete Customer", use_container_width=True
                        ):
                            if confirm_delete:
                                if DisputeAPIClient.delete_customer(st.session_state.selected_customer_id):
                                    st.session_state.notifications.append(
                                        {
                                            "type": "success",
                                            "message": "Customer deleted successfully!",
                                        }
                                    )
                                    st.session_state.selected_customer_id = None
                                    st.query_params.update({"page": "dashboard"})
                                    st.rerun()
                                else:
                                    st.error("Failed to delete customer")
                            else:
                                st.error("Please confirm deletion")

                with col2:
                    with st.form("merge_customer_form"):
                        st.markdown("**Merge Customer Accounts**")
                        target_customer = st.selectbox(
                            "Select target customer",
                            options=[
                                c["id"]
                                for c in DisputeAPIClient.get_customers()
                                if c["id"] != st.session_state.selected_customer_id
                            ],
                        )
                        confirm_merge = st.checkbox("Confirm account merge")

                        if st.form_submit_button("🔀 Merge Accounts", use_container_width=True):
                            if confirm_merge:
                                st.info("Account merging functionality coming soon!")
                            else:
                                st.error("Please confirm merge")
    else:
        # If no customer is selected, show a prompt
        st.info("Please select a customer from the list above to view their details.")


if __name__ == "__main__":
    display_customer_details_page()
    

