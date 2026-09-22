"""Acknowledge site-local ICA runs.

Spatially constrained ICA is a purely local computation: each site's spatial
maps are computed independently, with nothing to combine centrally. This step
exists only to satisfy the workflow's local/remote pairing.
"""

from typing import Dict

from .types import SiteRunSummary


def acknowledge_site_results(site_results: Dict[str, SiteRunSummary], logger) -> None:
    """Log which sites completed their local ICA run; no aggregation is done."""
    for site_name, summary in site_results.items():
        logger.info(
            "Site %s finished local ICA (%s, %d input file(s))",
            site_name,
            summary.status,
            summary.n_input_files,
        )
