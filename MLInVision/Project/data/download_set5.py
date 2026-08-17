import argparse
import tarfile
import urllib.request
from pathlib import Path

URLS = {
    "HR": "https://huggingface.co/datasets/eugenesiow/Set5/resolve/main/data/Set5_HR.tar.gz",
    "LR/X2": "https://huggingface.co/datasets/eugenesiow/Set5/resolve/main/data/Set5_LR_x2.tar.gz",
    "LR/X3": "https://huggingface.co/datasets/eugenesiow/Set5/resolve/main/data/Set5_LR_x3.tar.gz",
    "LR/X4": "https://huggingface.co/datasets/eugenesiow/Set5/resolve/main/data/Set5_LR_x4.tar.gz",
}


def _download(url: str, destination: Path) -> None:
    if destination.exists():
        return
    request = urllib.request.Request(
        url, headers={"User-Agent": "STSN-course-project/1.0"}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        destination.write_bytes(response.read())


def _extract_images(archive: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:gz") as bundle:
        for member in bundle.getmembers():
            suffix = Path(member.name).suffix.lower()
            if not member.isfile() or suffix not in {".png", ".jpg", ".jpeg", ".bmp"}:
                continue
            source = bundle.extractfile(member)
            if source is None:
                continue
            (destination / Path(member.name).name).write_bytes(source.read())


def download_set5(dataset_root: Path, scales: tuple[int, ...] = (2,)) -> Path:
    set5_root = dataset_root / "Set5"
    archive_root = dataset_root / "_archives"
    archive_root.mkdir(parents=True, exist_ok=True)
    selections = ["HR", *(f"LR/X{scale}" for scale in scales)]
    for relative in selections:
        archive = archive_root / f"Set5_{relative.replace('/', '_')}.tar.gz"
        _download(URLS[relative], archive)
        _extract_images(archive, set5_root / relative)
    return set5_root


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).parent / "dataset")
    parser.add_argument("--scales", type=int, nargs="+", default=[2])
    args = parser.parse_args()
    destination = download_set5(args.root, tuple(args.scales))
    print(f"Set5 is ready at: {destination}")


if __name__ == "__main__":
    main()
