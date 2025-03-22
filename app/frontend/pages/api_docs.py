import streamlit as st


def display_api_docs():
    st.title("API Documentation")

    st.markdown(
        """
    ## REST API Reference
    Explore our API endpoints for integration with the Banking Dispute Resolution System.
    """
    )

    with st.expander("📚 Customer Endpoints", expanded=True):
        st.markdown(
            """
        ### 1. Create Customer
        **POST** `/customers/`
        
        **Input:**
        ```json
        {
          "name": "John Doe",
          "email": "john.doe@example.com",
          "account_type": "Individual"
        }
        ```
        
        **Response:** (Status Code: 201)
        ```json
        {
          "id": "550e8400-e29b-41d4-a716-446655440000",
          "name": "John Doe",
          "email": "john.doe@example.com",
          "account_type": "Individual",
          "dispute_count": 0,
          "created_at": "2025-03-22T14:30:45.123456"
        }
        ```

        ### 2. Get All Customers
        **GET** `/customers/`
        
        **Query Parameters:**
        - `skip`: int (default: 0)
        - `limit`: int (default: 100)
        - `account_type`: string (optional)
        
        **Response:** (Status Code: 200)
        ```json
        [
          {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "account_type": "Individual",
            "dispute_count": 2,
            "created_at": "2025-03-22T14:30:45.123456"
          },
          ...
        ]
        ```
        
        ### 3. Get Customer by ID
        **GET** `/customers/{customer_id}`
        
        **Response:** (Status Code: 200)
        ```json
        {
          "id": "550e8400-e29b-41d4-a716-446655440000",
          "name": "John Doe",
          "email": "john.doe@example.com",
          "account_type": "Individual",
          "dispute_count": 2,
          "created_at": "2025-03-22T14:30:45.123456"
        }
        ```
        
        ### 4. Get Customer's Disputes
        **GET** `/customers/{customer_id}/disputes`
        
        **Query Parameters:**
        - `skip`: int (default: 0)
        - `limit`: int (default: 100)
        
        **Response:** (Status Code: 200)
        ```json
        [
          {
            "id": "550e8400-e29b-41d4-a716-446655440010",
            "customer_id": "550e8400-e29b-41d4-a716-446655440000",
            "transaction_id": "T12345",
            "merchant_name": "Example Store",
            "amount": 99.99,
            "description": "Unauthorized charge",
            "category": "Unauthorized",
            "status": "Open",
            "priority": 3,
            "created_at": "2025-03-22T15:30:45.123456",
            "resolved_at": null
          },
          ...
        ]
        ```
        
        ### 5. Update Customer
        **PUT** `/customers/{customer_id}`
        
        **Input:**
        ```json
        {
          "name": "John Doe Updated",
          "email": "john.updated@example.com",
          "account_type": "Business"
        }
        ```
        
        **Response:** (Status Code: 200)
        ```json
        {
          "id": "550e8400-e29b-41d4-a716-446655440000",
          "name": "John Doe Updated",
          "email": "john.updated@example.com",
          "account_type": "Business",
          "dispute_count": 2,
          "created_at": "2025-03-22T14:30:45.123456"
        }
        ```
        
        ### 6. Delete Customer
        **DELETE** `/customers/{customer_id}`
        
        **Response:** (Status Code: 200)
        ```json
        {
          "message": "Customer deleted successfully"
        }
        ```
        """
        )

    with st.expander("⚖️ Dispute Endpoints", expanded=True):
        st.markdown(
            """
        ### 1. Create Dispute
        **POST** `/disputes/`
        
        **Input:**
        ```json
        {
          "customer_id": "550e8400-e29b-41d4-a716-446655440000",
          "transaction_id": "T12345",
          "merchant_name": "Example Store",
          "amount": 99.99,
          "description": "Unauthorized charge",
          "category": "Unauthorized"
        }
        ```
        
        **Response:** (Status Code: 201)
        ```json
        {
          "id": "550e8400-e29b-41d4-a716-446655440010",
          "customer_id": "550e8400-e29b-41d4-a716-446655440000",
          "transaction_id": "T12345",
          "merchant_name": "Example Store",
          "amount": 99.99,
          "description": "Unauthorized charge",
          "category": "Unauthorized",
          "status": "Open",
          "priority": null,
          "created_at": "2025-03-22T15:30:45.123456",
          "resolved_at": null
        }
        ```
        
        ### 2. Get All Disputes
        **GET** `/disputes/`
        
        **Query Parameters:**
        - `skip`: int (default: 0)
        - `limit`: int (default: 100)
        - `status`: string (optional)
        - `priority_sort`: bool (default: true)
        
        **Response:** (Status Code: 200)
        ```json
        [
          {
            "id": "550e8400-e29b-41d4-a716-446655440010",
            "customer_id": "550e8400-e29b-41d4-a716-446655440000",
            "transaction_id": "T12345",
            "merchant_name": "Example Store",
            "amount": 99.99,
            "description": "Unauthorized charge",
            "category": "Unauthorized",
            "status": "Open",
            "priority": 3,
            "created_at": "2025-03-22T15:30:45.123456",
            "resolved_at": null
          },
          ...
        ]
        ```
        
        ### 3. Get Dispute by ID
        **GET** `/disputes/{dispute_id}`
        
        **Response:** (Status Code: 200)
        ```json
        {
          "id": "550e8400-e29b-41d4-a716-446655440010",
          "customer_id": "550e8400-e29b-41d4-a716-446655440000",
          "transaction_id": "T12345",
          "merchant_name": "Example Store",
          "amount": 99.99,
          "description": "Unauthorized charge",
          "category": "Unauthorized",
          "status": "Open",
          "priority": 3,
          "created_at": "2025-03-22T15:30:45.123456",
          "resolved_at": null,
          "customer": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "account_type": "Individual",
            "dispute_count": 2,
            "created_at": "2025-03-22T14:30:45.123456"
          }
        }
        ```
        
        ### 4. Update Dispute
        **PUT** `/disputes/{dispute_id}`
        
        **Input:**
        ```json
        {
          "status": "Under Review",
          "priority": 4,
          "description": "Updated description of the dispute"
        }
        ```
        
        **Response:** (Status Code: 200)
        ```json
        {
          "id": "550e8400-e29b-41d4-a716-446655440010",
          "customer_id": "550e8400-e29b-41d4-a716-446655440000",
          "transaction_id": "T12345",
          "merchant_name": "Example Store",
          "amount": 99.99,
          "description": "Updated description of the dispute",
          "category": "Unauthorized",
          "status": "Under Review",
          "priority": 4,
          "created_at": "2025-03-22T15:30:45.123456",
          "resolved_at": null
        }
        ```
        
        ### 5. Delete Dispute
        **DELETE** `/disputes/{dispute_id}`
        
        **Response:** (Status Code: 200)
        ```json
        {
          "message": "Dispute deleted successfully"
        }
        ```
        
        ### 6. Analyze Dispute
        **POST** `/disputes/{dispute_id}/analyze`
        
        **Response:** (Status Code: 201)
        ```json
        {
          "dispute_id": "550e8400-e29b-41d4-a716-446655440010",
          "analysis": {
            "priority": 4,
            "priority_reason": "High value transaction with a new merchant",
            "insights": "This appears to be a legitimate dispute based on transaction history.",
            "followup_questions": ["When did you first notice the charge?", "Have you contacted the merchant?"],
            "probable_solutions": ["Issue chargeback to merchant", "Request more information from customer"],
            "possible_reasons": ["Fraudulent merchant", "Unauthorized use of card"],
            "risk_score": 7.5,
            "risk_factors": ["High transaction amount", "First transaction with merchant"]
          }
        }
        ```
        """
        )

    with st.expander("🔍 Dispute Insights Endpoints", expanded=True):
        st.markdown(
            """
        ### 1. Create Dispute Insights
        **POST** `/disputes/{dispute_id}/insights`
        
        **Input:**
        ```json
        {
          "insights": "Detailed analysis of the dispute situation",
          "followup_questions": ["Question 1?", "Question 2?"],
          "probable_solutions": ["Solution 1", "Solution 2"],
          "possible_reasons": ["Reason 1", "Reason 2"],
          "risk_score": 6.5,
          "risk_factors": ["Factor 1", "Factor 2"],
          "priority_level": 4,
          "priority_reason": "Explanation for the priority level"
        }
        ```
        
        **Response:** (Status Code: 201)
        ```json
        {
          "id": "550e8400-e29b-41d4-a716-446655440020",
          "dispute_id": "550e8400-e29b-41d4-a716-446655440010",
          "insights": "Detailed analysis of the dispute situation",
          "followup_questions": ["Question 1?", "Question 2?"],
          "probable_solutions": ["Solution 1", "Solution 2"],
          "possible_reasons": ["Reason 1", "Reason 2"],
          "risk_score": 6.5,
          "risk_factors": ["Factor 1", "Factor 2"],
          "priority_level": 4,
          "priority_reason": "Explanation for the priority level",
          "created_at": "2025-03-22T16:30:45.123456",
          "updated_at": null
        }
        ```
        
        ### 2. Get Dispute Insights
        **GET** `/disputes/{dispute_id}/insights`
        
        **Response:** (Status Code: 200)
        ```json
        {
          "id": "550e8400-e29b-41d4-a716-446655440020",
          "dispute_id": "550e8400-e29b-41d4-a716-446655440010",
          "insights": "Detailed analysis of the dispute situation",
          "followup_questions": ["Question 1?", "Question 2?"],
          "probable_solutions": ["Solution 1", "Solution 2"],
          "possible_reasons": ["Reason 1", "Reason 2"],
          "risk_score": 6.5,
          "risk_factors": ["Factor 1", "Factor 2"],
          "priority_level": 4,
          "priority_reason": "Explanation for the priority level",
          "created_at": "2025-03-22T16:30:45.123456",
          "updated_at": null
        }
        ```
        
        ### 3. Update Dispute Insights
        **PUT** `/disputes/{dispute_id}/insights`
        
        **Input:**
        ```json
        {
          "insights": "Updated analysis of the dispute situation",
          "followup_questions": ["Updated question 1?", "Updated question 2?"],
          "probable_solutions": ["Updated solution 1", "Updated solution 2"],
          "possible_reasons": ["Updated reason 1", "Updated reason 2"],
          "risk_score": 8.0,
          "risk_factors": ["Updated factor 1", "Updated factor 2"],
          "priority_level": 5,
          "priority_reason": "Updated explanation for the priority level"
        }
        ```
        
        **Response:** (Status Code: 200)
        ```json
        {
          "id": "550e8400-e29b-41d4-a716-446655440020",
          "dispute_id": "550e8400-e29b-41d4-a716-446655440010",
          "insights": "Updated analysis of the dispute situation",
          "followup_questions": ["Updated question 1?", "Updated question 2?"],
          "probable_solutions": ["Updated solution 1", "Updated solution 2"],
          "possible_reasons": ["Updated reason 1", "Updated reason 2"],
          "risk_score": 8.0,
          "risk_factors": ["Updated factor 1", "Updated factor 2"],
          "priority_level": 5,
          "priority_reason": "Updated explanation for the priority level",
          "created_at": "2025-03-22T16:30:45.123456",
          "updated_at": "2025-03-22T17:45:30.987654"
        }
        ```
        """
        )

    st.markdown(
        """
    ## Note
    No authentication is required for these API endpoints.
    """
    )


if __name__ == "__main__":
    display_api_docs()
