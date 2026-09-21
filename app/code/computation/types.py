"""Define values exchanged by the spatially constrained ICA computation."""

from dataclasses import dataclass
from typing import List


@dataclass
class SiteInputs:
    """Site-local nifti inputs and local GIFT parameters."""

    in_files: List[str]
    refFiles: str
    preproc_type: int
    scaleType: int
    mask: str
    TR: list
    perfType: int
    dummy_scans: list
    prefix: str


@dataclass
class SiteRunSummary:
    """Small per-site status payload returned after a local GIFT run."""

    status: str
    n_input_files: int
