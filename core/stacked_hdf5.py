"""Finite-nframe stacked HDF5 (Eiger-like) 2D frame access."""
from __future__ import annotations

from pathlib import Path

import numpy as np

HDF5_SUFFIXES = {".h5", ".hdf5", ".nxs"}
MASTER_VDS_MIN = 1_000_000
DEFAULT_DATASET = "entry/data/data"
DEFAULT_START_TIME = "entry/data/start_time"


def is_hdf5_path(path: str | Path) -> bool:
    return Path(path).suffix.lower() in HDF5_SUFFIXES


def _open_h5(path: Path):
    try:
        import hdf5plugin  # noqa: F401
    except Exception:
        pass
    import h5py

    return h5py.File(path, "r")


def finite_nframes(
    path: str | Path,
    *,
    dataset: str = DEFAULT_DATASET,
    start_time: str = DEFAULT_START_TIME,
) -> int:
    """Return real frame count: finite start_time, else compact shape[0].

    Refuses master-style virtual axes (>= 1e6).
    """
    path = Path(path)
    with _open_h5(path) as handle:
        if start_time in handle:
            rel = np.asarray(handle[start_time][:], dtype=np.float64)
            counted = int(np.isfinite(rel).sum())
            if counted > 0:
                return counted
        if dataset not in handle:
            raise ValueError(f"HDF5 dataset {dataset!r} not in {path}")
        data = handle[dataset]
        if data.ndim == 2:
            return 1
        n0 = int(data.shape[0])
        if n0 >= MASTER_VDS_MIN:
            raise ValueError(f"refusing master VDS nframes={n0} for {path}")
        return n0


def read_frame(
    path: str | Path,
    iframe: int = 0,
    *,
    channel: int = 0,
    dataset: str = DEFAULT_DATASET,
) -> np.ndarray:
    path = Path(path)
    nframes = finite_nframes(path, dataset=dataset)
    if iframe < 0 or iframe >= nframes:
        raise IndexError(f"frame {iframe} outside 0..{nframes - 1} for {path}")
    with _open_h5(path) as handle:
        data = handle[dataset]
        if data.ndim == 2:
            array = np.array(data[()])
        elif data.ndim == 3:
            array = np.array(data[iframe])
        elif data.ndim == 4:
            array = np.array(data[iframe, channel])
        else:
            raise ValueError(f"unsupported HDF5 rank {data.ndim} in {path}")
    if array.ndim != 2:
        raise ValueError(f"expected 2D frame, got {array.shape} from {path}")
    return array
