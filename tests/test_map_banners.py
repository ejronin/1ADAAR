"""Unknown maps and unapproved imagery never alter published graphics."""
import unittest
from pathlib import Path
from unittest.mock import patch
import tempfile
import json
from src import map_banners

ROOT=Path(__file__).resolve().parents[1]


class MapBannerTests(unittest.TestCase):
    def test_no_cleared_images_means_original_art(self):
        for name in ('Bakurani','Ozeti','Zestafona','map not listed','../assets/secret'):
            self.assertIsNone(map_banners.banner_for_map(name))
        self.assertIsNone(map_banners.banner_for_map(None))

    def test_only_exact_manifest_names_and_local_files_are_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            (folder/'bakurani.webp').write_bytes(b'candidate image')
            with patch.object(map_banners,'FOLDER',folder),patch.object(
                  map_banners,'MANIFEST',folder/'manifest.json'):
                (folder/'manifest.json').write_text(json.dumps({
                    'schemaVersion':1,'images':{'Bakurani':'../bad.webp'}}))
                self.assertIsNone(map_banners.banner_for_map('Bakurani'))
                (folder/'manifest.json').write_text(json.dumps({
                    'schemaVersion':1,'images':{'Bakurani':'bakurani.webp'}}))
                self.assertEqual(map_banners.banner_for_map('BAKURANI'),
                                 folder/'bakurani.webp')
                self.assertIsNone(map_banners.banner_for_map('Other'))

    def test_no_external_image_urls_in_public_asset_manifest(self):
        content=(ROOT/'docs/assets/map-banners/manifest.json').read_text()
        self.assertNotIn('https:',content)
        self.assertNotIn('http:',content)


if __name__=='__main__':
    unittest.main()
