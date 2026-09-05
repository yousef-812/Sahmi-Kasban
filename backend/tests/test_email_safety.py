import pytest
from app.services.email_safety import (
    InvalidEmailError,
    validate_email_safety,
)


def test_validate_email_safety_valid():
    assert validate_email_safety("user@gmail.com", check_dns=False) == "user@gmail.com"
    assert validate_email_safety("yousefftaalip@gmail.com", check_dns=False) == "yousefftaalip@gmail.com"
    assert validate_email_safety("admin@sahmi-kasban.bdaey.com", check_dns=False) == "admin@sahmi-kasban.bdaey.com"


def test_validate_email_safety_disposable_and_fake():
    with pytest.raises(InvalidEmailError):
        validate_email_safety("spammer@10minutemail.com", check_dns=False)

    with pytest.raises(InvalidEmailError, match="المؤقتة أو الوهمية"):
        validate_email_safety("spammer@tempmail.com", check_dns=False)

    with pytest.raises(InvalidEmailError, match="المؤقتة أو الوهمية"):
        validate_email_safety("fake@yopmail.com", check_dns=False)


def test_validate_email_safety_typo_suggestions():
    with pytest.raises(InvalidEmailError, match="gmail.com"):
        validate_email_safety("user@gmai.com", check_dns=False)

    with pytest.raises(InvalidEmailError, match="yahoo.com"):
        validate_email_safety("user@yaho.com", check_dns=False)


def test_validate_email_safety_syntax():
    with pytest.raises(InvalidEmailError, match="صيغة البريد"):
        validate_email_safety("invalid_email_at_domain.com", check_dns=False)
