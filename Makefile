.PHONY: build clean run

PROJECT := keylistener
QML_DIR := src/qml
QML_SRC := $(QML_DIR)/qmldir $(wildcard $(QML_DIR)/*.qml)

all:
	@echo "usage: make [build | clean | run]"

build: $(QML_SRC)
	pyside6-project build
	ln -sf $(shell pwd)/$(PROJECT) $(QML_DIR)/

clean:
	pyside6-project clean
	rm -rf $(QML_DIR)/$(PROJECT)

run:
	pyside6-project run
