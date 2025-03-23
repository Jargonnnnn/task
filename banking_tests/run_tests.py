#!/usr/bin/env python
import os
import sys
import subprocess
from pathlib import Path
import json

def main():
    """Run the banking application tests with JSON reporting."""
    # Change to the script's directory to ensure correct relative paths
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    print("\nRunning banking application tests...")
    
    # Create results directory if it doesn't exist
    results_dir = script_dir / "results"
    results_dir.mkdir(exist_ok=True)
    
    # Set environment variable for JSON report output
    os.environ["PLAYWRIGHT_JSON_OUTPUT_NAME"] = str(results_dir / "playwright_report.json")
    
    try:
        # Run the tests
        test_result = subprocess.run(
            [sys.executable, "-m", "pytest", "test_banking.py", "-v", "-p", "no:cov"], 
            check=False  # Don't raise exception on test failure
        )
        
        # Check if the JSON report file exists
        json_report_path = script_dir / "test_results.json"
        if json_report_path.exists():
            # Read the JSON report
            with open(json_report_path, 'r') as f:
                report_data = json.load(f)
                
            # Summary stats
            summary = report_data.get('summary', {})
            total = summary.get('total', 0)
            passed = summary.get('passed', 0)
            failed = summary.get('failed', 0)
            skipped = summary.get('skipped', 0)
            
            print("\nTest Results Summary:")
            print(f"Total tests: {total}")
            print(f"Passed: {passed}")
            print(f"Failed: {failed}")
            print(f"Skipped: {skipped}")
            print(f"\nDetailed JSON report saved to: {json_report_path}")
            
            # Copy the report to the results directory for archiving
            with open(results_dir / "test_results.json", 'w') as f:
                json.dump(report_data, f, indent=2)
        
        # Return proper exit code based on test results
        if test_result.returncode != 0:
            print("Some tests failed. Check the JSON report for details.")
            return 1
        else:
            print("All tests passed!")
            return 0
            
    except subprocess.CalledProcessError as e:
        print(f"Error during execution: {e}")
        return 1
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())