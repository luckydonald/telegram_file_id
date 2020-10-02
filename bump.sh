#!/bin/bash
INIT_FILE=tg_file_id/__init__.py
sed -i -e "s/^__version__ = '[0-9]\+.[0-9]\+.[0-9]\+'/__version__ = '$1'/" $INIT_FILE;
bat $INIT_FILE;
