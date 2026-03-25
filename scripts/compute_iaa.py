"""
Zer0n-Bench: Inter-Annotator Agreement (IAA) Computation
Computes Fleiss' Kappa and Cohen's Kappa for expert annotations.

Usage:
    python compute_iaa.py [path_to_iaa_results.csv]

Default: validation/iaa_results.csv
"""

import csv
import collections
import sys
import os

# ==========================================
# CONFIGURATION
# ==========================================
DEFAULT_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'validation', 'iaa_results.csv'))


def load_data(filepath):
    """Load IAA data from CSV file."""
    rows_data = []
    expert_cols = ['Expert_A', 'Expert_B', 'Expert_C', 'Expert_D']

    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            labels = []
            for col in expert_cols:
                v = row.get(col, '')
                if v:
                    v = str(v).strip().lower()
                    if 'vuln' in v:
                        labels.append('Vulnerable')
                    elif 'safe' in v:
                        labels.append('Safe')
                    else:
                        labels.append(None)
                else:
                    labels.append(None)

            rows_data.append({
                'target_id': row.get('target_id', ''),
                'category': row.get('category', 'Unknown'),
                'labels': labels
            })

    return rows_data, len(expert_cols)


def fleiss_kappa(data, n_raters):
    """
    Compute Fleiss' Kappa for multiple raters.
    data: list of dicts with counts per category
    """
    N = len(data)
    k = n_raters

    # Get all categories
    categories = set()
    for d in data:
        categories.update(d.keys())
    categories = sorted(categories)
    n_cat = len(categories)

    # Build matrix
    matrix = []
    for d in data:
        row = [d.get(c, 0) for c in categories]
        matrix.append(row)

    # Compute P_i for each subject
    P_i = []
    for row in matrix:
        p = (sum(n_j**2 for n_j in row) - k) / (k * (k - 1))
        P_i.append(p)

    P_bar = sum(P_i) / N

    # Compute P_j for each category
    p_j = []
    for j in range(n_cat):
        total = sum(matrix[i][j] for i in range(N))
        p_j.append(total / (N * k))

    P_e = sum(pj**2 for pj in p_j)

    if P_e == 1:
        return 1.0

    kappa = (P_bar - P_e) / (1 - P_e)
    return kappa


def cohen_kappa(labels1, labels2):
    """Cohen's kappa for two raters."""
    if len(labels1) != len(labels2):
        raise ValueError(f"Label lists must be equal length: {len(labels1)} vs {len(labels2)}")
    n = len(labels1)

    cats = sorted(set(labels1) | set(labels2))

    # Observed agreement
    agree = sum(1 for a, b in zip(labels1, labels2) if a == b)
    p_o = agree / n

    # Expected agreement
    p_e = 0
    for c in cats:
        p1 = sum(1 for l in labels1 if l == c) / n
        p2 = sum(1 for l in labels2 if l == c) / n
        p_e += p1 * p2

    if p_e == 1:
        return 1.0

    return (p_o - p_e) / (1 - p_e)


def main():
    # Get file path
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = DEFAULT_PATH

    if not os.path.exists(filepath):
        print(f"ERROR: File not found: {filepath}")
        print(f"Usage: python compute_iaa.py [path_to_iaa_results.csv]")
        sys.exit(1)

    print(f"Loading data from: {filepath}")
    rows_data, n_raters = load_data(filepath)

    print(f"Total rows: {len(rows_data)}")

    # Filter complete entries (all 4 expert labels present)
    complete = [r for r in rows_data if all(l is not None for l in r['labels'])]
    print(f"Rows with all {n_raters} expert labels: {len(complete)}")

    # Label distribution
    label_counts = collections.Counter()
    for r in complete:
        for l in r['labels']:
            label_counts[l] += 1
    print(f"Label distribution: {dict(label_counts)}")

    # Category distribution
    cat_counts = collections.Counter(r['category'] for r in complete)
    print(f"Category distribution: {dict(cat_counts)}")

    # === COMPUTE FLEISS' KAPPA ===
    print(f"\n{'='*60}")
    print(f"COMPUTING IAA FOR {n_raters} RATERS ON {len(complete)} ENTRIES")
    print(f"{'='*60}")

    # Overall Fleiss' kappa
    fleiss_data = []
    for r in complete:
        counts = collections.Counter(r['labels'])
        fleiss_data.append(dict(counts))

    overall_kappa = fleiss_kappa(fleiss_data, n_raters)
    print(f"\n*** OVERALL Fleiss' Kappa: {overall_kappa:.4f} ***")

    # Percentage agreement
    total_pairs = 0
    agree_pairs = 0
    for r in complete:
        labels = r['labels']
        for i in range(len(labels)):
            for j in range(i+1, len(labels)):
                total_pairs += 1
                if labels[i] == labels[j]:
                    agree_pairs += 1
    pct_agree = agree_pairs / total_pairs * 100
    print(f"*** Overall % Agreement: {pct_agree:.1f}% ***")

    # Per-category Fleiss' kappa
    print(f"\n--- Per-Category Fleiss' Kappa ---")
    for cat in sorted(cat_counts.keys()):
        cat_entries = [r for r in complete if r['category'] == cat]
        if len(cat_entries) < 5:
            print(f"  {cat}: Too few entries ({len(cat_entries)})")
            continue

        cat_fleiss = []
        for r in cat_entries:
            counts = collections.Counter(r['labels'])
            cat_fleiss.append(dict(counts))

        k = fleiss_kappa(cat_fleiss, n_raters)

        # % agreement for this category
        tp = ap = 0
        for r in cat_entries:
            labels = r['labels']
            for i in range(len(labels)):
                for j in range(i+1, len(labels)):
                    tp += 1
                    if labels[i] == labels[j]:
                        ap += 1
        pct = ap/tp*100 if tp > 0 else 0

        print(f"  {cat}: kappa={k:.4f}, %agree={pct:.1f}%, n={len(cat_entries)}")

    # Pairwise Cohen's kappa
    print(f"\n--- Pairwise Cohen's Kappa ---")
    kappas = []
    for i in range(n_raters):
        for j in range(i+1, n_raters):
            l1 = [r['labels'][i] for r in complete]
            l2 = [r['labels'][j] for r in complete]
            k = cohen_kappa(l1, l2)
            kappas.append(k)
            print(f"  Expert_{chr(65+i)} vs Expert_{chr(65+j)}: kappa={k:.4f}")

    mean_cohen = sum(kappas) / len(kappas)
    print(f"\n*** Mean Pairwise Cohen's Kappa: {mean_cohen:.4f} ***")

    print(f"\n{'='*60}")
    print("SUMMARY FOR PAPER:")
    print(f"  Fleiss' Kappa (overall): {overall_kappa:.2f}")
    print(f"  Mean Cohen's Kappa: {mean_cohen:.2f}")
    print(f"  % Agreement: {pct_agree:.1f}%")
    print(f"  Number of complete entries: {len(complete)}")
    print(f"  Number of raters: {n_raters}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
