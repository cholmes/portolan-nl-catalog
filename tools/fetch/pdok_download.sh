#!/usr/bin/env bash
# Downloads the remaining (medium/large/deferred) BRO bulk files sequentially.
# Run from catalog root. Logs to vro/scripts/download.log
set -u
cd "$(dirname "$0")/../.." || exit 1
LOG="vro/scripts/download.log"
: > "$LOG"

# name|url|dest
items=(
  "GUF|https://service.pdok.nl/tno/bro-grondwatergebruiksysteem/atom/downloads/brogufvolledigeset.gpkg|vro/grondwatergebruiksysteem/brogufvolledigeset.gpkg"
  "GAR|https://service.pdok.nl/tno/bro-grondwatersamenstellingsonderzoek/atom/downloads/brogarvolledigeset.zip|vro/grondwatersamenstelling/brogarvolledigeset.zip"
  "Bodemkaart|https://service.pdok.nl/tno/bro-bodemkaart/atom/downloads/BRO_DownloadBodemkaart.gpkg|vro/bodemkaart/BRO_DownloadBodemkaart.gpkg"
  "Geomorfologie|https://service.pdok.nl/tno/bro-geomorfologische-kaart/atom/downloads/bro-geomorfologischekaart.zip|vro/geomorfologische_kaart/bro-geomorfologischekaart.zip"
  "GMW|https://service.pdok.nl/tno/bro-grondwatermonitoringput/atom/downloads/brogmwvolledigeset_v2_0.zip|vro/grondwatermonitoringput/brogmwvolledigeset_v2_0.zip"
  "BHR-G|https://service.pdok.nl/tno/bro-geologisch-booronderzoek/atom/downloads/brobhrgvolledigeset.gpkg|vro/geologisch_booronderzoek/brobhrgvolledigeset.gpkg"
  "BHR-P|https://service.pdok.nl/tno/bro-bodemkundig-booronderzoek/atom/downloads/brobhrpvolledigeset.zip|vro/bodemkundig_booronderzoek/brobhrpvolledigeset.zip"
  "GM-samenhang|https://service.pdok.nl/tno/bro-grondwatermonitoring-in-samenhang-karakteristieken/atom/downloads/brogmkenset.gpkg|vro/grondwatermonitoring_samenhang/brogmkenset.gpkg"
  "BHR-GT|https://service.pdok.nl/tno/bro-geotechnisch-booronderzoek/atom/downloads/geotechnischbooronderzoek.zip|vro/geotechnisch_booronderzoek/geotechnischbooronderzoek.zip"
  "SAD|https://service.pdok.nl/tno/bro-milieuhygienisch-bodemonderzoek/atom/downloads/brosadvolledigeset.gpkg|vro/milieuhygienisch_bodemonderzoek/brosadvolledigeset.gpkg"
  "CPT|https://service.pdok.nl/tno/bro-geotechnischsondeeronderzoek/atom/downloads/brocptvolledigeset_v2_0.zip|vro/geotechnisch_sondeeronderzoek/brocptvolledigeset_v2_0.zip"
)

for it in "${items[@]}"; do
  IFS='|' read -r name url dest <<< "$it"
  echo "[$(date +%H:%M:%S)] START $name -> $dest" >> "$LOG"
  if curl -sS -L --retry 3 --retry-delay 5 --max-time 7200 -o "$dest" "$url"; then
    echo "[$(date +%H:%M:%S)] OK    $name  $(du -h "$dest" | cut -f1)  $dest" >> "$LOG"
  else
    echo "[$(date +%H:%M:%S)] FAIL  $name  $url" >> "$LOG"
  fi
done
echo "[$(date +%H:%M:%S)] ALL DONE" >> "$LOG"
