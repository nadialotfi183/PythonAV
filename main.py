from ingestion import read
from processing import extract_tranform 


if __name__ == "__main__":
    rows = read.ingest('./data')
    if rows:
        extract_tranform.extract(rows[1])