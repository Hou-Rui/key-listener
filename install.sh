#!/bin/sh

PREFIX="${1:-/usr}"
PROJECT='keylistener'
TMPRUN='run.sh'

SHARE_DIR="$PREFIX/share/$PROJECT"
ICON_DIR="$PREFIX/share/icons/hicolor/256x256/apps"
APPL_DIR="$PREFIX/share/applications"

install -D -m 644 ./src/*.py -t "$SHARE_DIR"
install -D -m 644 ./src/qml/qmldir -t "$SHARE_DIR/qml"
install -D -m 644 ./src/qml/*.qml -t "$SHARE_DIR/qml"
install -D -m 644 ./icons/*.png -t "$ICON_DIR"
install -D -m 644 ./*.desktop -t "$APPL_DIR"

echo '#!/bin/sh' > "$TMPRUN"
echo "python3 \"$SHARE_DIR/main.py\"" >> "$TMPRUN"
install -D -m 755 "$TMPRUN" -T "$PREFIX/bin/$PROJECT"
rm "$TMPRUN"
