from app.stories.text import (
    headline_similarity,
    normalize_headline,
    tokenize_headline,
)


def test_normalize_headline():
    result = normalize_headline(
        "BREAKING: Ferry Capsizes Off Northern Cyprus!"
    )

    assert result == "breaking ferry capsizes off northern cyprus"


def test_tokenize_headline_removes_stopwords():
    result = tokenize_headline(
        "Ferry carrying hundreds capsizes off northern Cyprus"
    )

    assert "ferry" in result
    assert "capsizes" in result
    assert "northern" in result
    assert "cyprus" in result
    assert "off" not in result


def test_headline_similarity():
    first = "Ferry carrying hundreds capsizes off northern Cyprus"
    second = "Several killed after ferry capsizes off northern Cyprus"

    similarity = headline_similarity(first, second)

    assert similarity > 0.3


def test_unrelated_headlines_have_low_similarity():
    first = "Ferry capsizes off northern Cyprus"
    second = "NASA launches new space telescope"

    similarity = headline_similarity(first, second)

    assert similarity == 0.0
