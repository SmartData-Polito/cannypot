#!/bin/bash

rm src/cowrie/learning/saved_state/saved_state.pkl
rm -r src/cowrie/learning/explorer/new_commands/*
rm -r src/cowrie/learning/explorer/new_commands_outputs/*
rm -r src/cowrie/learning/output/dict/*
rm -r src/cowrie/learning/output/qtable/*
rm -r src/cowrie/learning/rl/dictionary/*
rm var/log/cowrie/cowrie.json*
rm var/lib/cowrie/tty/*
