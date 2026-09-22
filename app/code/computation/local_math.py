"""Run local spatially constrained ICA and finalize its output report."""

import os
import posixpath
import re
import shutil

from .gift import gift_gica
from .types import SiteInputs, SiteRunSummary

OUTPUT_HTML_NAME = "index.html"

# Match: src="x.png", src = "x.png", src='x.PNG', etc. (allow whitespace around '=')
_SRC_PATTERN = re.compile(r"""(\bsrc\s*=\s*)(["'])([^"']+?\.png)\2""", re.IGNORECASE)


def _finalize_html_report(out_dir: str, prefix: str) -> None:
    """Copy the GIFT HTML report to index.html and fix its image src paths."""
    expected_html_path = os.path.join(
        out_dir, f"{prefix}_gica_results/icatb_gica_html_report.html"
    )
    final_html_path = os.path.join(out_dir, OUTPUT_HTML_NAME)
    if not os.path.exists(expected_html_path):
        return
    shutil.copyfile(expected_html_path, final_html_path)

    with open(final_html_path, "r", encoding="utf-8") as f:
        html = f.read()

    report_dir = (
        f"{prefix}_gica_results"  # folder containing the images next to index.html
    )

    def _rewrite_src(match: re.Match) -> str:
        src_prefix = match.group(1)  # 'src = ' including original spacing
        quote = match.group(2)  # ' or "
        original = match.group(3)  # original value inside src

        # Use only the filename and point it to the report_dir, with web-safe slashes
        new_src = posixpath.join(report_dir, posixpath.basename(original))
        return f"{src_prefix}{quote}{new_src}{quote}"

    html = _SRC_PATTERN.sub(_rewrite_src, html)

    with open(final_html_path, "w", encoding="utf-8") as f:
        f.write(html)


def run_site_scica(inputs: SiteInputs, output_dir: str, logger) -> SiteRunSummary:
    """Run GIFT spatially constrained ICA locally and write outputs to disk."""
    logger.info(
        "Running spatially constrained ICA on %d input file(s)", len(inputs.in_files)
    )

    gift_gica(
        in_files=inputs.in_files,
        refFiles=inputs.refFiles,
        out_dir=output_dir,
        preproc_type=inputs.preproc_type,
        scaleType=inputs.scaleType,
        mask=inputs.mask,
        TR=inputs.TR,
        perfType=inputs.perfType,
        dummy_scans=inputs.dummy_scans,
        prefix=inputs.prefix,
    )

    _finalize_html_report(output_dir, inputs.prefix)

    return SiteRunSummary(status="completed", n_input_files=len(inputs.in_files))
