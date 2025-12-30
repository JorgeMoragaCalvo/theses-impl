import json
from typing import Optional, Any

import streamlit as st
import requests
"""
API Client for authenticated requests to the backend.
Handles token management and automatic header injection.
"""

class APIClient:
    """Centralized API client with authentication support."""

    def __init__(self, base_url: str):
        """
        Initialize API client.

        Args:
            base_url: Base URL for the backend API
        """
        self.base_url = base_url.rstrip("/")

    @staticmethod
    def _get_headers() -> dict[str, str]:
        """
        Get headers with authentication token if available.

        Returns:
            Dictionary of headers including Authorization if logged in
        """
        headers = {"Content-Type": "application/json"}

        # Add Authorization header if token exists
        if "access_token" in st.session_state and st.session_state.access_token:
            headers["Authorization"] = f"Bearer {st.session_state.access_token}"

        return headers

    def _handle_response(self, response: requests.Response) -> tuple[bool, Any]:
        """
        Handle API response and check for authentication errors.

        Args:
            response: Response object from requests

        Returns:
            Tuple of (success, data/error)
        """
        # Handle 401 Unauthorized - token expired or invalid
        if response.status_code == 401:
            # Clear the session and redirect to the login
            self.logout()
            # st.error("Session expired. Please login again.")
            # st.rerun()
            return False, {"error": "Unauthorized"}

        # Handle 403 Forbidden - insufficient permissions
        if response.status_code == 403:
            return False, {"error": "You don't have permission to access this resource"}

        # Handle other errors
        if response.status_code >= 400:
            try:
                error_data = response.json()
                return False, error_data
            except json.JSONDecodeError:
                return False, {"error": f"HTTP {response.status_code}: {response.text}"}

        # Success
        try:
            return True, response.json()
        except json.JSONDecodeError:
            return True, None

    def get(self, endpoint: str, params: dict | None = None) -> tuple[bool, Any]:
        """
        Make GET request to API.

        Args:
            endpoint: API endpoint (without base URL)
            params: Optional query parameters

        Returns:
            Tuple of (success, data/error)
        """
        try:
            response = requests.get(
                f"{self.base_url}/{endpoint.lstrip('/')}",
                headers=self._get_headers(),
                params=params,
                timeout=30
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return False, {"error": f"Network error: {str(e)}"}

    def post(self, endpoint: str, data: dict | None = None, json_data: dict | None = None) -> tuple[bool, Any]:
        """
        Make POST request to API.

        Args:
            endpoint: API endpoint (without base URL)
            data: Optional form data
            json_data: Optional JSON data

        Returns:
            Tuple of (success, data/error)
        """
        try:
            response = requests.post(
                f"{self.base_url}/{endpoint.lstrip('/')}",
                headers=self._get_headers(),
                data=data,
                json=json_data,
                timeout=30
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return False, {"error": f"Network error: {str(e)}"}

    def put(self, endpoint: str, data: dict | None = None, json_data: dict | None = None) -> tuple[bool, Any]:
        """
        Make the PUT request to API.

        Args:
            endpoint: API endpoint (without base URL)
            data: Optional form data
            json_data: Optional JSON data

        Returns:
            Tuple of (success, data/error)
        """
        try:
            response = requests.put(
                f"{self.base_url}/{endpoint.lstrip('/')}",
                headers=self._get_headers(),
                data=data,
                json=json_data,
                timeout=30
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return False, {"error": f"Network error: {str(e)}"}

    def delete(self, endpoint: str) -> tuple[bool, Any]:
        """
        Make the DELETE request to API.

        Args:
            endpoint: API endpoint (without base URL)

        Returns:
            Tuple of (success, data/error)
        """
        try:
            response = requests.delete(
                f"{self.base_url}/{endpoint.lstrip('/')}",
                headers=self._get_headers(),
                timeout=30
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return False, {"error": f"Network error: {str(e)}"}

    # Authentication methods

    def register(self, name: str, email: str, password: str) -> tuple[bool, Any]:
        """
        Register a new user.

        Args:
            name: User's name
            email: User's email
            password: User's password (min 8 characters)

        Returns:
            Tuple of (success, token_data/error)
        """
        success, data = self.post("/auth/register", json_data={
            "name": name,
            "email": email,
            "password": password
        })

        if success and data:
            self._store_auth_data(data)

        return success, data

    def login(self, email: str, password: str) -> tuple[bool, Any]:
        """
        Login with email and password.

        Args:
            email: User's email
            password: User's password

        Returns:
            Tuple of (success, token_data/error)
        """
        success, data = self.post("/auth/login", json_data={
            "email": email,
            "password": password
        })

        if success and data:
            self._store_auth_data(data)

        return success, data

    def logout(self):
        """Logout and clear session data."""
        # Clear session state
        keys_to_clear = [
            "access_token", "user", "student_id", "student_name",
            "student_email", "user_role", "messages", "conversation_id"
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]

        # Clear localStorage
        self._clear_token_from_browser()

    def _store_auth_data(self, data: dict):
        """Store authentication data in the session state and browser."""
        st.session_state.access_token = data.get("access_token")
        st.session_state.user = data.get("user")
        st.session_state.student_id = data["user"]["id"]
        st.session_state.student_name = data["user"]["name"]
        st.session_state.student_email = data["user"]["email"]
        st.session_state.user_role = data["user"]["role"]

        # Store token in browser localStorage (for persistence)
        self._store_token_in_browser(data.get("access_token"), data.get("user"))

    def get_current_user(self) -> tuple[bool, Any]:
        """
        Get current authenticated user information.

        Returns:
            Tuple of (success, user_data/error)
        """
        return self.get("/auth/me")

    @staticmethod
    def _store_token_in_browser(token: str, user: dict):
        """
        Store authentication token in browser localStorage for persistence.

        Args:
            token: JWT access token
            user: User data dictionary
        """
        # Use Streamlit's JS execution to store in localStorage
        storage_data = json.dumps({"token": token, "user": user})
        st.components.v1.html(
            f"""
            <script>
                localStorage.setItem('auth_data', '{storage_data}');
            </script>
            """,
            height=0
        )

    @staticmethod
    def _clear_token_from_browser():
        """Clear authentication token from browser localStorage."""
        st.components.v1.html(
            """
            <script>
                localStorage.removeItem('auth_data');
            </script>
            """,
            height=0
        )

    def load_token_from_browser(self):
        """
        Attempt to load the authentication token from browser localStorage.
        This should be called on app startup.
        """
        # Note: Reading from localStorage in Streamlit requires a component
        # For now, we'll rely on session_state persistence
        # In production, you might want to use a proper Streamlit component
        pass

    @staticmethod
    def is_authenticated() -> bool:
        """
        Check if the user is currently authenticated.

        Returns:
            True if the user has a valid token in session
        """
        return "access_token" in st.session_state and st.session_state.access_token is not None

    @staticmethod
    def is_admin() -> bool:
        """
        Check if the current user is an admin.

        Returns:
            True if the user has the admin role
        """
        return st.session_state.get("user_role") == "admin"


def get_api_client(base_url: str) -> APIClient:
    """
    Get or create the API client instance.

    Args:
        base_url: Base URL for the backend API

    Returns:
        APIClient instance
    """
    if "api_client" not in st.session_state:
        st.session_state.api_client = APIClient(base_url)
    return st.session_state.api_client

