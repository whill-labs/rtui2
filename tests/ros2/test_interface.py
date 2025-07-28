from __future__ import annotations

import typing as t
import unittest
import warnings

import rclpy

from rtui2.ros.interface.ros2 import Ros2

from .node.dummy_node1 import DummyNode1
from .node.dummy_node2 import DummyNode2


def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            test_func(self, *args, **kwargs)

    return do_test


class TestRos2Interface(unittest.TestCase):
    NODE1: t.ClassVar[DummyNode1 | None] = None
    NODE2: t.ClassVar[DummyNode2 | None] = None

    @classmethod
    def setUpClass(cls) -> None:
        # Initialize rclpy first, then create all nodes
        if not rclpy.ok():
            rclpy.init()

        cls.ROS = Ros2()
        cls.NODE1 = DummyNode1()
        cls.NODE2 = DummyNode2()

        rate = cls.ROS.node.create_rate(3)
        rate.sleep()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.ROS.terminate()

    def test_get_node_publisher(self):
        publishers = self.ROS.get_node_publishers("/dummy_node1")
        self.assertIn(("/topic", "std_msgs/msg/String"), publishers)
        self.assertIn(("/pub", "std_msgs/msg/Int32"), publishers)

    def test_get_node_subscribers(self):
        subscribers = self.ROS.get_node_subscribers("/dummy_node1")
        self.assertIn(("/sub", "sensor_msgs/msg/Image"), subscribers)

    def test_get_node_service_servers(self):
        servers = self.ROS.get_node_service_servers("/dummy_node1")
        self.assertIn(("/service", "std_srvs/srv/SetBool"), servers)

    def test_get_node_service_clients(self):
        self.assertEqual(
            self.ROS.get_node_service_clients("/dummy_node1"),
            [("/client", "std_srvs/srv/Empty")],
        )

    def test_get_node_action_servers(self):
        self.assertEqual(
            self.ROS.get_node_action_servers("/dummy_node1"),
            [("/action", "tf2_msgs/action/LookupTransform")],
        )

    def test_get_node_action_clients(self):
        clients = self.ROS.get_node_action_clients("/dummy_node1")
        self.assertIn(("/action_client", "tf2_msgs/action/LookupTransform"), clients)

    def test_get_topic_types(self):
        types = self.ROS.get_topic_types("/topic")
        self.assertEqual(types, ["std_msgs/msg/String"])

    def test_get_topic_publishers(self):
        # Debug: Check what topics and nodes are available
        topics = self.ROS.list_topics()
        nodes = self.ROS.list_nodes()
        print(f"Available topics: {topics}")
        print(f"Available nodes: {nodes}")

        # Debug: Check node publishers info
        node1_pubs = self.ROS.get_node_publishers("/dummy_node1")
        print(f"Node1 publishers: {node1_pubs}")

        publishers = self.ROS.get_topic_publishers("/topic")
        print(f"Publishers for /topic: {publishers}")

        # Check that we have the expected publisher (node, type, qos)
        self.assertEqual(len(publishers), 1)
        self.assertEqual(publishers[0][0], "/dummy_node1")
        self.assertEqual(publishers[0][1], "std_msgs/msg/String")
        # Third element should be QoS profile string
        self.assertIn("qos_profile:", publishers[0][2])
        self.assertIn("reliability:", publishers[0][2])
        self.assertIn("durability:", publishers[0][2])

    def test_get_topic_subscribers(self):
        subscribers = self.ROS.get_topic_subscribers("/topic")
        # Check that we have the expected subscriber (node, type, qos)
        self.assertEqual(len(subscribers), 1)
        self.assertEqual(subscribers[0][0], "/dummy_node2")
        self.assertEqual(subscribers[0][1], "std_msgs/msg/String")
        # Third element should be QoS profile string
        self.assertIn("qos_profile:", subscribers[0][2])
        self.assertIn("reliability:", subscribers[0][2])
        self.assertIn("durability:", subscribers[0][2])

    def test_get_service_types(self):
        self.assertEqual(
            self.ROS.get_service_types("/service"), ["std_srvs/srv/SetBool"]
        )

    def test_get_service_servers(self):
        # Not supported
        self.assertIsNone(self.ROS.get_service_servers("/service"))

    def test_get_action_types(self):
        self.assertEqual(
            self.ROS.get_action_types("/action"), ["tf2_msgs/action/LookupTransform"]
        )

    def test_get_action_servers(self):
        self.assertEqual(
            self.ROS.get_action_servers("/action"),
            [("/dummy_node1", "tf2_msgs/action/LookupTransform")],
        )

    def test_get_action_clients(self):
        self.assertEqual(
            self.ROS.get_action_clients("/action"),
            [("/dummy_node2", "tf2_msgs/action/LookupTransform")],
        )

    def test_list_nodes(self):
        nodes = self.ROS.list_nodes()
        self.assertIn("/dummy_node1", nodes)
        self.assertIn("/dummy_node2", nodes)
        self.assertNotIn("/_rtui", nodes)

    def test_list_topics(self):
        topics = self.ROS.list_topics()
        self.assertIn("/topic", topics)
        self.assertIn("/pub", topics)
        self.assertIn("/sub", topics)

    def test_list_services(self):
        services = self.ROS.list_services()
        self.assertIn("/service", services)
        self.assertIn("/client", services)

    def test_list_actions(self):
        actions = self.ROS.list_actions()
        self.assertIn("/action", actions)
        self.assertIn("/action_client", actions)


if __name__ == "__main__":
    unittest.main()
