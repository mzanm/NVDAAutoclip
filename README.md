# NVDA Autoclip Add-on

The NVDA Autoclip add-on automatically reads out the contents of the clipboard whenever it changes. This can be useful if you play a game that output's text to the clipboard and has no support to output directly to NVDA. No external programs are needed to use this add-on

## Installation

Installation is the same to all other add-ons.

1. Download the latest release from the [releases page](https://github.com/mzanm/nvda-autoclip/releases).
2. Click on the download file while NVDA is running and the install add-on dialog should appear.

## Usage

Once the add-on is installed and enable via either the shortcut or the option in the tools menu, it will automatically read out the contents of the clipboard whenever it changes. Note that currently  that the add-on is activated temporarily until next restart of NVDA. The add-on doesn't save it's state in the configuration of NVDA:

- **Keyboard shortcut**: Press `NVDA+Control+Shift+K` to toggle automatic clipboard reading. The shortcut can be reassigned in the NVDA input gestures dialog normally like all other gestures.
- **Tools menu**: Open the NVDA tools menu and select "`Automatic clipboard reading`" to toggle it on or off.

By default, The add-on  will not interrupt before speaking the clipboard. If you want the add-on to always interrupt current speech before speaking the clipboard, you can change this setting in the add-on's settings panel in the NVDA settings dialog. This option is useful if you're playing a game that outputs text to the clipboard while NVDA is in sleep mode, which causes keyboard keys to not interrupt NVDA.

## Configuration

The add-on right now has one configuration option in the settings panel, which allows the user to configure whether the add-on should always interrupt current speech to speak the clipboard.
