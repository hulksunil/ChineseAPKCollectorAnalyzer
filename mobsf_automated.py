import json
import os
import time
import requests

# Replace with your actual API key (go to mobsf in browser, then api, and copy the key from top left corner)
MOBSF_API = "fe1e1e62f0adad9aa3ae8d2d792e6c47013fc94eea86ab8cf5a56e0a1910309b"
BASE_PATH = "http://localhost:8000"


def get_processed_files():
    """Get the list of processed files from the JSON file."""
    if os.path.exists("processed_files.json"):
        with open("processed_files.json", "r") as f:
            return json.load(f)
    return []


def save_processed_file(apk_name_without_extension):
    """Save the processed file name to the JSON file."""
    processed_files = get_processed_files()
    processed_files.append(apk_name_without_extension)
    with open("processed_files.json", "w") as f:
        json.dump(processed_files, f, indent=4)


def uploadAPK(apkFilePath):
    """Upload APK to MobSF."""
    url = "/api/v1/upload"

    with open(apkFilePath, 'rb') as apk_file:
        files = {'file': (APK_PATH, apk_file, 'application/octet-stream')}
        headers = {'Authorization': MOBSF_API}
        response = requests.post(BASE_PATH+url, files=files, headers=headers)

        if response.status_code == 200:
            return response.json()['hash']
        else:
            print(f"Failed to upload {apkFilePath}: {response.text}")
            print(f"Status code: {response.status_code}")
            return None


def performScan(scan_hash):
    """Trigger a scan of the uploaded APK."""

    url = "/api/v1/scan"
    response = requests.post(
        BASE_PATH+url, headers={'Authorization': MOBSF_API}, data={'hash': scan_hash})
    if response.status_code == 200:
        print(f"Scan started for hash {scan_hash}.")
        return True
    else:
        print(f"Failed to start scan for {scan_hash}: {response.text}")
        return False


def getReport(scan_hash):
    """Fetch the scan report."""

    url = "/api/v1/report_json"
    response = requests.post(
        BASE_PATH+url, headers={'Authorization': MOBSF_API}, data={'hash': scan_hash})
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get report for {scan_hash}: {response.text}")
        return None


def save_report_to_file(report_data, filename):
    """Save the report data as a JSON file."""

    saveLocation = "reports/"+filename

    # Ensure the 'reports' directory exists
    os.makedirs(os.path.dirname(saveLocation), exist_ok=True)

    with open(saveLocation, 'w') as json_file:
        json.dump(report_data, json_file, indent=4)
    print(f"Report saved to {saveLocation}")


def perform_analysis(APK_PATH):
    """Perform the analysis."""

    apk_name = os.path.basename(APK_PATH)
    apk_name_without_extension = os.path.splitext(apk_name)[0]

    # Check if the APK has already been processed
    processed_files = get_processed_files()

    if apk_name_without_extension in processed_files:
        print(f"{apk_name_without_extension} has already been processed. Skipping.")
        return

    # upload apk file
    scan_hash = uploadAPK(APK_PATH)
    print(f"Uploaded {apk_name_without_extension} with hash: {scan_hash}")

    if scan_hash:
        print("uploadAPK success")

        # Start the scan
        if performScan(scan_hash):
            # Wait for the scan to complete
            print("Waiting for scan to finish...")
            time.sleep(10)  # Wait 10 seconds, adjust as needed
            # Get the report
            report = getReport(scan_hash)
            if report:
                save_report_to_file(report, filename=apk_name+"-report.json")

                # Save the processed file name so we don't reprocess it if we run the script again
                save_processed_file(apk_name_without_extension)
            else:
                print(f"No report generated for {APK_PATH}.")
        else:
            print(f"Scan failed for {APK_PATH}.")
    else:
        print(f"Failed to upload {APK_PATH} to MobSF.")


if __name__ == "__main__":
    # load apk files from the downloads directory
    apk_files = [f for f in os.listdir('./downloads/') if f.endswith('.apk')]

    if not apk_files:
        print("No APK files found in the downloads directory.")
        exit(1)
    else:
        print(f"Found {len(apk_files)} APK files in the downloads directory.")
        print("Starting analysis...")
        for apk_file in apk_files:
            APK_PATH = os.path.join('./downloads/', apk_file)
            print(f"Analyzing {APK_PATH}...")
            perform_analysis(APK_PATH)
            print(f"Finished analyzing {APK_PATH}.\n")
