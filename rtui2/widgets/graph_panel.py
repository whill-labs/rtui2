from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.events import Key
from textual.widgets import Static, Tree
from textual.widgets.tree import TreeNode

from ..ros import RosClient, RosEntity, RosEntityType
from ..ros.dependency_graph import RosDependencyGraph, RosDependencyNode

EXPANSION_DEPTH = 2


class TreeLabel:
    @staticmethod
    def label(entity: RosEntity) -> Text:
        style = ""
        if entity.type == RosEntityType.Node:
            style = "green"
        elif entity.type == RosEntityType.Topic:
            style = "white"
        return Text(entity.name, style=style)

    @staticmethod
    def leaf_label(entity: RosEntity) -> Text:
        text = TreeLabel.label(entity)
        text.stylize("bold underline")
        return text

    @staticmethod
    def error(msg: str) -> Text:
        return Text(f"ERROR: {msg}", style="red")

    NO_PUBLISHER = Text("[No publisher]", style="yellow")

    @staticmethod
    def is_no_publisher(label: str | Text) -> bool:
        plain = label.plain if isinstance(label, Text) else str(label)
        return plain.strip() == "No publisher"


class RosEntityGraphPanel(Static):
    """ROSエンティティの依存関係をツリー表示するパネル"""

    def __init__(
        self, ros: RosClient, entity: RosEntity | None = None, **kwargs
    ) -> None:
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

        self._tree = Tree(TreeLabel.label(self._entity), data=self._entity)
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
                label = TreeLabel.label(entity)
                child_node = parent.add(label, data=entity)
                self._populate_tree(child_node, child, depth + 1)
                if depth < EXPANSION_DEPTH - 1:
                    child_node.expand()
            else:
                if entity.type == RosEntityType.Topic:
                    topic_node = parent.add(TreeLabel.label(entity), data=entity)
                    topic_node.add_leaf(TreeLabel.NO_PUBLISHER)
                    if depth < EXPANSION_DEPTH - 1:
                        topic_node.expand()
                else:
                    parent.add_leaf(TreeLabel.leaf_label(entity), data=entity)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        node = event.node
        entity = node.data  # type: RosEntity | None

        if not isinstance(entity, RosEntity):
            return

        if entity.type != RosEntityType.Node:
            return

        if node.children and all(child.is_expanded for child in node.children):
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
            child
            for child in node.children
            if not TreeLabel.is_no_publisher(child.label)
        ]

        if not valid_children:
            return 0

        return 1 + max(self._subtree_depth(child) for child in valid_children)

    async def on_key(self, event: Key) -> None:
        if event.key == "space":
            selected_node = self._tree.cursor_node
            if selected_node is None or selected_node.parent is None:
                return

            siblings = selected_node.parent.children
            should_expand = not selected_node.is_expanded

            for sibling in siblings:
                if should_expand:
                    sibling.expand()
                else:
                    sibling.collapse()

            self.on_tree_node_selected(Tree.NodeSelected(selected_node))

            event.stop()
