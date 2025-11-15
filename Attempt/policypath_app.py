import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
import json

# Page config
st.set_page_config(
    page_title="PolicyPath - AI Prior Authorization",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .error-box {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="main-header">🏥 PolicyPath</p>', unsafe_allow_html=True)
st.markdown("### AI-Powered Prior Authorization Platform")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    n8n_url = st.text_input(
        "n8n Webhook URL",
        value="http://localhost:5678/webhook/policypath-submit",
        help="Your n8n workflow webhook endpoint"
    )
    
    st.divider()
    
    st.header("📊 Quick Stats")
    st.metric("Today's Approvals", "12", delta="3")
    st.metric("Avg Decision Time", "2.3s", delta="-0.5s")
    st.metric("AI Accuracy", "94%", delta="2%")
    
    st.divider()
    
    st.markdown("**System Status**")
    st.success("✅ AI Engine: Online")
    st.success("✅ Policy DB: Connected")
    st.info("ℹ️ Version: 1.0.0")

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🚀 Submit PA Request", 
    "📋 Dashboard", 
    "🔍 Case Lookup",
    "👥 Human Review Queue"
])

# Tab 1: Submit PA Request
with tab1:
    st.header("Submit Prior Authorization Request")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Patient Selection")
        
        # Sample patient data
        patients = {
            "P-1002345 - John D. Doe": "P-1002345",
            "P-1003456 - Jane A. Smith": "P-1003456",
            "P-1004567 - Emily R. White": "P-1004567",
            "1001 - John Smith (Demo)": "1001"
        }
        
        selected_patient = st.selectbox(
            "Select Patient",
            options=list(patients.keys()),
            help="Choose from existing patient records"
        )
        
        patient_id = patients[selected_patient]
        
        st.info(f"**Patient ID:** {patient_id}")
        
        # Additional options
        priority = st.select_slider(
            "Request Priority",
            options=["Standard", "Urgent", "Emergency"],
            value="Standard"
        )
        
        notes = st.text_area(
            "Additional Notes (Optional)",
            placeholder="Enter any additional clinical context..."
        )
    
    with col2:
        st.subheader("Request Preview")
        st.json({
            "patient_id": patient_id,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
            "notes": notes if notes else "None"
        })
    
    st.divider()
    
    # Submit button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submit_btn = st.button(
            "🚀 Submit PA Request",
            type="primary",
            use_container_width=True
        )
    
    if submit_btn:
        with st.spinner("🔄 Processing request through AI engine..."):
            try:
                # Call n8n webhook
                payload = {
                    "patient_id": patient_id,
                    "priority": priority,
                    "notes": notes,
                    "timestamp": datetime.now().isoformat()
                }
                
                response = requests.post(
                    n8n_url,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display results
                    st.balloons()
                    
                    # Parse decision
                    decision = "APPROVED"  # You'll parse from actual response
                    confidence = 95  # Parse from response
                    
                    if decision == "APPROVED":
                        st.markdown(f"""
                        <div class="success-box">
                            <h3>✅ Request APPROVED</h3>
                            <p><strong>Confidence:</strong> {confidence}%</p>
                            <p><strong>Processing Time:</strong> 2.3 seconds</p>
                            <p><strong>Request ID:</strong> {datetime.now().strftime('%Y%m%d%H%M%S')}_{patient_id}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif decision == "DENIED":
                        st.markdown(f"""
                        <div class="error-box">
                            <h3>❌ Request DENIED</h3>
                            <p><strong>Confidence:</strong> {confidence}%</p>
                            <p><strong>Reason:</strong> Does not meet policy criteria</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="warning-box">
                            <h3>⚠️ Requires Human Review</h3>
                            <p><strong>Confidence:</strong> {confidence}%</p>
                            <p><strong>Status:</strong> Sent to review queue</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Show AI reasoning
                    with st.expander("🤖 View AI Analysis"):
                        st.json(result)
                
                else:
                    st.error(f"❌ Error: {response.status_code} - {response.text}")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Connection Error: {str(e)}")
                st.warning("Make sure n8n is running and the webhook URL is correct")

# Tab 2: Dashboard
with tab2:
    st.header("📊 Analytics Dashboard")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Requests", "127", delta="12 today")
    with col2:
        st.metric("Auto-Approved", "98", delta="77%")
    with col3:
        st.metric("In Review", "8", delta="-2")
    with col4:
        st.metric("Denied", "21", delta="16%")
    
    st.divider()
    
    # Recent requests table
    st.subheader("Recent PA Requests")
    
    # Sample data
    recent_data = pd.DataFrame({
        'Request ID': [f'20251115_{i:04d}' for i in range(1, 6)],
        'Patient': ['John Doe', 'Jane Smith', 'Emily White', 'Michael Brown', 'Sarah Johnson'],
        'Treatment': ['Pembrolizumab', 'Dabrafenib+Trametinib', 'Trastuzumab', 'Nivolumab', 'Osimertinib'],
        'Decision': ['APPROVED', 'APPROVED', 'REVIEW', 'APPROVED', 'DENIED'],
        'Confidence': [98, 95, 67, 92, 88],
        'Time (s)': [2.1, 2.5, 3.2, 2.3, 2.8],
        'Timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S') for _ in range(5)]
    })
    
    # Color code decisions
    def color_decision(val):
        color = {
            'APPROVED': 'background-color: #d4edda',
            'DENIED': 'background-color: #f8d7da',
            'REVIEW': 'background-color: #fff3cd'
        }
        return color.get(val, '')
    
    styled_df = recent_data.style.applymap(color_decision, subset=['Decision'])
    st.dataframe(styled_df, use_container_width=True)

# Tab 3: Case Lookup
with tab3:
    st.header("🔍 Look Up PA Case")
    
    search_id = st.text_input("Enter Request ID or Patient ID")
    
    if st.button("Search"):
        if search_id:
            st.info(f"Searching for: {search_id}")
            # Add actual lookup logic here
        else:
            st.warning("Please enter a search term")

# Tab 4: Human Review Queue
with tab4:
    st.header("👥 Human Review Queue")
    
    st.markdown("""
    Cases flagged for human review due to:
    - Low AI confidence (< 90%)
    - Missing policy criteria
    - Complex clinical scenarios
    """)
    
    review_data = pd.DataFrame({
        'Request ID': ['20251115_0003'],
        'Patient': ['Emily White'],
        'Treatment': ['Trastuzumab'],
        'AI Decision': ['NEEDS_REVIEW'],
        'Confidence': [67],
        'Flag Reason': ['Missing prior chemotherapy documentation'],
        'Priority': ['Standard']
    })
    
    st.dataframe(review_data, use_container_width=True)
    
    if st.button("Review This Case"):
        st.info("Opening case details...")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>PolicyPath v1.0.0 | Built for Healthcare Hackathon 2025</p>
    <p>Powered by n8n + Google Gemini AI</p>
</div>
""", unsafe_allow_html=True)
