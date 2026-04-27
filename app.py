"""Flask dashboard for UPS metrics logged by Network UPS Tools."""

import os

from flask import Flask, render_template, request

from ups_data import build_dashboard_context

HOST = os.environ.get("UPS_DASHBOARD_HOST", "127.0.0.1")

# Keep this file small because it is the production WSGI entrypoint.
app = Flask(__name__)


@app.route("/")
def homepage() -> str:
    """Render the UPS dashboard."""

    # The data module owns parsing so this route only handles HTTP concerns.
    return render_template(
        "chartjs-example.html",
        **build_dashboard_context(
            request.args.get("start"),
            request.args.get("end"),
        ),
    )


if __name__ == "__main__":
    app.run(debug=False, host=HOST, port=5000)
