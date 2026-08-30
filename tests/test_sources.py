from config.sources import SOURCES, Source


def test_sources_exist():
    assert len(SOURCES) >= 1


def test_source_structure():
    for source in SOURCES:
        assert isinstance(source, Source)
        assert source.name
        assert source.url
        assert source.category
        assert source.geography
        assert source.credibility_tier
