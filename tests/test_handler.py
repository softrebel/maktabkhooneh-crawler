import unittest
from src.handler import MaktabkhoonehCrawler
import httpx
from src._core.schemas import UserInfo
from unittest.mock import patch, MagicMock
from src._core.schemas import UserInfo, LoginResponse


class TestMaktabkhoonehCrawler(unittest.TestCase):
    def test_init_with_default_values(self):
        crawler = MaktabkhoonehCrawler(username="test_user", password="test_pass")
        self.assertEqual(crawler.username, "test_user")
        self.assertEqual(crawler.password, "test_pass")
        self.assertIsNone(crawler.user_info)
        self.assertIsNone(crawler._client)
        self.assertIsNotNone(crawler.headers)
        self.assertEqual(crawler.cookies_file, "Maktabkhooneh.cookies")
        self.assertEqual(crawler.save_path, "data")
        self.assertEqual(crawler._crawled_links, [])
        self.assertIsNone(crawler.proxy)

    def test_init_with_custom_values(self):
        client = httpx.Client()
        headers = {"custom-header": "value"}
        crawler = MaktabkhoonehCrawler(
            username="test_user",
            password="test_pass",
            client=client,
            headers=headers,
            cookies_file="custom_cookies_file",
            save_path="custom_save_path",
            proxy="http://proxy",
        )
        self.assertEqual(crawler.username, "test_user")
        self.assertEqual(crawler.password, "test_pass")
        self.assertIsNone(crawler.user_info)
        self.assertEqual(crawler._client, client)
        self.assertEqual(crawler.headers, headers)
        self.assertEqual(crawler.cookies_file, "custom_cookies_file")
        self.assertEqual(crawler.save_path, "custom_save_path")
        self.assertEqual(crawler._crawled_links, [])
        self.assertEqual(crawler.proxy, "http://proxy")

    @patch("src.handler.save_cookies")
    @patch("src.handler.httpx.Client.request")
    def test_login_success(self, mock_request, mock_save_cookies):
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": "logined"}
        mock_request.return_value = mock_response

        crawler = MaktabkhoonehCrawler(username="test_user", password="test_pass")
        user_info = crawler.login()

        self.assertIsNotNone(user_info)
        self.assertEqual(crawler.user_info, user_info)
        mock_save_cookies.assert_called_once_with(crawler.client, crawler.cookies_file)

    @patch("src.handler.httpx.Client.request")
    def test_login_user_not_exist(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": "get-token"}
        mock_request.return_value = mock_response

        crawler = MaktabkhoonehCrawler(username="test_user", password="test_pass")
        with self.assertRaises(Exception) as context:
            crawler.login()
        self.assertEqual(str(context.exception), "get-token")

    @patch("src.handler.httpx.Client.request")
    def test_login_invalid_format(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": "invalid-format"}
        mock_request.return_value = mock_response

        crawler = MaktabkhoonehCrawler(username="test_user", password="test_pass")
        with self.assertRaises(Exception) as context:
            crawler.login()
        self.assertEqual(str(context.exception), "invalid-format")

    @patch("src.handler.httpx.Client.request")
    def test_login_unexpected_message(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": "unexpected"}
        mock_request.return_value = mock_response

        crawler = MaktabkhoonehCrawler(username="test_user", password="test_pass")
        with self.assertRaises(Exception) as context:
            crawler.login()
        self.assertEqual(str(context.exception), "unexpected")


if __name__ == "__main__":
    unittest.main()
