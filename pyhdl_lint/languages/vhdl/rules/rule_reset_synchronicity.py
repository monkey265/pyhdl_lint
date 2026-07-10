from typing import Dict, Set

from hdlConvertorAst.hdlAst import HdlContext, HdlModuleDec, HdlModuleDef, HdlStmProcess, HdlValueId

from pyhdl_lint.core.rule_base import AstRule, Severity

class ResetSynchronicityRule(AstRule):
    def __init__(self) -> None:
        super().__init__(
            id="VHDL-024",
            description="Reset name should reflect synchronicity ('a' prefix for asynchronous, e.g. 'areset_n' vs 'rst_n').",
            severity=Severity.WARNING,
        )

    def visit_HdlContext(self, context: HdlContext) -> HdlContext:
        # VHDL's entity (HdlModuleDec) and architecture (HdlModuleDef) are separate
        # top-level siblings - HdlModuleDef.dec is None, unlike Verilog's inline dec.
        # Correlate them by name: HdlModuleDef.module_name (HdlValueId) == entity name.
        async_signals_by_entity: Dict[str, Set[str]] = {}
        for obj in context.objs:
            if isinstance(obj, HdlModuleDef) and obj.module_name is not None:
                entity_name = str(obj.module_name).lower()
                signals = async_signals_by_entity.setdefault(entity_name, set())
                for stmt in obj.objs:
                    if isinstance(stmt, HdlStmProcess):
                        for s in (stmt.sensitivity or []):
                            if isinstance(s, HdlValueId):
                                signals.add(s.val.lower())

        for obj in context.objs:
            if isinstance(obj, HdlModuleDec):
                async_signals = async_signals_by_entity.get(obj.name.lower(), set())
                for port in obj.ports:
                    low_name = port.name.lower()
                    if "rst" not in low_name and "reset" not in low_name:
                        continue
                    is_named_async = low_name.startswith("a")
                    is_used_async = low_name in async_signals
                    if is_named_async and not is_used_async:
                        self.add_violation(
                            port,
                            f"Reset '{port.name}' is named as asynchronous ('a' prefix) but never appears in a process sensitivity list.",
                        )
                    elif not is_named_async and is_used_async:
                        self.add_violation(
                            port,
                            f"Reset '{port.name}' is used asynchronously (in a process sensitivity list) but its name doesn't reflect that (expected an 'a' prefix).",
                        )

        return super().visit_HdlContext(context)
