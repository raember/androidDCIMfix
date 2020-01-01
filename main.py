#!/usr/bin/env python3
import os
import re
from datetime import datetime
from optparse import OptionParser
from os import stat_result
from shutil import copyfile
from typing import List, Generator


class Mediafile:
    _path: str
    _filename: str
    _stat = None

    def __init__(self, path: str):
        self._path = path
        self._filename = os.path.basename(path)
        self._stat = os.stat(path)

    @property
    def path(self) -> str:
        return self._path

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def stat(self) -> stat_result:
        return self._stat

    @property
    def last_access(self) -> datetime:
        return datetime.fromtimestamp(self._stat.st_atime)

    @property
    def last_modification(self) -> datetime:
        return datetime.fromtimestamp(self._stat.st_mtime)

    @property
    def last_metadata_change(self) -> datetime:
        return datetime.fromtimestamp(self._stat.st_ctime)

    def __str__(self):
        return self._filename


class RegularFile(Mediafile):
    _head: str
    _index: int
    _convolution: int
    _extension: str

    def __init__(self, path: str, head: str, index: int, extension: str, convolution: int = 0):
        super(RegularFile, self).__init__(path)
        self._head = head
        self._index = index
        self._convolution = convolution
        self._extension = extension

    @property
    def head(self) -> str:
        return self._head

    @property
    def index(self) -> int:
        return self._index

    @index.setter
    def index(self, value: int):
        self._index = value

    @property
    def convolution(self) -> int:
        return self._convolution

    @convolution.setter
    def convolution(self, value: int):
        self._convolution = value

    @property
    def extension(self) -> str:
        return self._extension

    @property
    def filename(self) -> str:
        if self._convolution == 0:
            return f"{self._head}_" \
                   f"{self.last_modification.year}{self.last_modification.month:02d}{self.last_modification.day:02d}" \
                   f"_{self.last_modification.hour:02d}{self.last_modification.minute:02d}{self.last_modification.second:02d}" \
                   f".{self._extension}"
        return f"{self._head}_" \
               f"{self.last_modification.year}{self.last_modification.month:02d}{self.last_modification.day:02d}" \
               f"_{self.last_modification.hour:02d}{self.last_modification.minute:02d}{self.last_modification.second:02d}" \
               f"_{self._convolution}.{self._extension}"
        # if self._convolution == 0:
        #     return f"{self._head}_{self._index:04d}.{self._extension}"
        # return f"{self._head}_{self._index:04d}_{self._convolution}.{self._extension}"

    def __str__(self):
        return self.filename


class PictureFile(RegularFile):
    def __init__(self, path: str, index: int, convolution: int = 0):
        super(PictureFile, self).__init__(path, 'IMG', index, 'jpg', convolution)


class VideoFile(RegularFile):
    def __init__(self, path: str, index: int, convolution: int = 0):
        super(VideoFile, self).__init__(path, 'VID', index, 'mp4', convolution)


def parse_files(filenames: Generator[str, None, None]) -> Generator[Mediafile, None, None]:
    for path in filenames:
        match = re.match(r"(?P<head>DSC|MOV)_(?P<idx>\d{4})(_(?P<conv>\d{1,3}))?\.(?P<ext>JPG|mp4)$",
                         os.path.basename(path))
        if not match:
            yield Mediafile(path)
            continue
        head = match.group('head').upper()
        index = int(match.group('idx'))
        convolution = int(match.group('conv')) if match.group('conv') else 0
        # extension = match.group('ext')
        if head == 'DSC':
            yield PictureFile(path, index, convolution)
        elif head == 'MOV':
            yield VideoFile(path, index, convolution)


class Analysis:
    min_atime: Mediafile
    max_atime: Mediafile
    min_mtime: Mediafile
    max_mtime: Mediafile
    max_ctime: Mediafile
    min_ctime: Mediafile
    min_convolution: RegularFile
    unusual_filenames: List[Mediafile]
    total: int

    def __init__(self):
        self.min_atime = None
        self.max_atime = None
        self.min_mtime = None
        self.max_mtime = None
        self.min_ctime = None
        self.max_ctime = None
        self.min_convolution = None
        self.unusual_filenames = []
        self.total = 0

    def perform_analysis(self, gen: Generator[Mediafile, None, None]) -> Generator[Mediafile, None, None]:
        for file in gen:
            self.analyze(file)
            yield file

    def analyze(self, file: Mediafile):
        self.total += 1
        if self.min_atime is None or self.min_atime.last_access > file.last_access:
            self.min_atime = file
        if self.max_atime is None or self.max_atime.last_access < file.last_access:
            self.max_atime = file
        if self.min_mtime is None or self.min_mtime.last_modification > file.last_modification:
            self.min_mtime = file
        if self.max_mtime is None or self.max_mtime.last_modification < file.last_modification:
            self.max_mtime = file
        if self.min_ctime is None or self.min_ctime.last_metadata_change > file.last_metadata_change:
            self.min_ctime = file
        if self.max_ctime is None or self.max_ctime.last_metadata_change < file.last_metadata_change:
            self.max_ctime = file
        if isinstance(file, RegularFile):
            if self.min_convolution is None or self.min_convolution.convolution < file.convolution:
                self.min_convolution = file
        else:
            self.unusual_filenames.append(file)

    def print_time_table(self):
        earliest_label = "Earliest:"
        latest_label = "Latest:"
        pad_col0 = max(len(earliest_label), len(latest_label))
        pad_col1 = max(len(str(self.min_atime.last_access)), len(str(self.min_atime)),
                       len(str(self.max_atime.last_access)), len(str(self.max_atime)))
        pad_col2 = max(len(str(self.min_mtime.last_modification)), len(str(self.min_mtime)),
                       len(str(self.max_mtime.last_modification)), len(str(self.max_mtime)))
        pad_col3 = max(len(str(self.min_ctime.last_metadata_change)), len(str(self.min_ctime)),
                       len(str(self.max_ctime.last_metadata_change)), len(str(self.max_ctime)))
        print(" " * pad_col0 + " ┃ " +
              "Access".ljust(pad_col1) + " │ " +
              "Modification".ljust(pad_col2) + " │ " +
              "Metadata change".ljust(pad_col3))
        print("━" * (pad_col0 + 1) + "╋" +
              "━" * (pad_col1 + 2) + "┿" +
              "━" * (pad_col2 + 2) + "┿" +
              "━" * (pad_col3 + 2))
        print(f"{earliest_label.rjust(pad_col0)} ┃ "
              f"{str(self.min_atime).ljust(pad_col1)} │ "
              f"{str(self.min_mtime).ljust(pad_col2)} │ "
              f"{str(self.min_ctime).ljust(pad_col3)}")
        print(f"{' ' * pad_col0} ┃ "
              f"{str(self.min_atime.last_access).ljust(pad_col1)} │ "
              f"{str(self.min_mtime.last_modification).ljust(pad_col2)} │ "
              f"{str(self.min_ctime.last_metadata_change).ljust(pad_col3)}")
        print("─" * (pad_col0 + 1) + "╂" +
              "─" * (pad_col1 + 2) + "┼" +
              "─" * (pad_col2 + 2) + "┼" +
              "─" * (pad_col3 + 2))
        print(f"{latest_label.rjust(pad_col0)} ┃ "
              f"{str(self.max_atime).ljust(pad_col1)} │ "
              f"{str(self.max_mtime).ljust(pad_col2)} │ "
              f"{str(self.max_ctime).ljust(pad_col3)}")
        print(f"{' ' * pad_col0} ┃ "
              f"{str(self.max_atime.last_access).ljust(pad_col1)} │ "
              f"{str(self.max_mtime.last_modification).ljust(pad_col2)} │ "
              f"{str(self.max_ctime.last_metadata_change).ljust(pad_col3)}")


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-a", "--analyze", dest="analyze", action="store_true",
                      help="Analyze media files")
    parser.add_option("-o", "--out", dest="out", default=None,
                      help="Write sorted files to directory")
    args: List[str]
    (opt, args) = parser.parse_args()
    assert len(args) == 1
    path = args[0]
    files = parse_files(os.path.join(path, f) for f in os.listdir(path))
    if opt.analyze:
        print("Analyzing media files")
        analysis = Analysis()
        files = list(analysis.perform_analysis(files))
        print(f"Number of files: {len(files)}")
        analysis.print_time_table()
        print(f"Minimum convolutions detected: {analysis.min_convolution.convolution} ({analysis.min_convolution})")
        print(f"Unusual file names ({len(analysis.unusual_filenames)}):")
        print(", ".join(map(str, analysis.unusual_filenames)))
    if opt.out:
        out_path: str = opt.out
        print(f"Writing files to '{out_path}'")
        if not os.path.isdir(out_path):
            os.mkdir(out_path)
        files = sorted(files, key=lambda f: f.last_modification)
        pics = 0
        vids = 0
        other = 0
        new_filenames = []
        for file in files:
            if isinstance(file, PictureFile):
                pics += 1
                file.index = pics
                file.convolution = 0
                while file.filename in new_filenames:
                    file.convolution += 1
            elif isinstance(file, VideoFile):
                vids += 1
                file.index = vids
                file.convolution = 0
                while file.filename in new_filenames:
                    file.convolution += 1
            else:
                other += 1
            new_path = os.path.join(out_path, file.filename)
            copyfile(file.path, new_path)
            new_filenames.append(file.filename)
            print(f"Copied {os.path.basename(file.path)} to '{new_path}'")
        print(f"Copied {pics} pictures, {vids} videos and {other} other files to '{out_path}'")
