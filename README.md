
# timezones.json

Generates POSIX timezones strings reading data from `/usr/share/zoneinfo`

Uses Github workflow to automatically update weekly (Sunday) when a new TZDB is available

* always up-to-date
* uses Natsort for naming
* combines Various timezones in regions into one entry in the `min` files
* outputs CSV and JSON
* compresses to gzip files

Credit to vshymanskyy for the original script: https://github.com/vshymanskyy/posix_tz_db

