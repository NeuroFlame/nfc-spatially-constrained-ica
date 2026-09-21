"""Declare the spatially constrained ICA computation workflow."""

from framework import ComputationSpec, local_step, remote_step, stepped_workflow

from .inputs import load_site_inputs
from .local_math import run_site_scica
from .remote_math import acknowledge_site_results

SPEC = ComputationSpec(
    workflow=stepped_workflow(
        local_step(fn=run_site_scica, input_fn=load_site_inputs),
        remote_step(fn=acknowledge_site_results),
    ),
)
