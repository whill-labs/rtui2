# rtui

[![PyPI - Version](https://img.shields.io/pypi/v/rtui2)](https://pypi.org/project/rtui2/)

TUI tool for ROS 2 Topic/Node debugging

## Support

- Python
  - 3.10+
- ROS2
  - Humble
  - Jazzy

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
Usage: rtui [OPTIONS] COMMAND [ARGS]...

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

## License

This project was developed by WHILL Inc. and is released under the Apache License, Version 2.0. See [NOTICE](./NOTICE) for details.

### Acknowledgements

This product is based on the "rtui" project (https://github.com/eduidl/rtui), which is licensed under the Apache License, Version 2.0.

