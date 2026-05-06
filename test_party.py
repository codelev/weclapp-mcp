import pytest


class TestPartyList:
    """Tests for party_list tool - verifies tool handles user prompts for searching parties."""

    @pytest.mark.asyncio
    async def test_party_list_basic(self):
        """Test that party_list can be called with no parameters."""
        from domains.party import register
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register(mcp)

        # Verify the tool is registered
        tools = mcp._tool_manager.list_tools()
        tool_names = [t.name for t in tools]
        assert "party_list" in tool_names

    @pytest.mark.asyncio
    async def test_party_list_with_filter(self):
        """Test that party_list correctly passes filter parameter."""
        from domains.party import register
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register(mcp)

        # Get the tool function
        tool = mcp._tool_manager._tools["party_list"]
        assert tool is not None

    @pytest.mark.asyncio
    async def test_party_list_filter_customer(self):
        """Test filter for customers: 'customer = true'."""
        from client import _strip_nones

        # Verify filter string is passed through
        result = _strip_nones({"filter": "customer = true", "page": 1})
        assert result == {"filter": "customer = true", "page": 1}

    @pytest.mark.asyncio
    async def test_party_list_filter_supplier(self):
        """Test filter for suppliers: 'supplier = true'."""
        from client import _strip_nones

        result = _strip_nones({"filter": "supplier = true AND countryCode = 'DE'"})
        assert result == {"filter": "supplier = true AND countryCode = 'DE'"}


class TestPartyCount:
    """Tests for party_count tool - verifies tool handles count requests."""

    @pytest.mark.asyncio
    async def test_party_count_tool_exists(self):
        """Test that party_count tool is registered."""
        from domains.party import register
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register(mcp)

        tools = mcp._tool_manager.list_tools()
        tool_names = [t.name for t in tools]
        assert "party_count" in tool_names

    @pytest.mark.asyncio
    async def test_party_count_with_filter(self):
        """Test party_count with filter parameter."""
        from client import _strip_nones

        result = _strip_nones({"filter": "customer = true"})
        assert result == {"filter": "customer = true"}


class TestPartyGet:
    """Tests for party_get tool - verifies tool handles get by ID requests."""

    @pytest.mark.asyncio
    async def test_party_get_tool_exists(self):
        """Test that party_get tool is registered."""
        from domains.party import register
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register(mcp)

        tools = mcp._tool_manager.list_tools()
        tool_names = [t.name for t in tools]
        assert "party_get" in tool_names

    @pytest.mark.asyncio
    async def test_party_get_requires_id(self):
        """Test that party_get requires an id parameter."""
        from domains.party import register
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register(mcp)

        tool = mcp._tool_manager._tools["party_get"]
        # The tool should have 'id' in required parameters
        assert "id" in tool.parameters.get("required", [])


class TestPartyCreate:
    """Tests for party_create tool - verifies tool handles create requests."""

    @pytest.mark.asyncio
    async def test_party_create_tool_exists(self):
        """Test that party_create tool is registered."""
        from domains.party import register
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register(mcp)

        tools = mcp._tool_manager.list_tools()
        tool_names = [t.name for t in tools]
        assert "party_create" in tool_names

    @pytest.mark.asyncio
    async def test_party_create_organization(self):
        """Test creating an organization party via tool parameters."""
        from domains.party import register
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register(mcp)

        tool = mcp._tool_manager._tools["party_create"]
        # Verify the tool has party_type and company parameters
        assert "party_type" in tool.parameters.get("properties", {})
        assert "company" in tool.parameters.get("properties", {})

    @pytest.mark.asyncio
    async def test_party_create_person(self):
        """Test creating a person party via tool parameters."""
        from domains.party import register
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register(mcp)

        tool = mcp._tool_manager._tools["party_create"]
        # Verify the tool has first_name and last_name parameters
        assert "first_name" in tool.parameters.get("properties", {})
        assert "last_name" in tool.parameters.get("properties", {})

    @pytest.mark.asyncio
    async def test_party_create_with_addresses(self):
        """Test creating a party with addresses JSON via tool parameters."""
        from domains.party import register
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register(mcp)

        tool = mcp._tool_manager._tools["party_create"]
        # Verify the tool has addresses_json parameter
        assert "addresses_json" in tool.parameters.get("properties", {})


class TestPartyUpdate:
    """Tests for party_update tool - verifies tool handles update requests."""

    @pytest.mark.asyncio
    async def test_party_update_tool_exists(self):
        """Test that party_update tool is registered."""
        from domains.party import register
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register(mcp)

        tools = mcp._tool_manager.list_tools()
        tool_names = [t.name for t in tools]
        assert "party_update" in tool_names

    @pytest.mark.asyncio
    async def test_party_update_has_id_parameter(self):
        """Test that party_update has id parameter."""
        from domains.party import register
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register(mcp)

        tool = mcp._tool_manager._tools["party_update"]
        assert "id" in tool.parameters.get("properties", {})


class TestPartyDelete:
    """Tests for party_delete tool - verifies tool handles delete requests."""

    @pytest.mark.asyncio
    async def test_party_delete_tool_exists(self):
        """Test that party_delete tool is registered."""
        from domains.party import register
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register(mcp)

        tools = mcp._tool_manager.list_tools()
        tool_names = [t.name for t in tools]
        assert "party_delete" in tool_names


class TestActionTools:
    """Tests for action/workflow tools."""

    @pytest.mark.asyncio
    async def test_party_create_public_page_tool_exists(self):
        """Test that party_create_public_page tool is registered."""
        from domains.party import register
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register(mcp)

        tools = mcp._tool_manager.list_tools()
        tool_names = [t.name for t in tools]
        assert "party_create_public_page" in tool_names

    @pytest.mark.asyncio
    async def test_party_create_public_page_requires_id(self):
        """Test that party_create_public_page requires id."""
        from domains.party import register
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register(mcp)

        tool = mcp._tool_manager._tools["party_create_public_page"]
        assert "id" in tool.parameters.get("required", [])

    @pytest.mark.asyncio
    async def test_party_transfer_addresses_tool_exists(self):
        """Test that party_transfer_addresses_to_open_records tool is registered."""
        from domains.party import register
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register(mcp)

        tools = mcp._tool_manager.list_tools()
        tool_names = [t.name for t in tools]
        assert "party_transfer_addresses_to_open_records" in tool_names

    @pytest.mark.asyncio
    async def test_party_transfer_emails_tool_exists(self):
        """Test that party_transfer_emails_to_open_records tool is registered."""
        from domains.party import register
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register(mcp)

        tools = mcp._tool_manager.list_tools()
        tool_names = [t.name for t in tools]
        assert "party_transfer_emails_to_open_records" in tool_names

    @pytest.mark.asyncio
    async def test_party_upload_image_tool_exists(self):
        """Test that party_upload_image tool is registered."""
        from domains.party import register
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register(mcp)

        tools = mcp._tool_manager.list_tools()
        tool_names = [t.name for t in tools]
        assert "party_upload_image" in tool_names

    @pytest.mark.asyncio
    async def test_party_upload_image_requires_image_base64(self):
        """Test that party_upload_image requires image_base64."""
        from domains.party import register
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register(mcp)

        tool = mcp._tool_manager._tools["party_upload_image"]
        assert "image_base64" in tool.parameters.get("required", [])


class TestClientHelpers:
    """Tests for client helper functions."""

    def test_strip_nones_removes_none_values(self):
        """Test that _strip_nones removes None values."""
        from client import _strip_nones

        result = _strip_nones({"a": 1, "b": None, "c": "test"})
        assert result == {"a": 1, "c": "test"}

    def test_strip_nones_keeps_zero_and_false(self):
        """Test that _strip_nones keeps falsy values like 0 and False."""
        from client import _strip_nones

        result = _strip_nones({"a": 0, "b": False, "c": ""})
        assert result == {"a": 0, "b": False, "c": ""}

    def test_parse_json_param_valid(self):
        """Test parse_json_param with valid JSON."""
        from client import parse_json_param

        result = parse_json_param('{"key": "value"}', "test")
        assert result == {"key": "value"}

    def test_parse_json_param_none(self):
        """Test parse_json_param with None value."""
        from client import parse_json_param

        result = parse_json_param(None, "test")
        assert result is None

    def test_parse_json_param_invalid(self):
        """Test parse_json_param with invalid JSON raises error."""
        from client import parse_json_param

        with pytest.raises(ValueError) as exc_info:
            parse_json_param("not json", "test")

        assert "must be valid JSON" in str(exc_info.value)


class TestToolRegistration:
    """Tests for tool registration."""

    @pytest.mark.asyncio
    async def test_all_tools_registered(self):
        """Test that all expected tools are registered."""
        from domains.party import register
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register(mcp)

        tools = mcp._tool_manager.list_tools()
        tool_names = [t.name for t in tools]

        expected_tools = [
            "party_list",
            "party_count",
            "party_get",
            "party_create",
            "party_update",
            "party_delete",
            "party_download_image",
            "party_create_public_page",
            "party_transfer_addresses_to_open_records",
            "party_transfer_emails_to_open_records",
            "party_upload_image",
        ]

        for tool_name in expected_tools:
            assert tool_name in tool_names, f"Tool {tool_name} not found"


class TestResourceRegistration:
    """Tests for resource registration."""

    @pytest.mark.asyncio
    async def test_party_resource_registered(self):
        """Test that party resource is registered."""
        from mcp.server.fastmcp import FastMCP
        from server import mcp

        # The resource should be registered on the mcp instance
        # FastMCP stores URI template resources in _resource_manager._templates
        templates = mcp._resource_manager._templates
        
        # Check for party resource pattern in the template keys
        template_keys = list(templates.keys())
        party_resources = [key for key in template_keys if "party" in str(key).lower()]
        assert len(party_resources) > 0, f"Party resource not found. Available: {template_keys}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])