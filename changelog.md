# NVDAAutoclip changelog

## V1.3.2

- Updated translations

## V1.3.1

- Updated translations

## V1.3.0

- NVDA 2025.1 support
- Chinese translation by @Alan86024
- **Configurable Constants**: All hardcoded values are now configurable through settings:
    - Text segment size for splitting long clipboard text (default: 500 characters)
    - Maximum text length to speak (default: 15,000 characters)
    - Debounce delay to prevent duplicate speech (default: 100ms)
    - Interrupt delay between speech interruptions (default: 50ms)
    - Located in new "Advanced Settings" section with "Restore Defaults" button
- Added option to split long text at word boundaries for more natural speech flow instead of cutting mid-word

## V1.2.2

This version is mostly 1.2.1, but I forgot and called v1.2.1 v1.2.0, therefore this is a rerelease called v1.2.2 to clear up any possible confusion.

## V1.2.1

- Turkish translation by @babaprogramlar.

- Finnish translation by @jkinnunen.

- Updated the Vietnamese translation by nguyenninhhoang.

## V1.2.0

- NVDA 2024.1 support.

- fixed double speaking of the same text.

- added unassigned gesture to toggle interrupting speech before speaking the clipboard.

- You can now hide the option in the tools menu to toggle Autoclip. It can be found in the settings.

- When a large block of text is copied to the clipboard, it will be split into  500 character segments and be spoken separately to avoid causing issues with speech synthesizers.

- When the "always interrupt" option is enabled, rapid clipboard updates will no longer  interrupt speech.

- Improved performance.

## V1.1.0

- internal code optimizations to fix compatibility issue with DECTalk add-on and other bugs.

- Updated translations.

## V1.0.4

- Added Ukrainian translation by Heorhii.

## V1.0.3

- Added Vietnamese translation by nguyenninhhoang.

## V1.0.2

- the toggle Autoclip script is now in it's own category. The description has been also updated to include the name of the add-on so that it can be found when searching for it in the input gesture dialog.

- You can now toggle Autoclip, automatic clipboard reading in sleep mode

## V1.0.1

- the readme is included as add-on help.

## V1.0.0

- Initial release.
