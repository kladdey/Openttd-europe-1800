import io
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_heightmap_provenance import audit_archive, compare_pngs, fingerprint, png_chunks


def png(array, compression=6):
    out = io.BytesIO()
    Image.fromarray(array).save(out, format='PNG', compress_level=compression)
    return out.getvalue()


class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.array = np.arange(256, dtype=np.uint8).reshape(8, 8, 4)

    def test_reencoding_is_pixel_identity_not_byte_identity(self):
        result = compare_pngs(png(self.array, 0), png(self.array, 9))
        self.assertFalse(result['encoded_bytes_equal'])
        self.assertTrue(result['rgba_pixels_equal'])
        self.assertEqual(result['different_rgba_pixels'], 0)
        self.assertEqual(result['source']['rgba_sha256'], result['candidate']['rgba_sha256'])

    def test_green_change_cannot_pass_red_only_comparison(self):
        other = self.array.copy()
        other[0, 0, 1] += 1
        result = compare_pngs(png(self.array), png(other))
        self.assertFalse(result['rgba_pixels_equal'])
        self.assertEqual(result['different_rgba_pixels'], 1)
        self.assertEqual(result['different_red_pixels'], 0)

    def test_dimensions_are_checked(self):
        result = compare_pngs(png(self.array), png(self.array[:4]))
        self.assertFalse(result['dimensions_equal'])
        self.assertIsNone(result['different_rgba_pixels'])

    def test_crc_and_truncation_are_rejected(self):
        data = bytearray(png(self.array))
        data[29] ^= 1
        with self.assertRaisesRegex(ValueError, 'CRC'):
            png_chunks(bytes(data))
        with self.assertRaises(ValueError):
            png_chunks(png(self.array)[:-3])

    def test_archive_is_read_without_extracting_paths_or_links(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = base / 'source.png'
            source.write_bytes(png(self.array))
            archive = base / 'test.tar.gz'
            with tarfile.open(archive, 'w:gz') as stream:
                data = png(self.array, 0)
                item = tarfile.TarInfo('../outside.png')
                item.size = len(data)
                stream.addfile(item, io.BytesIO(data))
                link = tarfile.TarInfo('link.png')
                link.type = tarfile.SYMTYPE
                link.linkname = '/etc/passwd'
                stream.addfile(link)
            before = set(base.parent.iterdir())
            report = audit_archive(source, archive)
            self.assertEqual(len(report['comparisons']), 1)
            self.assertTrue(report['comparisons'][0]['rgba_pixels_equal'])
            self.assertEqual(before, set(base.parent.iterdir()))

    def test_preserved_source_matches_recorded_fingerprint(self):
        root = Path(__file__).resolve().parents[1]
        import json
        report = json.loads((root / 'maps/calibration/provenance_v1/pixel_comparison.json').read_text())
        actual, _ = fingerprint((root / 'source_assets/heightmaps/Europe_heightmap_original.png').read_bytes())
        self.assertEqual(actual, report['comparisons'][0]['source'])
        self.assertTrue(report['comparisons'][0]['rgba_pixels_equal'])


if __name__ == '__main__':
    unittest.main()
