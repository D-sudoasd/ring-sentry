import tempfile
import unittest
from pathlib import Path

import numpy as np

from core.loader import load_image, load_image_with_info
from core.stacked_hdf5 import finite_nframes, read_frame


def _write_stack(path: Path, *, n_real: int = 3, pad: int = 0, with_channel: bool = True) -> np.ndarray:
    import h5py

    height, width = 5, 7
    n0 = n_real + pad
    if with_channel:
        data = np.arange(n0 * 2 * height * width, dtype=np.float32).reshape(n0, 2, height, width)
    else:
        data = np.arange(n0 * height * width, dtype=np.float32).reshape(n0, height, width)
    start = np.full((n0,), np.nan, dtype=np.float64)
    start[:n_real] = np.arange(n_real, dtype=np.float64)
    with h5py.File(path, "w") as handle:
        handle.create_dataset("entry/data/data", data=data)
        handle.create_dataset("entry/data/start_time", data=start)
    return data


class StackedHdf5LoaderTests(unittest.TestCase):
    def test_finite_nframes_ignores_daq_pad(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "series.h5"
            data = _write_stack(path, n_real=3, pad=5)
            self.assertEqual(finite_nframes(path), 3)
            frame = load_image(path, frame_index=1, channel=0)
            self.assertEqual(frame.shape, (5, 7))
            self.assertTrue(np.array_equal(frame, data[1, 0]))
            again = finite_nframes(path)
            self.assertEqual(again, 3)

    def test_refuses_master_vds_shape(self):
        import h5py

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "master.h5"
            with h5py.File(path, "w") as handle:
                handle.create_dataset("entry/data/data", shape=(1_000_000, 2, 2), dtype="f4")
            with self.assertRaises(ValueError):
                finite_nframes(path)

    def test_public_loader_reports_nframes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "series.h5"
            _write_stack(path, n_real=4, pad=0, with_channel=False)
            info = load_image_with_info(path, frame_index=2)
            self.assertEqual(info["metadata"]["nframes"], 4)
            self.assertEqual(info["data"].shape, (5, 7))
            self.assertEqual(read_frame(path, 2).shape, (5, 7))
