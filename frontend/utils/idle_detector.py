import streamlit.components.v1 as components

"""
JavaScript-based idle detection for Layer 3 analytics.
Injects a script that monitors window focus/blur and idle timeout,
then posts events directly to the backend via fetch().
"""


def inject_idle_detector(
    backend_url: str = "http://localhost:8000",
    idle_timeout_seconds: int = 300,
):
    """
    Inject JavaScript for idle detection and focus/blur tracking.

    The JS script:
    - Tracks window focus/blur events
    - Detects idle after idle_timeout_seconds of no mouse/keyboard activity
    - Posts events directly to the backend via fetch() using the JWT token
      from localStorage (stored by api_client._store_token_in_browser)
    - Batches events and flushes every 30 seconds

    Args:
        backend_url: Backend API base URL for direct JS-to-backend posting
        idle_timeout_seconds: Seconds of inactivity before marking the user as idle
    """
    js_code = f"""
    <script>
    (function() {{
        // Prevent multiple injections in the same page
        if (window._idleDetectorInitialized) return;
        window._idleDetectorInitialized = true;

        const IDLE_TIMEOUT = {idle_timeout_seconds * 1000};
        const FLUSH_INTERVAL = 30000;
        const BACKEND_URL = '{backend_url}';
        const STORAGE_KEY = 'analytics_idle_events';

        let idleTimer = null;
        let isIdle = false;
        let isFocused = document.hasFocus();

        function getSessionId() {{
            let sid = sessionStorage.getItem('analytics_session_id');
            if (!sid) {{
                sid = crypto.randomUUID();
                sessionStorage.setItem('analytics_session_id', sid);
            }}
            return sid;
        }}

        function getEvents() {{
            try {{
                return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
            }} catch(e) {{ return []; }}
        }}

        function pushEvent(category, action) {{
            const events = getEvents();
            events.push({{
                session_id: getSessionId(),
                event_category: category,
                event_action: action,
                page_name: getCurrentPage(),
                extra_data: {{ source: 'js_idle_detector' }}
            }});
            localStorage.setItem(STORAGE_KEY, JSON.stringify(events));
        }}

        function getCurrentPage() {{
            // Derive page name from Streamlit's URL path
            const path = window.parent.location.pathname.toLowerCase();
            if (path.includes('chat')) return 'chat';
            if (path.includes('assessment')) return 'assessment';
            if (path.includes('progress')) return 'progress';
            if (path.includes('admin')) return 'admin';
            return 'home';
        }}

        async function flushEvents() {{
            const events = getEvents();
            if (events.length === 0) return;

            // Read auth token from localStorage
            let token = null;
            try {{
                const authData = JSON.parse(localStorage.getItem('auth_data') || '{{}}');
                token = authData.token;
            }} catch(e) {{ return; }}
            if (!token) return;

            try {{
                await fetch(BACKEND_URL + '/analytics/events', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + token
                    }},
                    body: JSON.stringify({{ events: events }})
                }});
                localStorage.setItem(STORAGE_KEY, '[]');
            }} catch(e) {{
                // Silent fail — analytics should never break UX
            }}
        }}

        function resetIdleTimer() {{
            if (isIdle) {{
                isIdle = false;
                pushEvent('idle_end', 'user_active');
            }}
            clearTimeout(idleTimer);
            idleTimer = setTimeout(function() {{
                isIdle = true;
                pushEvent('idle_start', 'user_idle');
            }}, IDLE_TIMEOUT);
        }}

        // Focus/blur events
        window.addEventListener('focus', function() {{
            if (!isFocused) {{
                isFocused = true;
                pushEvent('session_start', 'window_focus');
                resetIdleTimer();
            }}
        }});

        window.addEventListener('blur', function() {{
            isFocused = false;
            pushEvent('session_end', 'window_blur');
            clearTimeout(idleTimer);
        }});

        // Activity events for idle detection
        document.addEventListener('mousemove', resetIdleTimer);
        document.addEventListener('keypress', resetIdleTimer);
        document.addEventListener('scroll', resetIdleTimer);
        document.addEventListener('click', resetIdleTimer);

        // Initialize
        if (isFocused) {{
            pushEvent('session_start', 'page_load');
            resetIdleTimer();
        }}

        // Periodic flush
        setInterval(flushEvents, FLUSH_INTERVAL);
    }})();
    </script>
    """
    components.html(js_code, height=0)
