"""
Zer0n-Bench: Dataset Schema and Hash Integrity Validator
Validates JSON schema and cryptographic hash integrity for dataset entries.

Usage:
    python validate_schema.py dataset/zeron_bench_v1.0_full.json
    python validate_schema.py --manifest splits.json --sample 10

Options:
    --manifest FILE    Path to splits.json for split-aware validation
    --sample N         Validate only N random entries (for quick checks)
"""

import json
import hashlib
import sys
import argparse
import random
import os


def validate_dataset(data, sample_size=None):
    """Validate dataset entries for schema and hash integrity."""
    required_fields = ["target_id", "category", "vulnerability",
                       "ai_agents", "integrity_proof"]

    # Sample if requested
    if sample_size and sample_size < len(data):
        random.seed(42)  # Reproducible sampling
        data = random.sample(data, sample_size)
        print(f"Sampling {sample_size} entries for validation...")

    print(f"Validating {len(data)} entries...")
    errors = []
    validated = 0

    for i, entry in enumerate(data):
        # 1. Schema check
        for field in required_fields:
            if field not in entry:
                errors.append(f"Entry {i} ({entry.get('target_id','?')}): missing '{field}'")

        # 2. Cryptographic Hash Verification
        try:
            content = {k: v for k, v in entry.items()
                       if k != "integrity_proof"}
            computed = hashlib.sha256(
                json.dumps(content, sort_keys=True).encode()
            ).hexdigest()
            stored = entry["integrity_proof"]["hash"].replace("0x", "")
            if computed != stored:
                errors.append(
                    f"Entry {i} ({entry['target_id']}): hash mismatch "
                    f"[computed={computed[:8]}... stored={stored[:8]}...]"
                )
            else:
                validated += 1
        except Exception as e:
            errors.append(f"Entry {i}: hash check failed — {e}")

    return errors, validated, len(data)


def main():
    parser = argparse.ArgumentParser(
        description="Zer0n-Bench Dataset Validator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python validate_schema.py dataset/zeron_bench_v1.0_full.json
    python validate_schema.py --manifest splits.json --sample 10
        """
    )
    parser.add_argument("filepath", nargs="?", default=None,
                        help="Path to dataset JSON file")
    parser.add_argument("--manifest", "-m", type=str,
                        help="Path to splits.json manifest file")
    parser.add_argument("--sample", "-s", type=int,
                        help="Number of entries to sample for validation")

    args = parser.parse_args()

    # Determine the dataset path
    if args.filepath:
        dataset_path = args.filepath
    elif args.manifest:
        # Load manifest to find dataset path
        manifest_dir = os.path.dirname(args.manifest) or "."
        dataset_path = os.path.join(manifest_dir, "dataset", "zeron_bench_v1.0_full.json")
        if not os.path.exists(dataset_path):
            # Try relative to current directory
            dataset_path = "dataset/zeron_bench_v1.0_full.json"
    else:
        dataset_path = "dataset/zeron_bench_v1.0_full.json"

    if not os.path.exists(dataset_path):
        print(f"ERROR: Dataset file not found: {dataset_path}")
        print("Usage: python validate_schema.py <path_to_dataset.json>")
        print("   or: python validate_schema.py --manifest splits.json --sample 10")
        sys.exit(1)

    print(f"Loading dataset from: {dataset_path}")

    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    errors, validated, total = validate_dataset(data, args.sample)

    if not errors:
        if args.sample:
            print(f"SUCCESS: Sample {validated} hashes validated successfully (verify on-chain via blockchain/blockchain_proofs.csv)")
        else:
            print(f"SUCCESS: All {validated} entries passed validation.")
    else:
        print(f"FAILED: {len(errors)} errors found.")
        for e in errors[:10]:
            print(f"  - {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
