import pytest

from tools.config import FastAPIKwArgs, Settings


class TestSettings:
    """Test class for Settings."""

    @pytest.mark.usefixtures("settings")
    def test_local(self, settings: Settings) -> None:
        """Test local settings."""
        assert settings.IS_LOCAL

    @pytest.mark.usefixtures("settings")
    def test_fastapi_kwargs(self, settings: Settings) -> None:
        """Test fastapi_kwargs."""
        kwargs = settings.fastapi_kwargs

        assert kwargs["debug"] is False
        assert kwargs["title"] == "FastAPI"
        assert kwargs["version"] == "0.1.0"
        assert kwargs["openapi_url"] == "/openapi.json"
        assert kwargs["docs_url"] == "/docs"
        assert kwargs["redoc_url"] == "/redoc"
        assert kwargs["openapi_prefix"] == ""

    def test_custom_settings(self) -> None:
        """Test creating settings with custom values."""
        settings = Settings(
            IS_LOCAL=False,
            debug=True,
            title="Custom API",
            version="1.0.0",
        )

        assert not settings.IS_LOCAL
        assert settings.debug
        assert settings.title == "Custom API"
        assert settings.version == "1.0.0"

    def test_default_values(self) -> None:
        """Test that default values are set correctly."""
        settings = Settings()

        assert settings.title == "FastAPI"
        assert settings.version == "0.1.0"
        assert settings.api_prefix_v1 == "/api/v1"
        assert settings.allowed_hosts == ["*"]
        assert settings.debug is False

    def test_allowed_hosts_list(self) -> None:
        """Test that allowed_hosts is a list."""
        expected_count = 2
        settings = Settings(allowed_hosts=["localhost", "example.com"])

        assert isinstance(settings.allowed_hosts, list)
        assert len(settings.allowed_hosts) == expected_count
        assert "localhost" in settings.allowed_hosts


class TestFastAPIKwArgs:
    """Test class for FastAPIKwArgs."""

    def test_model_dump(self) -> None:
        """Test that model_dump returns a dict."""
        kwargs = FastAPIKwArgs(
            debug=True,
            title="Test API",
            summary="Test summary",
            description="Test description",
            version="2.0.0",
            openapi_url="/openapi.json",
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_prefix="",
        )

        result = kwargs.model_dump()

        assert isinstance(result, dict)
        assert result["debug"] is True
        assert result["title"] == "Test API"
        assert result["version"] == "2.0.0"
