import os
import pytest

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
skip_all_tests = False

# TODO: 
# (a) check that valid tariff is verified
# (b) check that an invalid tariff is rejected

# Check that reject CSV is populated