"""
Persistent Storage Manager for Streamlit Deployments
Handles data persistence across app redeployments using external storage.
"""

import json
import os
import tempfile
from typing import Dict, List, Optional
import streamlit as st

class PersistentStorageManager:
    """
    Manages persistent storage of analytics data across Streamlit deployments.
    Uses Streamlit's secrets management and external storage options.
    """
    
    def __init__(self):
        self.storage_type = self._detect_storage_type()
        self.local_cache = {}
        
        # Debug info for troubleshooting
        if st.secrets.get('GITHUB_TOKEN') and st.secrets.get('GIST_ID'):
            st.sidebar.success(f"✅ Storage: {self.storage_type}")
        else:
            st.sidebar.warning(f"⚠️ Storage: {self.storage_type}")
    
    def _detect_storage_type(self) -> str:
        """Detect available storage type based on environment."""
        
        # Check if GitHub Gist secrets are available (prioritize this for Streamlit Cloud)
        if st.secrets.get('GITHUB_TOKEN') and st.secrets.get('GIST_ID'):
            return 'github_gist'
        
        # Check if running on Streamlit Cloud (various hostname patterns)
        hostname = os.getenv('HOSTNAME', '').lower()
        is_streamlit_cloud = (
            os.getenv('STREAMLIT_CLOUD', False) or 
            'streamlit' in hostname or 
            'share.streamlit.io' in hostname or
            any(cloud_indicator in hostname for cloud_indicator in ['heroku', 'railway', 'vercel'])
        )
        
        if is_streamlit_cloud:
            # Option 2: Simple HTTP endpoint
            if st.secrets.get('STORAGE_ENDPOINT'):
                return 'http_storage'
            
            # Option 3: Session state only (temporary)
            else:
                st.warning("⚠️ No persistent storage configured. Data will be lost on redeployment.")
                return 'session_only'
        
        # Local development - use files
        return 'local_files'
    
    def save_feedback_data(self, feedback_data: List[Dict]) -> bool:
        """Save feedback data to persistent storage."""
        try:
            if self.storage_type == 'local_files':
                return self._save_to_local_file('feedback_log.json', feedback_data)
            
            elif self.storage_type == 'github_gist':
                return self._save_to_github_gist('feedback_log.json', feedback_data)
            
            elif self.storage_type == 'http_storage':
                return self._save_to_http_storage('feedback_log.json', feedback_data)
            
            elif self.storage_type == 'session_only':
                # Store in session state (temporary)
                st.session_state['feedback_data'] = feedback_data
                return True
                
        except Exception as e:
            st.error(f"Failed to save feedback data: {e}")
            return False
    
    def load_feedback_data(self) -> List[Dict]:
        """Load feedback data from persistent storage."""
        try:
            if self.storage_type == 'local_files':
                return self._load_from_local_file('feedback_log.json')
            
            elif self.storage_type == 'github_gist':
                return self._load_from_github_gist('feedback_log.json')
            
            elif self.storage_type == 'http_storage':
                return self._load_from_http_storage('feedback_log.json')
            
            elif self.storage_type == 'session_only':
                return st.session_state.get('feedback_data', [])
                
        except Exception as e:
            st.error(f"Failed to load feedback data: {e}")
            return []
    
    def save_analytics_data(self, analytics_data: List[Dict]) -> bool:
        """Save query analytics data to persistent storage."""
        try:
            if self.storage_type == 'local_files':
                return self._save_to_local_file('query_analytics.json', analytics_data)
            
            elif self.storage_type == 'github_gist':
                return self._save_to_github_gist('query_analytics.json', analytics_data)
            
            elif self.storage_type == 'http_storage':
                return self._save_to_http_storage('query_analytics.json', analytics_data)
            
            elif self.storage_type == 'session_only':
                st.session_state['analytics_data'] = analytics_data
                return True
                
        except Exception as e:
            st.error(f"Failed to save analytics data: {e}")
            return False
    
    def load_analytics_data(self) -> List[Dict]:
        """Load query analytics data from persistent storage."""
        try:
            if self.storage_type == 'local_files':
                return self._load_from_local_file('query_analytics.json')
            
            elif self.storage_type == 'github_gist':
                return self._load_from_github_gist('query_analytics.json')
            
            elif self.storage_type == 'http_storage':
                return self._load_from_http_storage('query_analytics.json')
            
            elif self.storage_type == 'session_only':
                return st.session_state.get('analytics_data', [])
                
        except Exception as e:
            st.error(f"Failed to load analytics data: {e}")
            return []
    
    # Local file operations
    def _save_to_local_file(self, filename: str, data: List[Dict]) -> bool:
        """Save data to local file."""
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False
    
    def _load_from_local_file(self, filename: str) -> List[Dict]:
        """Load data from local file."""
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return []
    
    # GitHub Gist operations
    def _save_to_github_gist(self, filename: str, data: List[Dict]) -> bool:
        """Save data to GitHub Gist."""
        import requests
        
        try:
            gist_id = st.secrets['GIST_ID']
            github_token = st.secrets['GITHUB_TOKEN']
            
            headers = {
                'Authorization': f'token {github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            payload = {
                'files': {
                    filename: {
                        'content': json.dumps(data, indent=2)
                    }
                }
            }
            
            response = requests.patch(
                f'https://api.github.com/gists/{gist_id}',
                headers=headers,
                json=payload
            )
            
            return response.status_code == 200
            
        except Exception:
            return False
    
    def _load_from_github_gist(self, filename: str) -> List[Dict]:
        """Load data from GitHub Gist."""
        import requests
        
        try:
            gist_id = st.secrets['GIST_ID']
            github_token = st.secrets['GITHUB_TOKEN']
            
            headers = {
                'Authorization': f'token {github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get(
                f'https://api.github.com/gists/{gist_id}',
                headers=headers
            )
            
            if response.status_code == 200:
                gist_data = response.json()
                if filename in gist_data['files']:
                    content = gist_data['files'][filename]['content']
                    return json.loads(content)
            
        except Exception:
            pass
        
        return []
    
    # HTTP storage operations (for custom endpoints)
    def _save_to_http_storage(self, filename: str, data: List[Dict]) -> bool:
        """Save data to HTTP storage endpoint."""
        import requests
        
        try:
            endpoint = st.secrets['STORAGE_ENDPOINT']
            api_key = st.secrets.get('STORAGE_API_KEY', '')
            
            payload = {
                'filename': filename,
                'data': data,
                'api_key': api_key
            }
            
            response = requests.post(f'{endpoint}/save', json=payload)
            return response.status_code == 200
            
        except Exception:
            return False
    
    def _load_from_http_storage(self, filename: str) -> List[Dict]:
        """Load data from HTTP storage endpoint."""
        import requests
        
        try:
            endpoint = st.secrets['STORAGE_ENDPOINT']
            api_key = st.secrets.get('STORAGE_API_KEY', '')
            
            params = {
                'filename': filename,
                'api_key': api_key
            }
            
            response = requests.get(f'{endpoint}/load', params=params)
            
            if response.status_code == 200:
                return response.json().get('data', [])
                
        except Exception:
            pass
        
        return []

# Global instance
storage_manager = PersistentStorageManager()