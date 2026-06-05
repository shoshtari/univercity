from pathlib import Path


from data.data_loader import Dataset1SegmentationDataset, Dataset2SegmentationDataset


def main() -> None:
    dataset_dir = "./data/dataset"
    dataset1_root = Path(dataset_dir) / "dataset1"
    dataset2_root = Path(dataset_dir) / "dataset2"

    ds1 = Dataset1SegmentationDataset(dataset1_root)
    ds2 = Dataset2SegmentationDataset(dataset2_root)

    print(f"dataset1 len: {len(ds1)}")
    print(f"dataset2 len: {len(ds2)}")


if __name__ == "__main__":
    main()
