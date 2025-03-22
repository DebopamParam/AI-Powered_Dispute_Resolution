# app/frontend/components/followup_questions.py
import streamlit as st
from typing import List, Dict

def display_followup_questions(questions: List[str], dispute_id: str):
    """Displays interactive follow-up questions with response handling"""
    with st.container(border=True):
        st.markdown("### Follow-up Questions")
        
        if not questions:
            st.info("No follow-up questions generated for this case")
            return
            
        for i, question in enumerate(questions):
            with st.expander(f"Question #{i+1}: {question}", expanded=False):
                response = st.text_area(
                    "Agent Response",
                    key=f"response_{dispute_id}_{i}",
                    placeholder="Enter your response here...",
                    height=100
                )
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button("Save Response", key=f"save_{dispute_id}_{i}"):
                        if response.strip():
                            # Implement API call to save response
                            st.success("Response saved successfully")
                        else:
                            st.warning("Please enter a response before saving")
                with col2:
                    if st.button("Mark as Completed", key=f"complete_{dispute_id}_{i}"):
                        # Implement API call to mark question as resolved
                        st.success("Question marked as completed")