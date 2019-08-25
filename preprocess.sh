# download images
wget --no-parent -r -nd -P /C/work/wood/data http://www.ee.oulu.fi/research/imag/wood/WOOD/IMAGES/

# download labels
wget -P /C/work/wood/data http://www.ee.oulu.fi/research/imag/wood/WOOD/manlabel.txt

# convert to png
cd /C/work/wood/data
find . -name '*.gz' -exec sh -c 'gzip -dc "$1" | magick convert - "${1%.gz}.png" && rm "$1"' sh {} \;
