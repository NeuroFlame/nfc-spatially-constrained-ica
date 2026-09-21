"""Load and validate site-local inputs for spatially constrained ICA."""

import glob
import json
import os

from .types import SiteInputs

GIFT_TEMPLATE_PATH = "/computation/gift/GroupICAT/icatb/icatb_templates"


def _validate_type(variable, variable_name, expected_types):
    """Raise ValueError when a local parameter does not match its expected type."""
    if not isinstance(expected_types, list):
        expected_types = [expected_types]
    if type(variable) not in expected_types:
        raise ValueError(
            f"Got invalid type for variable {variable_name}. "
            f"Expected {expected_types}, got {type(variable)}."
        )


def _resolve_ref_files(ref_files: str) -> str:
    """Resolve a bundled Neuromark template name to its full path in the image."""
    if not os.path.exists(ref_files) and "neuromark" in ref_files.lower():
        if ".nii" not in ref_files:
            ref_files = ref_files + ".nii"
        ref_files = os.path.join(GIFT_TEMPLATE_PATH, ref_files)
    return ref_files


def load_site_inputs(data_dir: str) -> SiteInputs:
    """Load nifti inputs and local GIFT parameters, validating both."""
    in_files = list(glob.glob(os.path.join(data_dir, "*.nii*")))
    if len(in_files) == 0:
        raise ValueError("No nifti files were found in data directory.")
    for filename in in_files:
        if not os.path.exists(filename):
            raise ValueError(f"Input nifti {filename} does not exist")

    local_parameters_path = os.path.join(data_dir, "local_parameters.json")
    with open(local_parameters_path, "r") as f:
        local_parameters = json.load(f)

    ref_files = _resolve_ref_files(local_parameters["refFiles"])
    if not os.path.exists(ref_files):
        raise ValueError(
            f"Input template file {ref_files} does not exist on the file system"
        )
    _validate_type(ref_files, "refFiles", str)

    preproc_type = local_parameters["preproc_type"]
    _validate_type(preproc_type, "preproc_type", int)

    scale_type = local_parameters["scaleType"]
    _validate_type(scale_type, "scaleType", int)

    mask = local_parameters["mask"]
    _validate_type(mask, "mask", str)
    if mask not in ["default", "default&icv"] and not os.path.exists(mask):
        raise ValueError(
            "Mask must be either default, default&icv or a file that exists on "
            f"the file system. Got {mask}, which does not exist on the filesystem."
        )

    tr = local_parameters["TR"]
    _validate_type(tr, "TR", list)

    perf_type = local_parameters["perfType"]
    _validate_type(perf_type, "perfType", int)

    dummy_scans = local_parameters["dummy_scans"]
    _validate_type(dummy_scans, "dummy_scans", list)

    prefix = local_parameters["prefix"]
    _validate_type(prefix, "prefix", str)

    return SiteInputs(
        in_files=in_files,
        refFiles=ref_files,
        preproc_type=preproc_type,
        scaleType=scale_type,
        mask=mask,
        TR=tr,
        perfType=perf_type,
        dummy_scans=dummy_scans,
        prefix=prefix,
    )
