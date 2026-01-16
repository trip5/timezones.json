#!/usr/bin/env python3
"""
Generate Home Assistant Clock Helper YAML files and index
"""
import csv
import os
import json
from pathlib import Path

def sanitize_filename(name):
    """Convert timezone name to safe filename"""
    # Remove region prefix (e.g., "Asia/")
    if '/' in name:
        name = name.split('/', 1)[1]
    # Replace slashes with hyphens
    name = name.replace('/', '-')
    return name

def get_region(tz_name):
    """Extract region from timezone name"""
    if '/' in tz_name:
        return tz_name.split('/')[0]
    return tz_name.split('-')[0]  # For Etc/GMT entries

def create_yaml_content(tz_name, posix_string, is_alternate=False):
    """Generate YAML content for a timezone helper"""
    entity_suffix = "alternate_timezone" if is_alternate else "timezone"
    message_suffix = "Alternate Set" if is_alternate else "Set"
    
    yaml = f'''alias: "Set Clock Helper {'Alternate ' if is_alternate else ''}Timezone to {tz_name}"
sequence:
  - service: input_text.set_value
    target:
      entity_id: input_text.clock_helper_{entity_suffix}
    data:
      value: "{posix_string}"
  - service: persistent_notification.create
    data:
      title: ✅ Timezone Updated
      message: "Clock Helper Timezone {message_suffix} to {tz_name}"
'''
    return yaml

def generate_ha_helpers(input_file, output_dir):
    """Generate all HA helper files and index"""
    
    # Read timezone data
    timezones = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 2:
                tz_name = row[0].strip('"')
                posix_string = row[1].strip('"')
                timezones.append((tz_name, posix_string))
    
    # Group by region
    regions = {}
    for tz_name, posix_string in timezones:
        region = get_region(tz_name)
        if region not in regions:
            regions[region] = []
        regions[region].append((tz_name, posix_string))
    
    # Create output directory
    base_dir = Path(output_dir)
    base_dir.mkdir(exist_ok=True)
    
    # Generate YAML files
    for region, tz_list in regions.items():
        region_dir = base_dir / region
        region_dir.mkdir(exist_ok=True)
        
        for tz_name, posix_string in tz_list:
            filename = sanitize_filename(tz_name)
            
            # Primary file
            primary_file = region_dir / f"{filename}.yaml"
            with open(primary_file, 'w', encoding='utf-8') as f:
                f.write(create_yaml_content(tz_name, posix_string, is_alternate=False))
            
            # Alternate file
            alternate_file = region_dir / f"{filename}-Alternate.yaml"
            with open(alternate_file, 'w', encoding='utf-8') as f:
                f.write(create_yaml_content(tz_name, posix_string, is_alternate=True))
    
    # Generate index.md
    index_path = base_dir / "index.md"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("## Helpers for Trip5's Clocks\n\n")
        f.write("### Set Your Primary Timezone\n\n")
        f.write("Click your timezone below to set the helper instantly:\n\n")
        
        # Sort regions alphabetically
        for region in sorted(regions.keys()):
            f.write(f"#### {region}\n\n")
            
            # Sort timezones within region
            for tz_name, posix_string in sorted(regions[region], key=lambda x: x[0]):
                filename = sanitize_filename(tz_name)
                display_name = filename  # Use the sanitized name for display
                
                base_url = "https://raw.githubusercontent.com/trip5/timezones.json/refs/heads/master/HA-clock-helper"
                primary_url = f"{base_url}/{region}/{filename}.yaml"
                alternate_url = f"{base_url}/{region}/{filename}-Alternate.yaml"
                
                primary_link = f"https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url={primary_url}"
                alternate_link = f"https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url={alternate_url}"
                
                f.write(f"- [{display_name}]({primary_link}) ({posix_string}) [Alternate]({alternate_link})\n")
            
            f.write("\n")
    
    print(f"Generated {len(timezones) * 2} YAML files and index.md in {output_dir}")
    print(f"Regions: {', '.join(sorted(regions.keys()))}")
    print(f"Total entries: {len(timezones)}")

if __name__ == "__main__":
    import sys
    
    input_file = "timezones.min.csv"
    output_dir = "HA-clock-helper"
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    generate_ha_helpers(input_file, output_dir)
