import os
import zipfile
from configparser import ConfigParser
from io import StringIO
from itertools import chain

from tqdm import tqdm


RELEASES = [
    {
        "flavour": "high-res",
        "filename_pattern": "imperial-assault-data-v{version}-high-res.zip",
        "paths": [
            ('images/large', 'images'),
            ('data', 'data'),
            ('schemas', 'schemas'),
            ('LICENSE', 'LICENSE')
        ],
    },
    {
        "flavour": "low-res",
        "filename_pattern": "imperial-assault-data-v{version}-low-res.zip",
        "paths": [
            ('images/small', 'images'),
            ('data', 'data'),
            ('schemas', 'schemas'),
            ('LICENSE', 'LICENSE')
        ],
    }
]


class ReleaseBuilder:
    destination = 'build'
    filename_pattern = "imperial-assault-data-v{version}-{flavour}.zip"

    def __init__(self):
        self.root = os.path.abspath(os.path.dirname(__file__))
        config = ConfigParser()
        config.read(os.path.join(self.root, 'imperial-assault-data.cfg'))
        self.version = config['default']['version']

    @staticmethod
    def get_file_paths(root, dest):
        if os.path.isfile(root):
            yield root, dest
        else:
            for dir_path, _, file_names in os.walk(root):
                for f in file_names:
                    yield os.path.join(dir_path, f), os.path.join(dir_path, f).replace(root, dest)

    def build_releases(self):
        build_path = os.path.join(self.root, self.destination)
        if not os.path.exists(build_path):
            os.makedirs(build_path)

        for release_config in RELEASES:
            release_filename = os.path.join(build_path, self.filename_pattern.format(
                version=self.version,
                flavour=release_config['flavour']
            ))
            zip_file = zipfile.ZipFile(release_filename, 'w', zipfile.ZIP_DEFLATED)

            files = list(chain(*[
                self.get_file_paths(os.path.join(self.root, origin_path), destination_path)
                for origin_path, destination_path in release_config['paths']
            ]))

            version_tag = f"v{self.version}-{release_config['flavour']}"

            for filename_abs_path, zip_destination in tqdm(files, desc=f"Building release {version_tag}"):
                zip_file.write(filename_abs_path, zip_destination)

            version_file = StringIO()
            version_file.write(version_tag)
            version_file.seek(0)
            zip_file.writestr("VERSION", version_file.getvalue())

            zip_file.close()


if __name__ == '__main__':
    rb = ReleaseBuilder()
    rb.build_releases()
