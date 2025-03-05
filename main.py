from BehavioralBiometricSA.static_analysis.api.static_analysis import analyze
from BehavioralBiometricSA.static_analysis.api.db_utils import export_table_to_csv
import argparse

def main():
    parser = argparse.ArgumentParser(description="Static Analysis API: Process multicore static info table and optionally export to CSV.")
    parser.add_argument('--export', help="Export the `multicore_static_info` table to CSV at the specified directory", type=str, required=False)
    args = parser.parse_args()
    analyze()
    if args.export:
        export_table_to_csv(args.export)

if __name__ == '__main__':
    main()
