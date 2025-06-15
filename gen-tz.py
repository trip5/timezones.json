#!/usr/bin/env python

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
    grouped = {}
    for zone, posix in timezones_dict.items():
        grouped.setdefault(posix, []).append(zone)
    result = {}
    for posix, zones in grouped.items():
        if len(zones) == 1:
            result[zones[0]] = posix
        else:
            # Group by shared region prefix
            regions = [z.split('/', 1) for z in zones if '/' in z]
            if not regions:
                continue
            region = regions[0][0]
            names = [r[1] for r in regions if r[0] == region]
            combined = f"{region}/{'-'.join(names)}"
            if len(combined) > max_key_len:
                combined = combined[:max_key_len].rstrip('-')
            result[combined] = posix
    return result

def print_csv(timezones_dict):
    for name, tz in timezones_dict.items():
        print('"{}","{}"'.format(name, tz))


def print_json(timezones_dict):
    json.dump(timezones_dict, sys.stdout, indent=0, sort_keys=False, separators=(",", ":"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generates POSIX timezones strings reading data from " + ZONES_DIR)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-j", "--json", action="store_true", help="outputs JSON")
    group.add_argument("-c", "--csv", action="store_true", help="outputs CSV")
    group.add_argument("-mj", "--minimal_json", action="store_true", help="outputs minimal de-duplicated JSON")
    group.add_argument("-mc", "--minimal_csv", action="store_true", help="outputs minimal de-duplicated CSV")
    data = parser.parse_args()

    timezones = make_timezones_dict()

    if args.minimal_json or args.minimal_csv:
        timezones = make_minimal_timezones_dict(timezones)

    if args.json or args.minimal_json:
        print_json(timezones)
    elif args.csv or args.minimal_csv:
        print_csv(timezones)
