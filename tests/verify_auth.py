import unittest
from unittest.mock import MagicMock, patch
import json
import uuid
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock supabase_client before any other imports
mock_supabase = MagicMock()
sys.modules['supabase_client'] = MagicMock(supabase=mock_supabase)

# Also mock database.db to avoid real pool issues
mock_db = MagicMock()
sys.modules['database.db'] = mock_db

from app import app

class TestAuthIntegration(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        # Reset mocks
        mock_supabase.reset_mock()
        mock_db.reset_mock()

    def tearDown(self):
        self.app_context.pop()

    def test_signup_logic(self):
        # 1. Test Signup
        mock_user = MagicMock()
        mock_user.id = "user123"
        mock_supabase.auth.sign_up.return_value = MagicMock(user=mock_user)
        
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_table.insert.return_value = mock_table
        mock_table.execute.return_value = MagicMock()

        payload = {
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "TestPassword123"
        }
        res = self.app.post('/signup', json=payload)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['message'], "User created")

    def test_login_logic(self):
        # 2. Test Login
        mock_session = MagicMock()
        mock_session.access_token = "fake-jwt-token"
        mock_user = MagicMock()
        mock_user.id = "user123"
        
        # We must return an object that has .session and .user as attributes, not mocks that look like them?
        # Actually MagicMock is fine, but we need to ensure they return strings for serialization
        mock_res = MagicMock()
        mock_res.session.access_token = "fake-jwt-token"
        mock_res.user.id = "user123"
        mock_res.user.email = "testuser@example.com"
        mock_res.user.user_metadata = {"name": "Test User"}
        mock_supabase.auth.sign_in_with_password.return_value = mock_res

        payload = {
            "email": "testuser@example.com",
            "password": "TestPassword123"
        }
        res = self.app.post('/login', json=payload)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['access_token'], "fake-jwt-token")
        self.assertEqual(res.json['user'], "user123")

    def test_create_chat_protected(self):
        # 3. Test Protected Create Chat
        
        # Case A: No token
        res = self.app.post('/create-chat', json={"title": "Test Chat"})
        self.assertEqual(res.status_code, 401)
        
        # Case B: Valid token
        mock_user = MagicMock()
        mock_user.id = "user123"
        mock_supabase.auth.get_user.return_value = MagicMock(user=mock_user)
        
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_table.insert.return_value = mock_table
        # execute() should return something JSON serializable
        mock_table.execute.return_value = MagicMock(data={"id": "chat1", "title": "Test Chat"})

        res = self.app.post('/create-chat', 
                            json={"title": "Test Chat"},
                            headers={"Authorization": "Bearer valid-token"})
        
        self.assertEqual(res.status_code, 200)
        # Verify insert used g.user.id
        mock_table.insert.assert_called_once()
        call_args = mock_table.insert.call_args[0][0]
        self.assertEqual(call_args['user_id'], "user123")

    def test_data_isolation_sessions(self):
        # 5. Test Data Isolation (Postgres sessions)
        mock_user = MagicMock()
        mock_user.id = "userA"
        mock_supabase.auth.get_user.return_value = MagicMock(user=mock_user)
        
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_db.get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur
        
        # Simulate /sessions?offset=0
        mock_cur.fetchall.return_value = [("sess1", MagicMock(isoformat=lambda: "2026-03-26T18:00:00"))]
        
        res = self.app.get('/sessions', headers={"Authorization": "Bearer tokenA"})
        
        self.assertEqual(res.status_code, 200)
        # Verify SQL query includes WHERE user_id = %s
        args, kwargs = mock_cur.execute.call_args
        sql = args[0]
        params = args[1]
        self.assertIn("WHERE user_id = %s", sql)
        self.assertEqual(params[0], "userA")

if __name__ == '__main__':
    unittest.main()
