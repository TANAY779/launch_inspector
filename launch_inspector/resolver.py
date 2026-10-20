"""Launch resolver engine for ROS 2 static dry-run analysis."""

from __future__ import annotations

import importlib.util
import os
import pathlib
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

import launch
from launch import LaunchContext, LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    GroupAction,
    IncludeLaunchDescription,
    OpaqueFunction,
    SetLaunchConfiguration,
)
from launch.substitutions import LaunchConfiguration
from launch.utilities import normalize_to_list_of_substitutions, perform_substitutions
import launch_ros
from launch_ros.actions import (
    ComposableNodeContainer,
    Node,
    PushRosNamespace,
    SetParameter,
    SetRemap,
)
from launch_ros.descriptions import ComposableNode
from launch_ros.utilities import evaluate_parameters

from launch_inspector.models import (
    DiagnosticFinding,
    EndpointDirection,
    LaunchSystemModel,
    QoSProfile,
    ReliabilityPolicy,
    ResolvedNode,
    Severity,
    TopicEndpoint,
)
from launch_inspector.stubs.library import get_standard_stubs


class LaunchResolver:
    """Safely resolves ROS 2 launch files without starting OS processes."""

    def __init__(
        self,
        launch_path: Optional[str] = None,
        launch_description: Optional[LaunchDescription] = None,
        launch_arguments: Optional[Dict[str, str]] = None,
    ):
        self.launch_path = os.path.abspath(launch_path) if launch_path else None
        self.launch_description = launch_description
        self.launch_arguments = launch_arguments or {}
        self.context = LaunchContext()

    def resolve(self) -> LaunchSystemModel:
        model = LaunchSystemModel(
            launch_path=self.launch_path,
            arguments=dict(self.launch_arguments),
        )

        # 1. Pre-seed launch arguments in context
        for key, val in self.launch_arguments.items():
            self.context.launch_configurations[key] = str(val)

        # 2. Load launch description if file provided
        ld = self.launch_description
        if ld is None and self.launch_path:
            ld = self._load_launch_description(self.launch_path, model)

        if ld is None:
            model.diagnostics.append(
                DiagnosticFinding(
                    rule_id="LAUNCH-001",
                    severity=Severity.ERROR,
                    message=f"Failed to load launch description from {self.launch_path}",
                )
            )
            return model

        # 3. First pass: declare all arguments so defaults are known
        self._collect_declared_arguments(ld.entities)

        # 4. Second pass: visit all actions
        for entity in ld.entities:
            self._visit_entity(entity, model, active_condition=True)

        return model

    def _load_launch_description(
        self, path: str, model: LaunchSystemModel
    ) -> Optional[LaunchDescription]:
        if not os.path.exists(path):
            model.diagnostics.append(
                DiagnosticFinding(
                    rule_id="FILE-001",
                    severity=Severity.ERROR,
                    message=f"Launch file not found: {path}",
                )
            )
            return None

        if path.endswith(".py"):
            try:
                module_name = f"launch_module_{os.path.basename(path).replace('.', '_')}"
                spec = importlib.util.spec_from_file_location(module_name, path)
                if spec is None or spec.loader is None:
                    return None
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

                if hasattr(module, "generate_launch_description"):
                    return module.generate_launch_description()
                else:
                    model.diagnostics.append(
                        DiagnosticFinding(
                            rule_id="LAUNCH-002",
                            severity=Severity.ERROR,
                            message=f"Launch file missing 'generate_launch_description()': {path}",
                        )
                    )
                    return None
            except Exception as e:
                model.diagnostics.append(
                    DiagnosticFinding(
                        rule_id="PYTHON-001",
                        severity=Severity.ERROR,
                        message=f"Error evaluating Python launch file {path}: {e}",
                    )
                )
                return None
        else:
            # XML or YAML launch file
            try:
                from launch.launch_description_sources import AnyLaunchDescriptionSource

                source = AnyLaunchDescriptionSource(path)
                return source.get_launch_description(self.context)
            except Exception as e:
                model.diagnostics.append(
                    DiagnosticFinding(
                        rule_id="PARSE-001",
                        severity=Severity.ERROR,
                        message=f"Error parsing launch file {path}: {e}",
                    )
                )
                return None

    def _collect_declared_arguments(self, entities: List[Any]) -> None:
        """Scan declared launch arguments and populate context with defaults if not supplied."""
        for entity in entities:
            if isinstance(entity, DeclareLaunchArgument):
                arg_name = entity.name
                if arg_name not in self.context.launch_configurations:
                    if entity.default_value is not None:
                        val = perform_substitutions(
                            self.context,
                            normalize_to_list_of_substitutions(entity.default_value),
                        )
                        self.context.launch_configurations[arg_name] = val
            elif isinstance(entity, GroupAction):
                self._collect_declared_arguments(entity.get_sub_entities())

    def _evaluate_condition(self, condition: Any) -> bool:
        if condition is None:
            return True
        try:
            return bool(condition.evaluate(self.context))
        except Exception:
            # If substitution cannot be resolved yet, assume True for static safety
            return True

    def _visit_entity(
        self, entity: Any, model: LaunchSystemModel, active_condition: bool = True
    ) -> None:
        # Check condition on entity
        cond = getattr(entity, "condition", None)
        entity_active = active_condition and self._evaluate_condition(cond)

        if isinstance(entity, Node):
            self._handle_node(entity, model, active=entity_active)

        elif isinstance(entity, GroupAction):
            sub_entities = entity.get_sub_entities()
            for sub in sub_entities:
                self._visit_entity(sub, model, active_condition=entity_active)

        elif isinstance(entity, IncludeLaunchDescription):
            if entity_active:
                try:
                    generated_actions = entity.execute(self.context)
                    for act in generated_actions:
                        self._visit_entity(act, model, active_condition=True)
                except Exception as e:
                    model.unresolved_items.append(
                        f"IncludeLaunchDescription failed: {e}"
                    )

        elif isinstance(entity, OpaqueFunction):
            if entity_active:
                try:
                    generated_actions = entity.execute(self.context)
                    if generated_actions:
                        for act in generated_actions:
                            self._visit_entity(act, model, active_condition=True)
                except Exception as e:
                    model.unresolved_items.append(f"OpaqueFunction failed: {e}")

        elif isinstance(entity, LaunchDescription):
            for sub in entity.entities:
                self._visit_entity(sub, model, active_condition=entity_active)

        elif hasattr(entity, "execute"):
            # Non-process spawning actions (e.g. SetParameter, SetRemap, PushRosNamespace)
            # execute safely in context
            if entity_active and not isinstance(entity, ExecuteProcess):
                try:
                    entity.execute(self.context)
                except Exception:
                    pass

    def _handle_node(self, node: Node, model: LaunchSystemModel, active: bool) -> None:
        try:
            node._perform_substitutions(self.context)
        except Exception as e:
            model.unresolved_items.append(f"Node substitution expansion failed: {e}")
            return

        # Extract name and namespace
        node_name = node.node_name or "unnamed_node"
        if "<node_name_unspecified>" in node_name:
            # Fallback to executable name
            node_name = self._resolve_raw_str(getattr(node, "_Node__node_executable", "node"))
        
        # Strip any unspecified marker in namespace
        ns = node.expanded_node_namespace or ""
        if "<node_namespace_unspecified>" in ns:
            ns = ""
        ns = ns.strip("/")

        # Clean node name if namespace was prepended
        if "/" in node_name:
            node_name = node_name.rstrip("/").split("/")[-1]

        pkg = self._resolve_raw_str(getattr(node, "_Node__package", None))
        exe = self._resolve_raw_str(getattr(node, "_Node__node_executable", None))

        # Extract remappings
        remappings: List[Tuple[str, str]] = []
        raw_remaps = getattr(node, "_Node__expanded_remappings", None) or []
        for src, dst in raw_remaps:
            remappings.append((str(src), str(dst)))

        # Extract and evaluate parameters
        parameters: Dict[str, Any] = {}
        raw_params = getattr(node, "_Node__parameters", None)
        if raw_params is not None:
            try:
                evaluated_params = evaluate_parameters(self.context, raw_params)
                for item in evaluated_params:
                    if isinstance(item, dict):
                        parameters.update(item)
                    elif isinstance(item, pathlib.Path) or isinstance(item, str):
                        # Load YAML parameter file
                        param_path = str(item)
                        if os.path.isfile(param_path):
                            loaded = self._parse_yaml_parameters(param_path, node_name, ns)
                            parameters.update(loaded)
            except Exception as e:
                model.unresolved_items.append(f"Param evaluation for {node_name} error: {e}")

        # Global parameters in context
        global_params = self.context.launch_configurations.get("global_params", [])
        if global_params:
            for g_item in global_params:
                if isinstance(g_item, tuple):
                    g_name, g_val = g_item
                    parameters.setdefault(str(g_name), g_val)

        is_lifecycle = getattr(node, "_Node__is_lifecycle_node", False) or "LifecycleNode" in type(node).__name__

        resolved_node = ResolvedNode(
            name=node_name,
            namespace=ns,
            package=pkg,
            executable=exe,
            parameters=parameters,
            remappings=remappings,
            is_lifecycle=is_lifecycle,
            condition_active=active,
        )

        # Attach topic endpoints from stubs and apply remappings
        self._populate_endpoints(resolved_node, pkg, exe, remappings)

        if active:
            model.nodes.append(resolved_node)
        else:
            model.skipped_nodes.append(resolved_node)

        # If it's a ComposableNodeContainer, process its composable nodes
        if isinstance(node, ComposableNodeContainer):
            composable_descriptions = getattr(
                node, "_ComposableNodeContainer__composable_node_descriptions", []
            )
            for c_desc in composable_descriptions:
                if isinstance(c_desc, ComposableNode):
                    self._handle_composable_node(c_desc, ns, model, active)

    def _handle_composable_node(
        self, c_desc: ComposableNode, parent_ns: str, model: LaunchSystemModel, active: bool
    ) -> None:
        try:
            name = perform_substitutions(self.context, normalize_to_list_of_substitutions(c_desc.node_name))
        except Exception:
            name = "composable_node"

        try:
            sub_ns = perform_substitutions(self.context, normalize_to_list_of_substitutions(c_desc.node_namespace or ""))
        except Exception:
            sub_ns = ""

        full_ns = f"{parent_ns}/{sub_ns}".strip("/")
        pkg = self._resolve_raw_str(c_desc.package)
        plugin = self._resolve_raw_str(c_desc.plugin)

        remappings: List[Tuple[str, str]] = []
        if c_desc.remappings:
            for src, dst in c_desc.remappings:
                s_str = perform_substitutions(self.context, normalize_to_list_of_substitutions(src))
                d_str = perform_substitutions(self.context, normalize_to_list_of_substitutions(dst))
                remappings.append((s_str, d_str))

        parameters: Dict[str, Any] = {}
        if c_desc.parameters:
            try:
                evaluated_params = evaluate_parameters(self.context, c_desc.parameters)
                for item in evaluated_params:
                    if isinstance(item, dict):
                        parameters.update(item)
                    elif isinstance(item, (pathlib.Path, str)) and os.path.isfile(str(item)):
                        parameters.update(self._parse_yaml_parameters(str(item), name, full_ns))
            except Exception:
                pass

        resolved_node = ResolvedNode(
            name=name,
            namespace=full_ns,
            package=pkg,
            executable=plugin,
            parameters=parameters,
            remappings=remappings,
            is_lifecycle=False,
            condition_active=active,
        )

        self._populate_endpoints(resolved_node, pkg, plugin, remappings)

        if active:
            model.nodes.append(resolved_node)
        else:
            model.skipped_nodes.append(resolved_node)

    def _populate_endpoints(
        self,
        node: ResolvedNode,
        package: Optional[str],
        executable: Optional[str],
        remappings: List[Tuple[str, str]],
    ) -> None:
        remap_dict = {src: dst for src, dst in remappings}

        # 1. From stubs
        if package and executable:
            stubs = get_standard_stubs(package, executable)
            for topic_name, direction, msg_type, qos in stubs:
                final_topic = self._resolve_topic_name(topic_name, node.namespace, remap_dict)
                node.endpoints.append(
                    TopicEndpoint(
                        topic=final_topic,
                        node_full_name=node.full_name,
                        direction=direction,
                        message_type=msg_type,
                        qos=qos,
                        original_name=topic_name,
                    )
                )

        # 2. Add endpoints for explicit remappings not in stubs
        for src, dst in remappings:
            already_covered = any(ep.original_name == src for ep in node.endpoints)
            if not already_covered:
                final_topic = dst if dst.startswith("/") else f"/{node.namespace}/{dst}".replace("//", "/")
                # Create a generic endpoint
                node.endpoints.append(
                    TopicEndpoint(
                        topic=final_topic,
                        node_full_name=node.full_name,
                        direction=EndpointDirection.SUBSCRIBER,  # default assumed
                        message_type=None,
                        original_name=src,
                    )
                )

    def _resolve_topic_name(
        self, topic_template: str, namespace: str, remap_dict: Dict[str, str]
    ) -> str:
        # Check remapping first
        if topic_template in remap_dict:
            target = remap_dict[topic_template]
            if target.startswith("/"):
                return target
            return f"/{namespace}/{target}".replace("//", "/")

        if topic_template.startswith("/"):
            return topic_template

        ns = namespace.strip("/")
        if not ns:
            return f"/{topic_template}"
        return f"/{ns}/{topic_template}"

    def _parse_yaml_parameters(
        self, file_path: str, node_name: str, namespace: str
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if not isinstance(data, dict):
                return params

            # Check wildcard /**
            if "/**" in data and isinstance(data["/**"], dict):
                params.update(data["/**"].get("ros__parameters", {}))

            # Check node full path or relative name
            candidates = [
                f"/{node_name}",
                f"/{namespace}/{node_name}" if namespace else None,
                node_name,
            ]
            for cand in candidates:
                if cand and cand in data and isinstance(data[cand], dict):
                    params.update(data[cand].get("ros__parameters", {}))
        except Exception:
            pass
        return params

    def _resolve_raw_str(self, val: Any) -> Optional[str]:
        if val is None:
            return None
        if isinstance(val, str):
            return val
        try:
            return perform_substitutions(
                self.context, normalize_to_list_of_substitutions(val)
            )
        except Exception:
            return str(val)
