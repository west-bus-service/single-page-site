# single-page-site

This repository is based on the 2024 version of the West's Transportation website, made accessible for the managers of the service

## How to change the cancellation message

Open the repository:

[https://github.com/west-bus-service/single-page-site](https://github.com/west-bus-service/single-page-site)

Click on `cancellation_message.html`

Click on the pencil icon :pencil:

Edit the message as necessary. To remove the message, delete all of the text in
the file.

Click the green `Commit changes...` button. In the popup, leave all of the default options and click `Commit changes` to continue.

Wait a few minutes for the page to update. If this doesn't work, contact Max

## How to edit the schedule data (GTFS)

The routes, stops, times and fares shown on [/newhomepage/](https://westbusservice.com/newhomepage/) come from `west_gtfs.zip`.

1. Open the feed in the editor: [edit.gtfs.zone](https://edit.gtfs.zone/#load=https://raw.githubusercontent.com/west-bus-service/single-page-site/main/west_gtfs.zip)
2. Make changes, then export the feed as a ZIP
3. On GitHub, upload the exported file as `west_gtfs.zip`, replacing the existing one

Fares use GTFS Fares v2. Fares that change on a date are split by `timeframes.txt`, each tied to a calendar entry (`FARES_2026`, `FARES_2027`) that sets the dates the fare applies.

## Printable brochure

`pnpm build` also prints a trifold brochure from the same schedule data to `brochure.pdf` (English) and `brochure-es.pdf` (Spanish) at the site root, using headless Chrome (via puppeteer-core). The route maps load basemap tiles from OpenFreeMap, so the build needs network access. The text is in `_data/brochure.js` and the layout in `brochure/`. If Chrome isn't found locally, set `CHROME_PATH` to a Chrome or Chromium binary.

## Local development

Requires Node 22.

```sh
pnpm install
pnpm start
```

The site is served at http://localhost:8080 and rebuilds on changes. `pnpm build` writes the site to `_site/`.
