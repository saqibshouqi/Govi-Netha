"""
Shared pytest fixtures.
Adds the backend root to sys.path so all imports work when pytest
is run from the backend/ directory.
"""
import sys
import os

# Ensure backend/ is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))