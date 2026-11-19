#!/bin/bash
# Genera el dataset oficial y lo carga en retail_dwh. No deja Spark ni Java activos.
set -euo pipefail

PIN="191fd84ad1eb7c890f6b3a83556d7bc583c29f42"
SRC="/opt/retail-data-warehouse"
IMPORT_DIR="/var/lib/postgresql/import"
LAB_SQL="/opt/estudia-lab/sql"

if [[ ! -d "$SRC/.git" ]]; then
  rm -rf "$SRC"
  git clone https://github.com/oleong/retail-data-warehouse.git "$SRC"
fi
git -C "$SRC" checkout "$PIN"
echo "dataset commit: $(git -C "$SRC" rev-parse HEAD)"

python3 -m venv /opt/retail-venv
/opt/retail-venv/bin/pip install --quiet --upgrade pip
/opt/retail-venv/bin/pip install --quiet "numpy>=1.26" "pandas>=2.2"
/opt/retail-venv/bin/python "$SRC/data/raw/generate_data.py"
rm -rf /opt/retail-venv

install -d -o postgres -g postgres -m 750 "$IMPORT_DIR"
install -o postgres -g postgres -m 640 \
  "$SRC/data/raw/products.csv" \
  "$SRC/data/raw/customers.csv" \
  "$SRC/data/raw/stores.csv" \
  "$SRC/data/raw/sales_transactions.csv" \
  "$IMPORT_DIR/"

sudo -u postgres psql -d retail_dwh -v ON_ERROR_STOP=1 \
  -v products_csv="$IMPORT_DIR/products.csv" \
  -v customers_csv="$IMPORT_DIR/customers.csv" \
  -v stores_csv="$IMPORT_DIR/stores.csv" \
  -v sales_csv="$IMPORT_DIR/sales_transactions.csv" \
  -f "$LAB_SQL/02_dataset.sql"

sudo -u postgres psql -d retail_dwh -v ON_ERROR_STOP=1 \
  -v products_csv="$IMPORT_DIR/products.csv" \
  -v customers_csv="$IMPORT_DIR/customers.csv" \
  -v stores_csv="$IMPORT_DIR/stores.csv" \
  -v sales_csv="$IMPORT_DIR/sales_transactions.csv" \
  -f "$LAB_SQL/02_load.sql"

echo "dataset loaded"
