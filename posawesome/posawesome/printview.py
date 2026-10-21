"""Customisations for Frappe's standard print-view rendering.

Frappe's ``www/printview.html`` template is deliberately standalone: it does
not extend ``templates/web.html`` and therefore never loads ``app_include_css``
or ``web_include_css``. The ``pdf_body_html`` hook is called by
``frappe.www.printview.get_rendered_template`` for the print-view body, so it
is the smallest supported hook we can use to make the POS Awesome stylesheet
available there.

The stylesheet is added with ``media="screen"`` so it only affects the
on-screen action toolbar. PDF generation and the printed invoice remain
unchanged. The hook is also called while generating PDFs; API calls are
skipped to keep generated PDF HTML completely free of screen-only assets.
"""

from __future__ import annotations

from pathlib import Path

import frappe
from frappe.utils.pdf import pdf_body_html as render_print_body

from posawesome import __version__

_CSS_PATH = Path(__file__).resolve().parent.parent / "public" / "css" / "posawesome.css"


def _stylesheet_url() -> str:
    """Return the public stylesheet URL with a file-based cache buster."""

    try:
        version = int(_CSS_PATH.stat().st_mtime)
    except OSError:
        version = __version__

    return f"/assets/posawesome/css/posawesome.css?v={version}"


def pdf_body_html(template, args, **kwargs):
    """Render the print body and append the screen-only toolbar stylesheet."""

    html = render_print_body(template, args, **kwargs)

    # PDF downloads and the get_html_and_style API are served under /api/.
    # They do not need the browser toolbar stylesheet, and keeping it out of
    # those responses avoids an unnecessary asset request while generating a
    # PDF.
    request = getattr(frappe.local, "request", None)
    request_path = getattr(request, "path", "") or ""
    if request_path.startswith("/api/"):
        return html

    stylesheet_url = _stylesheet_url()
    return (
        f'{html}\n<link rel="stylesheet" type="text/css" media="screen" '
        f'href="{stylesheet_url}" data-posawesome-printview-css="1">'
    )
