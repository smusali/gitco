"""Test that the gitco package can be imported correctly."""


def test_gitco_import():
    """Test that the gitco package can be imported."""
    import gitco

    # Test that version is available
    assert hasattr(gitco, "__version__")
    assert gitco.__version__ == "0.1.0"

    # Test that other metadata is available
    assert hasattr(gitco, "__author__")
    assert hasattr(gitco, "__email__")
    assert hasattr(gitco, "__license__")
    assert hasattr(gitco, "__url__")


def test_gitco_metadata():
    """Test that package metadata is correct."""
    import gitco

    assert gitco.__author__ == "FortyOne Technologies Inc."
    assert gitco.__email__ == "fortyone.technologies@gmail.com"
    assert gitco.__license__ == "MIT"
    assert gitco.__url__ == "https://github.com/41technologies/gitco"
