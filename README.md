
# timezones.json

Uses Github workflow to automatically update weekly (Sunday) when a new TZDB is available

* always up-to-date
* uses Natsort for naming
* combines Various timezones in regions into one entry in the `min` files
* outputs CSV and JSON
* compresses to gzip files

## Fetching

Fetched from various devices or apps using a URL such as:
- [https://github.com/trip5/timezones.json/releases/latest/download/timezones.csv](https://github.com/trip5/timezones.json/releases/latest/download/timezones.csv)

## Previews

- [Full Timezone List](timezones.md)
- [Minimal Timezone List](timezones.min.md)

## Inspiration

Credit to dmfilipenko for the original script: https://github.com/dmfilipenko/timezones.json

Credit to vshymanskyy for the update to use natsort: https://github.com/vshymanskyy/posix_tz_db

