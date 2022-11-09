import typing
from dataclasses import dataclass
from pathlib import Path

class Metadata(object):

    @dataclass
    class SeqInfo(object):
        fps: float
        progressiveSeq: bool

        def __post_init__(self):
            self.fps = float(self.fps)
            self.progressiveSeq = bool(int(self.progressiveSeq))

    @dataclass
    class ImageInfo(object):
        pathName: str
        name: str
        isProgressive: bool
        isTopFieldFirst: bool
        isRepeatFirstField: bool

        def __post_init__(self):
            self.isProgressive = bool(int(self.isProgressive))
            self.isTopFieldFirst = bool(int(self.isTopFieldFirst))
            self.isRepeatFirstField = bool(int(self.isRepeatFirstField))

    seqInfo: SeqInfo
    imageInfos: dict[str, ImageInfo]

    def __init__(self, path: str):
        with open(path, 'r') as f:
            self._loadMetadata(f)
        self.applyRules()

    def __getitem__(self, name: str):
        return self.imageInfos.get(name, None)

    def __iter__(self):
        return iter(self.imageInfos.values())

    def __len__(self):
        return len(self.imageInfos.values())

    @staticmethod
    def get_file_name(path: str) -> str:
        pathObj = Path(path)
        return pathObj.stem

    def _loadSeqMetadata(self, line: str) -> SeqInfo:
        lineType, *args = line.split(' ')
        if lineType.lower() != 'sequence':
            raise Exception(f'Given metadata was expected to be a sequence, but was ${lineType}!')
        buildArgs = dict([arg.split(':') for arg in args])
        return self.SeqInfo(**buildArgs)

    def _loadImageMetadata(self, line: str) -> ImageInfo:
        lineType, name, *args = line.split(' ')
        if lineType.lower() != 'image':
            raise Exception(f'Given metadata was expected to be an image, but was ${lineType}!')
        buildArgs = dict([arg.split(':') for arg in args])
        return self.ImageInfo(pathName=name, name=name.rsplit('.', 1)[0], **buildArgs)

    def _loadMetadata(self, file: typing.TextIO):
        lines = [line.strip() for line in file.readlines()]
        self.seqInfo = self._loadSeqMetadata(lines[0])
        self.imageInfos = dict()
        for line in lines[1:]:
            imgMetadata = self._loadImageMetadata(line)
            self.imageInfos[imgMetadata.name] = imgMetadata

    def applyRules(self):
        if self.seqInfo.progressiveSeq:
            for imgInfo in self.imageInfos.values():
                imgInfo.isProgressive = True

    def applyHeuristics(self):
        if not self.seqInfo.progressiveSeq:
            # make heuristic check of misuse of seqInfo.isProgressiveSequence
            progressiveCount = len([0 for imgInfo in self.imageInfos.values() if imgInfo.isProgressive])
            interlacedCount = len(self.imageInfos) - progressiveCount
            if progressiveCount != 0 and interlacedCount != 0:
                print("[WARN] Sequence is not progressive and contains mixed [interlaced|progressive] image flags !")
                print("[INFO] Converting all image flags to interlaced...")
                # Assume everything is interlaced
                for imgInfo in self.imageInfos.values():
                    imgInfo.isProgressive = False
