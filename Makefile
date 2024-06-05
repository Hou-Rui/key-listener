.PHONY: all help build clean run

PROJECT = keylistener
SRC_PYTHON = $(wildcard *.py)
SRC_QML = $(wildcard *.qml)
SRC_MAIN = main.py

all: help

help:
	@echo available commands: build, clean, run

build:
	pyside6-project build

clean:
	pyside6-project clean

run: build
	python $(SRC_MAIN)