import os
import pytest

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
skip_all_tests = False

# TODO: 
# (a) check that 100 tariffs are added
# (b) check that metadata is appended