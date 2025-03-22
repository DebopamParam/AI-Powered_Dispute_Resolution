import streamlit as st
from typing import Dict, Any, List


def ai_insights_panel(analysis: Dict[str, Any], priority: int):
    """Displays AI-generated insights in a structured panel."""

    with st.container():

        # Priority and Risk
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Priority Level", f"{priority}/5")
        with col2:
            st.metric("Risk Score", f"{analysis.get('risk_score', 'N/A')}/10.0")

        # Priority Reason
        if analysis.get("priority_reason"):
            with st.expander("Priority Reason", expanded=True):
                st.markdown(analysis["priority_reason"])

        # Key Insights
        if analysis.get("insights"):
            with st.expander("Key Insights", expanded=True):
                # Use markdown instead of write to ensure full text is displayed
                st.markdown("### AI Insights")
                st.markdown(analysis["insights"])

        # Follow-up Questions
        if analysis.get("followup_questions"):
            with st.expander("Follow-up Questions", expanded=False):
                if isinstance(analysis["followup_questions"], str):
                    try:
                        # Attempt to parse as a list (in case it's a string representation)
                        questions = eval(analysis["followup_questions"])
                        if isinstance(questions, list):
                            for question in questions:
                                st.markdown(f"- {question}")
                        else:
                            st.markdown(analysis["followup_questions"])  # Display as is
                    except:
                        st.markdown(
                            analysis["followup_questions"]
                        )  # Display as is if parsing fails
                elif isinstance(analysis["followup_questions"], list):
                    for question in analysis["followup_questions"]:
                        st.markdown(f"- {question}")
                else:
                    st.markdown(analysis["followup_questions"])

        # Probable Solutions
        if analysis.get("probable_solutions"):
            with st.expander("Probable Solutions", expanded=False):
                if isinstance(analysis["probable_solutions"], str):
                    try:
                        solutions = eval(analysis["probable_solutions"])
                        if isinstance(solutions, list):
                            for solution in solutions:
                                st.markdown(f"- {solution}")
                        else:
                            st.markdown(analysis["probable_solutions"])
                    except:
                        st.markdown(analysis["probable_solutions"])
                elif isinstance(analysis["probable_solutions"], list):
                    for solution in analysis[
                        "probable_solutions"
                    ]:  # Use analysis["probable_solutions"] instead of solutions
                        st.markdown(f"- {solution}")
                else:
                    st.markdown(analysis["probable_solutions"])

        # Possible Reasons
        if analysis.get("possible_reasons"):
            with st.expander("Possible Reasons", expanded=False):
                if isinstance(analysis["possible_reasons"], str):
                    try:
                        reasons = eval(analysis["possible_reasons"])
                        if isinstance(reasons, list):
                            for reason in reasons:
                                st.markdown(f"- {reason}")
                        else:
                            st.markdown(analysis["possible_reasons"])
                    except:
                        st.markdown(analysis["possible_reasons"])

                elif isinstance(analysis["possible_reasons"], list):
                    for reason in analysis["possible_reasons"]:
                        st.markdown(f"- {reason}")
                else:
                    st.markdown(analysis["possible_reasons"])

        # Risk Factors
        if analysis.get("risk_factors"):
            with st.expander("Risk Factors", expanded=False):
                if isinstance(analysis["risk_factors"], str):
                    try:
                        risk_factors = eval(analysis["risk_factors"])
                        if isinstance(risk_factors, list):
                            for risk_factor in risk_factors:
                                st.markdown(f"- {risk_factor}")
                        else:
                            st.markdown(analysis["risk_factors"])
                    except:
                        st.markdown(analysis["risk_factors"])
                elif isinstance(analysis["risk_factors"], list):
                    for risk_factor in analysis["risk_factors"]:
                        st.markdown(f"- {risk_factor}")
                else:
                    st.markdown(analysis["risk_factors"])
