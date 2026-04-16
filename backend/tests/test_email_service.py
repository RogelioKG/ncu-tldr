from unittest.mock import MagicMock, patch

from botocore.exceptions import ClientError

from app.services.email_service import send_verification_email


def test_send_verification_email_success():
    with patch("app.services.email_service._get_ses_client") as mock_fn:
        mock_client = MagicMock()
        mock_client.send_email.return_value = {"MessageId": "test-123"}
        mock_fn.return_value = mock_client

        result = send_verification_email("109999001@cc.ncu.edu.tw", "test-token-abc")

        assert result is True
        call_kwargs = mock_client.send_email.call_args.kwargs
        assert "test-token-abc" in call_kwargs["Message"]["Body"]["Html"]["Data"]
        assert call_kwargs["Destination"] == {
            "ToAddresses": ["109999001@cc.ncu.edu.tw"]
        }


def test_send_verification_email_ses_error_returns_false():
    with patch("app.services.email_service._get_ses_client") as mock_fn:
        mock_client = MagicMock()
        mock_client.send_email.side_effect = ClientError(
            {"Error": {"Code": "MessageRejected", "Message": "rejected"}},
            "SendEmail",
        )
        mock_fn.return_value = mock_client

        result = send_verification_email("109999001@cc.ncu.edu.tw", "test-token-abc")

        assert result is False
