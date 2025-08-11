# rtui2
[![PyPI - Version](https://img.shields.io/pypi/v/rtui2)](https://pypi.org/project/rtui2/)

TUI tool for ROS 2 Topic/Node debugging

![output](https://github.com/user-attachments/assets/576b9ecd-81cd-4b26-948c-65cea6ce49af)

## Support

- Python
  - 3.10+
- ROS 2
  - Humble
  - Jazzy
  - Kilted
- DDS Implementation
  - FastDDS Discovery Server mode supported
    - Compatible with centralized discovery architectures
    - Requires `ROS_DISCOVERY_SERVER` environment variable for discovery server endpoint
    - Automatically sets [`ROS_SUPER_CLIENT=true`](https://fast-dds.docs.eprosima.com/en/v2.14.5/fastdds/env_vars/env_vars.html?highlight=super_client#ros-super-client) for enhanced discovery capabilities

## Install

Via [pipx](https://github.com/pypa/pipx) (Recommended)

```sh-session
$ pipx install rtui2
```

Pip

```sh-session
$ pip3 install --user rtui2
```

## Demo

[demo](https://github.com/eduidl/rtui/assets/25898373/901f58a8-98f6-4f23-82d6-404d15d5f35b)

## Usage

```
Usage: rtui2 [OPTIONS] COMMAND [ARGS]...

  Terminal User Interface for ROS User

Options:
  --help  Show this message and exit.

Commands:
  action   Inspect ROS actions
  node     Inspect ROS nodes (default)
  service  Inspect ROS services
  topic    Inspect ROS topics
  type     Inspect ROS types
```

- node/topic/service/action/type
  - get a list of nodes, topics, or etc.
  - get an information about specific node, topic, or etc.
  - mouse operation
    - click link of a node, a topic, or etc.
  - keyboard operation
    - `b/f`: Trace history backward and forward
    - `r`: Once more get list of nodes, topics or etc.
    - `q`: Terminate app
- Set `ROS_DISCOVERY_SERVER` environment variable to enable discovery server mode
  - e.g. `export ROS_DISCOVERY_SERVER=127.0.0.1:11811`

## License

This project was developed by WHILL Inc. and is released under the Apache License, Version 2.0. See [NOTICE](./NOTICE) for details.

### Acknowledgements

This product is based on the "rtui" project (https://github.com/eduidl/rtui), which is licensed under the Apache License, Version 2.0.
