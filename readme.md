# NVDA Autoclip Add-on

Automatically reads clipboard text when it changes. Useful for games that output text to the clipboard without direct NVDA support. No external programs required.

[Changelog](https://github.com/mzanm/NVDAAutoclip/blob/main/changelog.md)
[Download latest version](https://github.com/mzanm/NVDAAutoclip/releases/latest/download/Autoclip.nvda-addon)

## Installation

**Compatibility:** NVDA 2021.1 or later

**Note:** The add-on is available in the NVDA add-on store (NVDA menu > tools > Add-on Store > Available add-ons tab) the following is a manual installation guide.

1. Download the latest release from the [releases page](https://github.com/mzanm/NVDAAutoclip/releases) or use the direct download link above
2. Open the downloaded file while NVDA is running to launch the install dialog

## Usage

Once installed, the add-on reads the clipboard text when it changes automatically when enabled. By default, it's activated temporarily until NVDA restarts. To persist the state across restarts and to use the add-on within a configuration profile, enable this option in the add-on settings.

### Enabling/Disabling

- **Keyboard shortcut**: `NVDA+Control+Shift+K` (customizable in NVDA Input Gestures dialog > Autoclip category)
- **Tools menu**: NVDA menu > Tools > "Automatic clipboard reading"

### Configuration

Access settings via NVDA Settings dialog > Autoclip category.

- **Interrupt before speaking the clipboard**: Whether to interrupt current speech first before reading out  a clipboard change
- **Remember automatic clipboard reading after NVDA restart**: Persist enabled/disabled state across restarts (required for configuration profiles)
- **Show in the NVDA tools menu**: Toggle visibility in the Tools menu

#### Advanced Settings

- **Split text above this length to segments spoken separately**: Maximum characters per segment to not overwhelm speech synthesizers when a large block of text is copied to the clipboard(default: 500, set below 100 to disable text splitting entirely)
- **Try to split segments at word boundaries**: When text splitting is enabled, split at spaces to avoid cutting words (default: enabled)
- **Maximum text length to speak**: Ignore clipboard updates exceeding this length (default: 15,000 characters)
- **Debounce delay**: Prevent repeating identical content within this delay in milliseconds (default: 100ms, 0 to disable, -1 for no duplicates ever)
- **Minimum delay between speech interrupts**: Minimum milliseconds between interruptions when interrupting is enabled (default: 50ms, 0 to always interrupt)
- **Restore Defaults**: Reset all advanced settings
