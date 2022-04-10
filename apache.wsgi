import sys, os, logging
sys.stdout = sys.stderr
logging.basicConfig(stream=sys.stderr)

project_filepath = os.path.join(os.path.dirname(__file__), "", "")
sys.path.insert(0, project_filepath)

from server import app as application
