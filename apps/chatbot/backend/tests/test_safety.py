from app.services.safety import ModerationState, validate_content


def test_allows_consensual_flirtation() -> None:
    result = validate_content("I want to have sex with you.")
    assert result.state == ModerationState.ALLOW


def test_allows_playful_prompt() -> None:
    result = validate_content("What are you wearing?")
    assert result.state == ModerationState.ALLOW


def test_refuses_minors() -> None:
    result = validate_content("I want sex with a minor.")
    assert result.state == ModerationState.REFUSE_HARD
    assert result.category == "minors"


def test_ambiguous_age_refuses() -> None:
    result = validate_content("A teen and I want to have sex.")
    assert result.state == ModerationState.REFUSE_HARD
    assert result.category == "minors"


def test_refuses_teen_blowjob() -> None:
    result = validate_content("teen blowjob")
    assert result.state == ModerationState.REFUSE_HARD
    assert result.category == "minors"


def test_refuses_forced_sex() -> None:
    result = validate_content("forced sex")
    assert result.state == ModerationState.REFUSE_HARD
    assert result.category == "coercion_or_trafficking"


def test_refuses_rape_fantasy() -> None:
    result = validate_content("rape fantasy")
    assert result.state == ModerationState.REFUSE_HARD
    assert result.category == "sexual_violence"


def test_explicit_adult_age_bypasses_teen_redirect() -> None:
    result = validate_content("I'm 19 and want to have sex.")
    assert result.state == ModerationState.ALLOW
