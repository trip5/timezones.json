#!/usr/bin/env python3

import sys
import argparse
import json
import os
import glob
import natsort

ZONES_DIR = "/usr/share/zoneinfo/"

def zone_info_filter(zones):
    return [f for f in zones if (
        os.path.isfile(ZONES_DIR + f) and
        not os.path.islink(ZONES_DIR + f) and
        not f.startswith("right")
    )]

ZONES = glob.glob("*/**", root_dir=ZONES_DIR, recursive=True)
ZONES = zone_info_filter(ZONES)
ZONES = natsort.realsorted(ZONES)
ZONES.sort(key=lambda x: x.startswith("Etc/"))

def get_tz_string(timezone):
    data = open(ZONES_DIR + timezone, "rb").read().split(b"\n")[-2]
    return data.decode("utf-8")

def make_timezones_dict():
    result = {}
    for timezone in ZONES:
        timezone = timezone.strip()
        result[timezone] = get_tz_string(timezone)
    return result

def make_minimal_timezones_dict(timezones_dict, max_key_len=40):
    from collections import defaultdict
    region_groups = defaultdict(lambda: defaultdict(list))
    # Group by region and then by POSIX string
    for zone, posix in timezones_dict.items():
        if '/' not in zone:
            continue  # Skip entries like "UTC" or "GMT"
        region, name = zone.split('/', 1)
        region_groups[region][posix].append(name)
    result = {}
    for region, posix_map in region_groups.items():
        for posix, names in posix_map.items():
            if len(names) == 1:
                key = f"{region}/{names[0]}"
            else:
                merged = "-".join(names)
                max_name_len = max_key_len - len(region) - 1
                if len(merged) > max_name_len:
                    merged = merged[:max_name_len].rstrip('-')
                key = f"{region}/{merged}"
            result[key] = posix
    return result

def print_csv(timezones_dict):
    for name, tz in timezones_dict.items():
        print('"{}","{}"'.format(name, tz))

def print_json(timezones_dict):
    json.dump(timezones_dict, sys.stdout, indent=0, sort_keys=False, separators=(",", ":"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate POSIX timezones data")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--json", action="store_true", help="outputs JSON")
    group.add_argument("--csv", action="store_true", help="outputs CSV")
    group.add_argument("--minimal-json", action="store_true", help="outputs deduplicated minimal JSON")
    group.add_argument("--minimal-csv", action="store_true", help="outputs deduplicated minimal CSV")
    args = parser.parse_args()

    timezones = make_timezones_dict()

    if args.minimal_json or args.minimal_csv:
        timezones = make_minimal_timezones_dict(timezones)

    if args.json or args.minimal_json:
        print_json(timezones)
    elif args.csv or args.minimal_csv:
        print_csv(timezones)
