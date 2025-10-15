#!/usr/bin/env python3
# Debug helper: import ResponseScreen and call setup_card to reproduce language/name resolution
import os
import sys
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

os.environ['APP_LANG'] = 'pt'
from screens import ResponseScreen

rs = ResponseScreen()
# Simulate a card name passed from draw (French canonical)
rs.setup_card('Le Mat', 'droite')

print('Done')
