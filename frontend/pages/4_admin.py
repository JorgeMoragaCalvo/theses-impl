import streamlit as st
import sys
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd

# Add the parent directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.api_client import get_api_client
"""
Admin Dashboard - User and system management (Admin only).
"""

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Get API client
api_client = get_api_client(BACKEND_URL)

st.set_page_config(page_title="Admin Dashboard", page_icon="👨‍💼", layout="wide")

st.title("👨‍💼 Admin Dashboard")

# Check if the user is authenticated
if not api_client.is_authenticated():
    st.warning("Please login from the home page first!")
    st.info("Click the link in the sidebar to go to the home page.")
    st.stop()

# Check if the user is admin
if not api_client.is_admin():
    st.error("⛔ Access Denied")
    st.warning("This page is only accessible to administrators.")
    st.info("If you need admin access, please contact your system administrator.")
    st.stop()

# Admin confirmed - show dashboard
st.success(f"👋 Welcome, Administrator **{st.session_state.get('student_name', 'Admin')}**")

# Create tabs for different admin functions
tab1, tab2, tab3 = st.tabs(["👥 User Management", "📊 System Statistics", "⚙️ Settings"])

# ============================================================================
# TAB 1: USER MANAGEMENT
# ============================================================================

with tab1:
    st.subheader("👥 User Management")

    # Fetch all users
    success, users = api_client.get("admin/users")

    if success and users:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)

        total_users = len(users)
        active_users = len([u for u in users if u.get("is_active", True)])
        admin_users = len([u for u in users if u.get("role") == "admin"])
        inactive_users = total_users - active_users

        with col1:
            st.metric("Total Users", total_users)
        with col2:
            st.metric("Active Users", active_users)
        with col3:
            st.metric("Inactive Users", inactive_users)
        with col4:
            st.metric("Administrators", admin_users)

        st.divider()

        # User list table
        st.markdown("### User List")

        # Prepare data for DataFrame
        user_data = []
        for user in users:
            last_login = user.get("last_login")
            if last_login:
                last_login = datetime.fromisoformat(last_login.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")

            created_at = user.get("created_at")
            if created_at:
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00")).strftime("%Y-%m-%d")

            user_data.append({
                "ID": user["id"],
                "Name": user["name"],
                "Email": user["email"],
                "Role": user["role"],
                "Status": "Active" if user["is_active"] else "Inactive",
                "Conversations": user.get("total_conversations", 0),
                "Assessments": user.get("total_assessments", 0),
                "Avg Score": f"{user.get('average_score', 0):.1f}" if user.get("average_score") else "N/A",
                "Created": created_at,
                "Last Login": last_login or "Never"
            })

        # Display as dataframe
        df = pd.DataFrame(user_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()

        # User management actions
        st.markdown("### Manage User")

        col1, col2 = st.columns([2, 3])

        with col1:
            # Select user
            user_select = st.selectbox(
                "Select User:",
                options=[f"{u['id']} - {u['name']} ({u['email']})" for u in users],
                key="user_select"
            )

            selected_user_id = int(user_select.split(" - ")[0])
            selected_user = next(u for u in users if u["id"] == selected_user_id)

            # Display user info
            st.markdown(f"**Name:** {selected_user['name']}")
            st.markdown(f"**Email:** {selected_user['email']}")
            st.markdown(f"**Role:** {selected_user['role']}")
            st.markdown(f"**Status:** {'Active' if selected_user['is_active'] else 'Inactive'}")

        with col2:
            st.markdown("#### Actions")

            # Activate/Deactivate user
            current_status = selected_user["is_active"]
            action_label = "Deactivate User" if current_status else "Activate User"
            action_color = "secondary" if current_status else "primary"

            if st.button(action_label, type=action_color, key="toggle_status"):
                new_status = not current_status
                success, data = api_client.put(
                    f"admin/users/{selected_user_id}/status",
                    params={"is_active": new_status}
                )

                if success:
                    st.success(f"User {'activated' if new_status else 'deactivated'} successfully!")
                    st.rerun()
                else:
                    error_msg = data.get("detail", data.get("error", "Failed to update status"))
                    st.error(f"Error: {error_msg}")

            st.divider()

            # Change user role
            st.markdown("#### Change Role")
            new_role = st.selectbox(
                "New Role:",
                options=["user", "admin"],
                index=0 if selected_user["role"] == "user" else 1,
                key="new_role"
            )

            if st.button("Update Role", type="primary", key="update_role"):
                if new_role == selected_user["role"]:
                    st.warning("User already has this role!")
                else:
                    success, data = api_client.put(
                        f"admin/users/{selected_user_id}/role",
                        params={"role": new_role}
                    )

                    if success:
                        st.success(f"User role updated to '{new_role}' successfully!")
                        st.rerun()
                    else:
                        error_msg = data.get("detail", data.get("error", "Failed to update role"))
                        st.error(f"Error: {error_msg}")

    elif success:
        st.info("No users found in the system.")
    else:
        error_msg = users.get("error", users.get("detail", "Failed to load users"))
        st.error(f"Error: {error_msg}")

# ============================================================================
# TAB 2: SYSTEM STATISTICS
# ============================================================================

with tab2:
    st.subheader("📊 System Statistics")

    # Fetch system stats
    success, stats = api_client.get("admin/stats")

    if success and stats:
        # Display key metrics
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Total Users", stats.get("total_users", 0))
        with col2:
            st.metric("Active Users", stats.get("active_users", 0))
        with col3:
            st.metric("Conversations", stats.get("total_conversations", 0))
        with col4:
            st.metric("Assessments", stats.get("total_assessments", 0))
        with col5:
            avg_score = stats.get("average_assessment_score")
            st.metric("Avg Assessment Score", f"{avg_score:.1f}" if avg_score else "N/A")

        st.divider()

        # Additional analytics placeholder
        st.markdown("### 📈 Usage Analytics")
        st.info("🚧 Detailed usage analytics and charts coming soon!")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### User Engagement")
            st.markdown("- Daily active users")
            st.markdown("- Average session duration")
            st.markdown("- Peak usage times")
            st.markdown("- User retention rate")

        with col2:
            st.markdown("#### Learning Progress")
            st.markdown("- Topic popularity")
            st.markdown("- Assessment completion rates")
            st.markdown("- Average improvement over time")
            st.markdown("- Common topics of difficulty")

    elif success:
        st.info("No statistics available yet.")
    else:
        error_msg = stats.get("error", stats.get("detail", "Failed to load statistics"))
        st.error(f"Error: {error_msg}")

# ============================================================================
# TAB 3: SETTINGS
# ============================================================================

with tab3:
    st.subheader("⚙️ System Settings")

    # Fetch system settings
    success, settings_data = api_client.get("admin/settings")

    if success and settings_data:
        st.markdown("### Current Configuration")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### LLM Configuration")
            st.markdown(f"**Provider:** {settings_data.get('llm_provider', 'N/A')}")
            st.markdown(f"**Model:** {settings_data.get('llm_model', 'N/A')}")
            st.markdown(f"**Temperature:** {settings_data.get('temperature', 'N/A')}")
            st.markdown(f"**Max Tokens:** {settings_data.get('max_tokens', 'N/A')}")

        with col2:
            st.markdown("#### System Information")
            st.markdown(f"**Version:** {settings_data.get('version', 'N/A')}")
            st.markdown(f"**Debug Mode:** {'Enabled' if settings_data.get('debug') else 'Disabled'}")
            st.markdown(f"**Session Timeout:** {settings_data.get('session_timeout_minutes', 'N/A')} minutes")

        st.divider()

        st.info("⚠️ System settings are currently read-only. To modify settings, update the .env file and restart the backend server.")

    elif success:
        st.info("No settings available.")
    else:
        error_msg = settings_data.get("error", settings_data.get("detail", "Failed to load settings"))
        st.error(f"Error: {error_msg}")

st.divider()

# Admin tips
st.markdown("### 💡 Admin Tips")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **User Management Best Practices:**
    - Regularly review inactive users
    - Monitor assessment completion rates
    - Encourage struggling students
    - Grant admin privileges carefully
    """)

with col2:
    st.markdown("""
    **Security Recommendations:**
    - Change default admin password immediately
    - Review user activity logs regularly
    - Keep the system updated
    - Use strong authentication methods
    """)
