# mixxx.log excerpt — clean --settings-path run 2026-07-19
# Full: /tmp/migx-settings-test/mixxx.log

10:59:16.389 Warning [Main] Failed to load "qt" translations for locale "en_IS" from "/Users/gudjon/code/migx/res/translations/"
10:59:16.390 Debug [Main] KeyboardEventFilter - "/Users/gudjon/code/migx/res/keyboard/is_IS.kbd.cfg"  not found, trying en_US.kbd.cfg
10:59:16.390 Warning [Main] KeyboardEventFilter - "/Users/gudjon/code/migx/res/en_US.kbd.cfg"  not found, starting without shortcuts
10:59:16.529 Debug [Main] Mixxx 2.7.0-alpha (git 022149dd46-modified (migx-harness); built on: Jul 17 2026 @ 16:38:32; flags: -pipe;-ffast-math;-funroll-loops;-O3;-fomit-frame-pointer;-fobjc-arc;-Wall;-Wextra;$<$<COMPILE_LANGUAGE:CXX>:-Woverloaded-virtual>;-Wfloat-conversion;-Werror=return-type;-Wformat=2;-Wformat-security;-Wvla;-Wundef;-fmacro-prefix-map=/Users/gudjon/code/migx=.) is starting...
10:59:16.576 Info [Main] CoreServices - Initializing or upgrading database schema
10:59:16.578 Info [Main] SettingsDAO - Failed to prepare query: Returning default value "" for "mixxx.schema.version"
10:59:16.578 Info [Main] SettingsDAO - Failed to prepare query: Returning default value "" for "mixxx.schema.last_used_version"
10:59:16.578 Info [Main] SettingsDAO - Failed to prepare query: Returning default value "" for "mixxx.schema.version"
10:59:16.578 Debug [Main] SchemaManager - Loading database schema migrations from ":/schema.xml"
10:59:16.578 Info [Main] SchemaManager - Upgrading database schema from version 0 to version 40
10:59:16.578 Info [Main] SchemaManager - Upgrading database schema to version 1 : "The base schema for the Mixxx SQLITE database."
10:59:16.579 Info [Main] SchemaManager - Upgraded database schema to version 1
10:59:16.579 Info [Main] SchemaManager - Upgrading database schema to version 2 : "Add a header_parsed integer column to the library to indicate when a\n      track's tags have been parsed."
10:59:16.579 Info [Main] SchemaManager - Upgraded database schema to version 2
10:59:16.579 Info [Main] SchemaManager - Upgrading database schema to version 3 : "Change the location column to be a an integer. Change comment to be\n      varchar(256) and album/artist/title to be varchar(64)."
10:59:16.580 Info [Main] SchemaManager - Upgraded database schema to version 3
10:59:16.580 Info [Main] SchemaManager - Upgrading database schema to version 4 : "Add file type column."
10:59:16.580 Info [Main] SchemaManager - Upgraded database schema to version 4
10:59:16.580 Info [Main] SchemaManager - Upgrading database schema to version 5 : "Add needs_verification column to library hashes table."
10:59:16.580 Info [Main] SchemaManager - Upgraded database schema to version 5
10:59:16.580 Info [Main] SchemaManager - Upgrading database schema to version 6 : "Added a ReplayGain Column."
10:59:16.581 Info [Main] SchemaManager - Upgraded database schema to version 6
10:59:16.581 Info [Main] SchemaManager - Upgrading database schema to version 7 : "Add timesplayed and rating column. Reset header state."
10:59:16.581 Info [Main] SchemaManager - Upgraded database schema to version 7
10:59:16.581 Info [Main] SchemaManager - Upgrading database schema to version 8 : "Added iTunes tables"
10:59:16.581 Info [Main] SchemaManager - Upgraded database schema to version 8
10:59:16.582 Info [Main] SchemaManager - Upgrading database schema to version 9 : "Tables for Traktor library feature"
10:59:16.582 Info [Main] SchemaManager - Upgraded database schema to version 9
10:59:16.582 Info [Main] SchemaManager - Upgrading database schema to version 10 : "Playlist and crate locks"
10:59:16.582 Info [Main] SchemaManager - Upgraded database schema to version 10
10:59:16.582 Info [Main] SchemaManager - Upgrading database schema to version 11 : "Tables for Rhythmbox library feature"
10:59:16.582 Info [Main] SchemaManager - Upgraded database schema to version 11
10:59:16.583 Info [Main] SchemaManager - Upgrading database schema to version 12 : "Add beats column to library table."
10:59:16.583 Info [Main] SchemaManager - Upgraded database schema to version 12
10:59:16.583 Info [Main] SchemaManager - Upgrading database schema to version 13 : "Add position column to Rhythmbox, iTunes, and Traktor playlist tables."
10:59:16.583 Info [Main] SchemaManager - Upgraded database schema to version 13
10:59:16.583 Info [Main] SchemaManager - Upgrading database schema to version 14 : "Add composer column to library table."
10:59:16.584 Info [Main] SchemaManager - Upgraded database schema to version 14
10:59:16.584 Info [Main] SchemaManager - Upgrading database schema to version 15 : "Add datetime_added to playlists tracks."
10:59:16.584 Info [Main] SchemaManager - Upgraded database schema to version 15
10:59:16.584 Info [Main] SchemaManager - Upgrading database schema to version 16 : "Add track analysis table."
10:59:16.584 Info [Main] SchemaManager - Upgraded database schema to version 16
10:59:16.584 Info [Main] SchemaManager - Upgrading database schema to version 17 : "Add columns for BPM lock and a sub-version string for beats."
10:59:16.585 Info [Main] SchemaManager - Upgraded database schema to version 17
10:59:16.585 Info [Main] SchemaManager - Upgrading database schema to version 18 : "Add keys column to library table."
10:59:16.585 Info [Main] SchemaManager - Upgraded database schema to version 18
10:59:16.585 Info [Main] SchemaManager - Upgrading database schema to version 19 : "Add key_id column to library table for caching the global key. Default to\n      INVALID."
10:59:16.585 Info [Main] SchemaManager - Upgraded database schema to version 19
10:59:16.585 Info [Main] SchemaManager - Upgrading database schema to version 20 : "Crates in AutoDJ queue (for automated random-track selection)."
10:59:16.586 Info [Main] SchemaManager - Upgraded database schema to version 20
