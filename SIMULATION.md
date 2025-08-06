# RAE.IO Simulation & Bug Check Guide

## Simulation Steps
1. Switch between every mode, especially in/out of Fuckery and Training.
2. Upload, generate, and query in every mode; test file handling and plugin routing.
3. Attempt to access encrypted data without the key (should fail).
4. Test plugin reloads and agent retraining.
5. Install on all 4 platforms; verify font and color theming.

## Bugs Found/Fixes
- Mode switching cleans up old keys.
- All encrypted blobs are never written unencrypted, even if user toggles out of Fuckery.
- Font fallback in UI for non-Windows systems.
- Exception handling for plugin failures and data ingestion.
- Consistent deep purple button behavior on all platforms.