# Key Listener

A utility to listen for key presses and execute commands via evdev. Works on both X11 and Wayland.

## Dependencies

- PySide6
- Kirigami
- python-qasync
- python-evdev

## Features

- Bind command to execute when a certain key is pressed / released.
- Group bindings with presets.
- Specify shell to execute commands in preset. For example, a preset using `adb shell` as shell executes commands on Android / WayDroid devices when a key is pressed / released on host.
