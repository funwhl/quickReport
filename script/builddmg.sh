#!/bin/sh
# Create a folder (named dmg) to prepare our DMG in (if it doesn't already exist).
mkdir -p dist/quickReport
# Empty the dmg folder.
rm -r dist/quickReport/*
# Copy the app bundle to the dmg folder.
cp -r "dist/quickReport.app" dist/quickReport
# If the DMG already exists, delete it.
test -f "dist/quickReport.dmg" && rm "dist/quickReport.dmg"
create-dmg \
  --volname "quickReport" \
  --volicon "haizhi.ico" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "quickReport.app" 175 120 \
  --hide-extension "quickReport.app" \
  --app-drop-link 425 120 \
  "dist/quickReport.dmg" \
  "dist/quickReport/"