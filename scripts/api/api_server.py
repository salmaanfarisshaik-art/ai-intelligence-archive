"""
-------------------------------------------------------
THIS FILE IS AUTO-GENERATED.
DO NOT EDIT MANUALLY.
Changes may be overwritten during the next pipeline run.
-------------------------------------------------------

Local Knowledge API Server.
Uses Python's built-in http.server — zero external dependencies.
The API is completely optional and read-only.
The ingestion pipeline does not depend on this server.
"""
import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from scripts.lib.logger import setup_logger
from scripts.api.routes import handle_request
from scripts.api.serializers import serialize_response

logger = setup_logger("api_server")

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8080


class KnowledgeAPIHandler(BaseHTTPRequestHandler):
    """
    Read-only HTTP request handler.
    All endpoints are deterministic GET-only operations.
    No mutation endpoints exist.
    """

    def do_GET(self):
        parsed = urlparse(self.path)
        query_params = parse_qs(parsed.query)
        path = parsed.path.rstrip("/")

        try:
            result = handle_request(path, query_params)
            response_body = serialize_response(result)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(response_body.encode("utf-8"))
        except Exception as e:
            logger.error(f"API error on {self.path}: {e}", exc_info=True)
            error_body = serialize_response({"error": str(e)})
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(error_body.encode("utf-8"))

    def do_POST(self):
        """Explicitly reject mutation attempts."""
        self.send_response(405)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        body = serialize_response({"error": "Method Not Allowed. This API is read-only."})
        self.wfile.write(body.encode("utf-8"))

    do_PUT = do_POST
    do_DELETE = do_POST
    do_PATCH = do_POST

    def log_message(self, format, *args):
        """Route access logs through the structured logger."""
        logger.info(f"API {args[0]}")


def start_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
    """Start the local read-only Knowledge API server."""
    server = HTTPServer((host, port), KnowledgeAPIHandler)
    logger.info(f"Knowledge API server starting on http://{host}:{port}")
    logger.info("Endpoints: /api/models, /api/papers, /api/datasets, /api/tools, /api/news, /api/search, /api/categories, /api/tags, /api/analytics, /api/graph, /api/entity/<id>")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("API server shutting down.")
        server.server_close()


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HOST
    port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORT
    start_server(host, port)
