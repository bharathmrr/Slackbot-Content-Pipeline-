"""
Integration tests for API endpoints.
"""

import pytest
import requests
import os


class TestAPIEndpoints:
    """Integration tests for API endpoints."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.base_url = os.getenv("BASE_URL", "http://localhost:8000")
        self.session = requests.Session()
        self.session.timeout = 30
    
    def test_health_endpoint(self):
        """Test health endpoint."""
        response = self.session.get(f"{self.base_url}/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = self.session.get(f"{self.base_url}/")
        
        assert response.status_code == 200
        data = response.json()
        assert "Slackbot Content Pipeline" in data["message"]
        assert "version" in data
    
    def test_batch_endpoint_not_found(self):
        """Test batch endpoint with non-existent ID."""
        response = self.session.get(f"{self.base_url}/api/batches/non-existent-id")
        
        # Should return 404 or error response
        assert response.status_code in [404, 500]
    
    def test_api_response_format(self):
        """Test API response format consistency."""
        response = self.session.get(f"{self.base_url}/health")
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json"
        
        # Should be valid JSON
        data = response.json()
        assert isinstance(data, dict)
    
    def test_cors_headers(self):
        """Test CORS headers are present."""
        response = self.session.options(f"{self.base_url}/health")
        
        # Should have CORS headers in development
        if "localhost" in self.base_url:
            assert "access-control-allow-origin" in response.headers
    
    @pytest.mark.parametrize("endpoint", ["/health", "/", "/api/batches/test"])
    def test_response_times(self, endpoint):
        """Test response times for various endpoints."""
        import time
        
        start_time = time.time()
        response = self.session.get(f"{self.base_url}{endpoint}")
        response_time = time.time() - start_time
        
        # Response should be under 5 seconds
        assert response_time < 5.0
        
        # Should get some response (not necessarily 200)
        assert response.status_code in [200, 404, 500]
