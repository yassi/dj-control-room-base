from django.test import TestCase

from dj_control_room_base.core.panel_tool import (
    PanelTool,
    PanelToolContext,
    PanelToolResult,
    ToolRegistry,
)


def _schema():
    return {"type": "object", "properties": {}}


class TestToolRegistryRegister(TestCase):
    def test_decorator_returns_the_function_unchanged(self):
        registry = ToolRegistry()

        @registry.register(
            name="do_thing", scope="read", description="desc", input_schema=_schema()
        )
        def handler(ctx):
            return "called"

        self.assertTrue(callable(handler))
        self.assertEqual(handler(None), "called")

    def test_registered_tool_appears_in_tools(self):
        registry = ToolRegistry()

        @registry.register(
            name="do_thing", scope="read", description="desc", input_schema=_schema()
        )
        def handler(ctx):
            pass

        self.assertEqual(len(registry.tools), 1)
        tool = registry.tools[0]
        self.assertIsInstance(tool, PanelTool)
        self.assertEqual(tool.name, "do_thing")
        self.assertEqual(tool.scope, "read")
        self.assertEqual(tool.description, "desc")
        self.assertEqual(tool.input_schema, _schema())

    def test_tool_handler_is_the_decorated_function(self):
        registry = ToolRegistry()

        @registry.register(
            name="do_thing", scope="read", description="desc", input_schema=_schema()
        )
        def handler(ctx):
            pass

        self.assertIs(registry.tools[0].handler, handler)

    def test_multiple_registrations_preserve_order(self):
        registry = ToolRegistry()

        @registry.register(
            name="alpha", scope="s", description="d", input_schema=_schema()
        )
        def handler_alpha(ctx):
            pass

        @registry.register(
            name="beta", scope="s", description="d", input_schema=_schema()
        )
        def handler_beta(ctx):
            pass

        self.assertEqual([t.name for t in registry.tools], ["alpha", "beta"])

    def test_duplicate_name_raises(self):
        registry = ToolRegistry()

        @registry.register(
            name="dup", scope="s", description="d", input_schema=_schema()
        )
        def handler_one(ctx):
            pass

        with self.assertRaises(ValueError):

            @registry.register(
                name="dup", scope="s", description="d", input_schema=_schema()
            )
            def handler_two(ctx):
                pass

    def test_duplicate_name_does_not_register_second_handler(self):
        registry = ToolRegistry()

        @registry.register(
            name="dup", scope="s", description="d", input_schema=_schema()
        )
        def handler_one(ctx):
            pass

        try:

            @registry.register(
                name="dup", scope="s", description="d", input_schema=_schema()
            )
            def handler_two(ctx):
                pass

        except ValueError:
            pass

        self.assertEqual(len(registry.tools), 1)
        self.assertIs(registry.tools[0].handler, handler_one)

    def test_tools_property_returns_a_copy(self):
        """Mutating the returned list must not affect the registry's internal state."""
        registry = ToolRegistry()

        @registry.register(
            name="alpha", scope="s", description="d", input_schema=_schema()
        )
        def handler(ctx):
            pass

        snapshot = registry.tools
        snapshot.append("not a real tool")
        self.assertEqual(len(registry.tools), 1)

    def test_empty_registry_has_no_tools(self):
        registry = ToolRegistry()
        self.assertEqual(registry.tools, [])
        self.assertEqual(len(registry), 0)

    def test_len_reflects_registered_count(self):
        registry = ToolRegistry()

        @registry.register(
            name="alpha", scope="s", description="d", input_schema=_schema()
        )
        def handler(ctx):
            pass

        self.assertEqual(len(registry), 1)

    def test_iteration_yields_tools_in_order(self):
        registry = ToolRegistry()

        @registry.register(
            name="alpha", scope="s", description="d", input_schema=_schema()
        )
        def handler_alpha(ctx):
            pass

        @registry.register(
            name="beta", scope="s", description="d", input_schema=_schema()
        )
        def handler_beta(ctx):
            pass

        self.assertEqual([t.name for t in registry], ["alpha", "beta"])

    def test_separate_registries_do_not_share_state(self):
        registry_a = ToolRegistry()
        registry_b = ToolRegistry()

        @registry_a.register(
            name="only_in_a", scope="s", description="d", input_schema=_schema()
        )
        def handler(ctx):
            pass

        self.assertEqual(len(registry_a.tools), 1)
        self.assertEqual(len(registry_b.tools), 0)


class TestToolRegistryIntegrationWithPanelToolTypes(TestCase):
    """Sanity check that registry-produced tools behave like manually-built ones."""

    def test_handler_invocation_via_context(self):
        registry = ToolRegistry()

        @registry.register(
            name="echo",
            scope="read",
            description="Echoes input",
            input_schema=_schema(),
        )
        def handle_echo(ctx: PanelToolContext) -> PanelToolResult:
            return PanelToolResult(success=True, message="ok", data=ctx.inputs)

        tool = registry.tools[0]
        ctx = PanelToolContext(user=None, inputs={"x": 1}, config=None)
        result = tool.handler(ctx)

        self.assertTrue(result.success)
        self.assertEqual(result.data, {"x": 1})
