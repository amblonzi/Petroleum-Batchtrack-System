import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from a2wsgi import ASGIMiddleware
from app.main import app

# Wrap FastAPI app with ASGIMiddleware for WSGI compatibility
application = ASGIMiddleware(app)