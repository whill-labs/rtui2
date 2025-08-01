from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from .entity import RosEntity, RosEntityType
from .client import RosClient


@dataclass
class RosDependencyNode:
    entity: RosEntity
    children: list[RosDependencyNode] = field(default_factory=list)


class RosDependencyGraph:
    def __init__(self, root_entity: RosEntity, ros_client: RosClient) -> None:
        self._ros = ros_client
        self.root = self._build_graph(root_entity, visited=set())

    def _build_graph(
        self,
        entity: RosEntity,
        visited: set[str]
    ) -> RosDependencyNode:
        key = f"{entity.type}:{entity.name}"
        if key in visited:
            return RosDependencyNode(entity)

        visited.add(key)
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
                child_node = self._build_graph(topic_entity, visited)
                children.append(child_node)

        elif entity.type == RosEntityType.Topic:
            # Topic → Publisher Nodes
            for pub_info in info.publishers:
                pub_node_name = pub_info[0]
                node_entity = RosEntity.new_node(pub_node_name)
                child_node = self._build_graph(node_entity, visited)
                children.append(child_node)

        return RosDependencyNode(entity, children)
