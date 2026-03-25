# Zer0n-Bench Docker Image
# One-command reproducibility for dataset validation

FROM python:3.11-slim

# Set working directory
WORKDIR /zer0n-bench

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Set environment
ENV PYTHONUNBUFFERED=1

# Default command: run validation on sample
CMD ["python", "validation/validate_schema.py", "--manifest", "splits.json", "--sample", "10"]

# Usage examples in README:
# docker run zer0n-bench                                    # Run default (sample 10)
# docker run zer0n-bench python validation/validate_schema.py dataset/zeron_bench_v1.0_full.json  # Full validation
# docker run zer0n-bench python scripts/compute_iaa.py      # Compute IAA
