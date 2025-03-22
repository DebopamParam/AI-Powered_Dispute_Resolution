# app/frontend/components/dispute_card.py
import streamlit as st
from typing import Dict


def dispute_card(dispute: Dict):
    priority_colors = {
        1: "#4a86e8",
        2: "#5cb85c",
        3: "#f0ad4e",
        4: "#d9534f",
        5: "#d9534f",
    }

    with st.container():
        st.markdown(
            f"""
        <div style='
            border-left: 5px solid {priority_colors.get(dispute.get("priority", 1), "#999")};
            padding: 15px;
            margin: 10px 0;
            background: white;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        '>
            <div style='display: flex; justify-content: space-between;'>
                <h3 style='margin: 0;'>#{dispute['id'][:6]}</h3>
                <div style='
                    background: {priority_colors.get(dispute.get("priority", 1))};
                    color: white;
                    padding: 2px 8px;
                    border-radius: 12px;
                    font-size: 0.8em;
                '>
                    {dispute.get('priority', 'N/A')}
                </div>
            </div>
            <p style='margin: 8px 0; color: #666;'>{dispute['description'][:100]}...</p>
            <div style='display: flex; justify-content: space-between; font-size: 0.9em;'>
                <div>${dispute['amount']}</div>
                <div>{dispute['status']}</div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        # st.button(
        #     "View Details",
        #     on_click=lambda id=dispute["id"]: st.query_params.update(
        #         {"page": "dispute_details", "id": id}
        #     ),
        # )
