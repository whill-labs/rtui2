from __future__ import annotations

from textual.widgets import Static, Tree
from textual.widgets.tree import TreeNode
from textual.app import ComposeResult
from rich.text import Text

from ..ros import RosClient, RosEntity, RosEntityType
from ..ros.dependency_graph import RosDependencyGraph, RosDependencyNode

EXPANSION_DEPTH = 2


class TreeLabel:
    LEAF_NODE = lambda label: Text(label, style="green")
    NO_PUBLISHER = Text("[No publisher]", style="yellow")
    ERROR = lambda msg: Text(f"Error: {msg}", style="red")

    @staticmethod
    def is_placeholder_label(label: str | Text) -> bool:
        """[No publisher]のようなplaceholding leafを判定"""
        plain = label.plain if isinstance(label, Text) else str(label)
        return plain.strip() == "No publisher"


class RosEntityGraphPanel(Static):
    """ROSエンティティの依存関係をツリー表示するパネル"""

    def __init__(self, ros: RosClient, entity: RosEntity | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._ros = ros
        self._entity = entity
        self._tree: Tree[RosEntity] | None = None

    def compose(self) -> ComposeResult:
        if self._tree:
            yield self._tree

    def set_entity(self, entity: RosEntity) -> None:
        if entity != self._entity:
            self._entity = entity
            self.update_graph()

    def update_graph(self) -> None:
        if self._tree:
            self._tree.remove()

        if self._entity is None:
            return

        self._tree = Tree(self._entity.name, data=self._entity)
        self.mount(self._tree)

        graph = RosDependencyGraph(self._entity, self._ros, max_depth=EXPANSION_DEPTH)
        self._populate_tree(self._tree.root, graph.root)
        self._tree.root.expand()

    def _populate_tree(
        self,
        parent: TreeNode,
        dep_node: RosDependencyNode,
        depth: int = 0,
    ) -> None:
        for child in dep_node.children:
            entity = child.entity

            if child.children:
                # 再帰的に追加
                child_node = parent.add(entity.name, data=entity)
                self._populate_tree(child_node, child, depth + 1)
                if depth < EXPANSION_DEPTH - 1:
                    child_node.expand()
            else:
                if entity.type == RosEntityType.Topic:
                    topic_node = parent.add(entity.name, data=entity)
                    topic_node.add_leaf(TreeLabel.NO_PUBLISHER)
                    if depth < EXPANSION_DEPTH - 1:
                        topic_node.expand()
                else:
                    parent.add_leaf(TreeLabel.LEAF_NODE(entity.name), data=entity)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        node = event.node
        entity = node.data  # type: RosEntity | None

        if not isinstance(entity, RosEntity):
            return

        if entity.type != RosEntityType.Node:
            return

        if self._subtree_depth(node) > EXPANSION_DEPTH:
            return

        try:
            node._children.clear()
            node._expanded = False

            graph = RosDependencyGraph(entity, self._ros, max_depth=EXPANSION_DEPTH)
            self._populate_tree(node, graph.root)
            node.expand()
        except Exception as e:
            node.add_leaf(TreeLabel.ERROR(str(e)))

    def _subtree_depth(self, node: TreeNode) -> int:
        if not node.children:
            return 0

        valid_children = [
            child for child in node.children
            if not TreeLabel.is_placeholder_label(child.label)
        ]

        if not valid_children:
            return 0

        return 1 + max(self._subtree_depth(child) for child in valid_children)
