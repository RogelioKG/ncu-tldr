from email import message_from_string
from unittest.mock import MagicMock, patch

from botocore.exceptions import ClientError

from app.services.email_service import send_verification_email


def test_send_verification_email_success():
    with patch("app.services.email_service._get_ses_client") as mock_fn:
        mock_client = MagicMock()
        mock_client.send_raw_email.return_value = {"MessageId": "test-123"}
        mock_fn.return_value = mock_client

        result = send_verification_email("109999001@cc.ncu.edu.tw", "test-token-abc")

        assert result is True
        call_kwargs = mock_client.send_raw_email.call_args.kwargs
        raw_message = call_kwargs["RawMessage"]["Data"]
        msg = message_from_string(raw_message)
        html_part = msg.get_payload()[0]
        html_body = html_part.get_payload(decode=True).decode("utf-8")
        assert "test-token-abc" in html_body
        assert call_kwargs["Destinations"] == [
            "109999001@cc.ncu.edu.tw",
            "hsuchen@g.ncu.edu.tw",
        ]


def test_send_verification_email_ses_error_returns_false():
    with patch("app.services.email_service._get_ses_client") as mock_fn:
        mock_client = MagicMock()
        mock_client.send_raw_email.side_effect = ClientError(
            {"Error": {"Code": "MessageRejected", "Message": "rejected"}},
            "SendRawEmail",
        )
        mock_fn.return_value = mock_client

        result = send_verification_email("109999001@cc.ncu.edu.tw", "test-token-abc")

        assert result is False
