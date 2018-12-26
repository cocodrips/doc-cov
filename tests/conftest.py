import pathlib
import sys

proj_root = (pathlib.Path(__file__).parent / 'sample_project').resolve()
sys.path.insert(0, str(proj_root))
