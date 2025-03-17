# NVDA Autoclip Add-on

The NVDA Autoclip add-on automatically reads out the contents of the clipboard whenever it changes. This can be useful if you play a game that outputs text to the clipboard and has no support to output directly to NVDA. No external programs are needed to use this add-on.

[Changelog](https://github.com/mzanm/NVDAAutoclip/blob/main/changelog.md)
[Download latest version](https://github.com/mzanm/NVDAAutoclip/releases/latest/download/Autoclip.nvda-addon)

## Installation

**Compatibility:** Minimum compatible NVDA Version: 2019.3.

Installation is the same as for all other add-ons.

1. Download the latest release from the [releases page](https://github.com/mzanm/NVDAAutoclip/releases), or use the direct download link above.

2. While NVDA is running, open the downloaded file. The install add-on dialog should appear.

## Usage

Once the add-on is installed and enabled via either the shortcut or the option in the Tools menu, it will automatically read out the contents of the clipboard whenever it changes. Note that by default, the add-on is activated temporarily until the next restart of NVDA. The add-on doesn't save its state in the configuration of NVDA unless you change that behavior in the settings panel of the add-on.

- **Keyboard shortcut**: Press `NVDA+Control+Shift+K` to toggle automatic clipboard reading. The shortcut can be reassigned in the NVDA Input Gestures dialog like all other gestures. It can be found in the Autoclip category.

- **Tools menu**: Open the NVDA Tools menu and select "**Automatic clipboard reading**" to toggle it on or off.

By default, the add-on will not interrupt current speech before speaking the clipboard content. If you want the add-on to always interrupt current speech before speaking the clipboard, you can change this setting in the add-on's settings panel in the NVDA Settings dialog. This option is useful if you're playing a game that outputs text to the clipboard while NVDA is in sleep mode, which causes keyboard keys to not interrupt NVDA.

### Configuration

The add-on has several configuration options available in the settings panel:

- **Always Interrupt before speaking the clipboard**: Allows you to configure whether the add-on should always interrupt current speech to speak the clipboard content.

- **Remember automatic clipboard reading after NVDA restart**: Allows the add-on to remember whether it was enabled or disabled between NVDA restarts. This option must be enabled to be able to set up the add-on to run in a specific program using configuration profiles.

- **Show in the NVDA tools menu**: Disabling this option will remove the add-on's toggle from the tools menu. This is useful if you primarily use the keyboard shortcut to enable or disable the add-on and no longer require it to be accessible through the tools menu.

- **Try to split text at word boundaries**:

  - Enables splitting text at the nearest space to avoid cutting words in half.

  - **Default value**: Enabled.

#### Advanced Settings

- **Split characters above this length to segments spoken separately**:

  - Sets the maximum number of characters per segment when splitting long clipboard content.

  - **Default value**: `500` characters.

  - Set to a number under `100` to disable text splitting entirely.

- **Maximum text length to speak**:

  - Sets the maximum length of clipboard text to be spoken.

  - If the clipboard content exceeds this length, the add-on will silently ignore that clipboard update without speaking it.

  - **Default value**: `15,000` characters.

- **Debounce delay**:

  - Prevents the add-on from speaking the same clipboard content again within the specified delay.

  - Specified in milliseconds.

  - **Default value**: `100` milliseconds.

  - Set to `0` to disable.

- **Minimum delay between speech interrupts**:

  - Controls the minimum delay between speech interruptions when the add-on is set to interrupt current speech.

  - Specified in milliseconds.

  - **Default value**: `50` milliseconds.

  - Set to `0` to disable and always interrupt speech.

- **Restore Defaults**:

  - restores all advanced settings to their default values.
