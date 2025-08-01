from __future__ import annotations

from textual.widgets import Static, Tree
from textual.widgets.tree import TreeNode
from textual.app import ComposeResult

from ..ros import RosClient, RosEntity
from ..ros.dependency_graph import RosDependencyGraph, RosDependencyNode


class RosEntityGraphPanel(Static):
    """ROSエンティティの依存関係をツリー表示するパネル"""

    def __init__(
        self,
        ros: RosClient,
        entity: RosEntity | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._ros = ros
        self._entity = entity
        self._tree = Tree("Dependency Graph")

    def compose(self) -> ComposeResult:
        yield self._tree

    def on_mount(self) -> None:
        if self._entity:
            self.update_graph()

    def set_entity(self, entity: RosEntity) -> None:
        if entity != self._entity:
            self._entity = entity
            self.update_graph()

    def update_graph(self) -> None:
        self._tree.clear()
        if self._entity is None:
            return

        graph = RosDependencyGraph(self._entity, self._ros)
        self._populate_tree(self._tree.root, graph.root)
        self._tree.root.expand()

    def _populate_tree(self, parent: TreeNode, dep_node: RosDependencyNode) -> None:
        for child in dep_node.children:
            label = f"{child.entity.name}"
            if child.children:
                child_node = parent.add(label)
                self._populate_tree(child_node, child)
            else:
                parent.add_leaf(label)
