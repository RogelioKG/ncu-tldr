import boto3
from botocore.exceptions import ClientError

from app.config import get_settings


def _get_ses_client():
    settings = get_settings()
    return boto3.client(
        "ses",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )


def send_verification_email(to_email: str, token: str) -> bool:
    settings = get_settings()
    verify_url = f"{settings.verify_base_url}/verify-email?token={token}"
    client = _get_ses_client()
    try:
        client.send_email(
            Source=settings.email_from,
            Destination={"ToAddresses": [to_email]},
            Message={
                "Subject": {"Data": "NCU-TLDR 信箱驗證", "Charset": "UTF-8"},
                "Body": {
                    "Html": {
                        "Data": (
                            f"<p>請點擊以下連結完成 NCU-TLDR 信箱驗證：</p>"
                            f'<p><a href="{verify_url}">{verify_url}</a></p>'
                            f"<p>此連結將於 24 小時後失效。</p>"
                        ),
                        "Charset": "UTF-8",
                    }
                },
            },
        )
        return True
    except ClientError:
        return False
