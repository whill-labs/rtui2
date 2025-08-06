from __future__ import annotations

from dataclasses import dataclass, field

from .client import RosClient
from .entity import RosEntity, RosEntityType


@dataclass
class RosDependencyNode:
    entity: RosEntity
    children: list[RosDependencyNode] = field(default_factory=list)


class RosDependencyGraph:
    def __init__(
        self, root_entity: RosEntity, ros_client: RosClient, max_depth: int = 1
    ) -> None:
        self._ros = ros_client
        self._max_depth = max_depth
        self.root = self._build_graph(root_entity, depth=0)

    def _build_graph(
        self, entity: RosEntity, depth: int
    ) -> RosDependencyNode:
        if depth > self._max_depth:
            return RosDependencyNode(entity)

        children: list[RosDependencyNode] = []

        try:
            info = self._ros.get_entity_info(entity)
        except Exception:
            return RosDependencyNode(entity)

        if entity.type == RosEntityType.Node:
            # Node → Subscribed Topics
            for topic_name, _ in info.subscribers:
                if topic_name == "/parameter_events":
                    continue

                topic_entity = RosEntity.new_topic(topic_name)
                child_node = self._build_graph(topic_entity, depth + 1)
                children.append(child_node)

        elif entity.type == RosEntityType.Topic:
            # Topic → Publisher Nodes
            for pub_info in info.publishers:
                pub_node_name = pub_info[0]
                node_entity = RosEntity.new_node(pub_node_name)
                child_node = self._build_graph(node_entity, depth + 1)
                children.append(child_node)

        return RosDependencyNode(entity, children)
