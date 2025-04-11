import json
import os
import time
import requests

# Replace with your actual API key (go to mobsf in browser, then api, and copy the key from top left corner)
MOBSF_API = "7eed554cb4a62b0cbf77668108b91d9b0413879c3f61007c98d8fbe52b6be784"
BASE_PATH = "http://localhost:8000"


def is_mobsf_running():
    try:
        response = get_mobsf_ping_response()
        if response == 200:
            return True
        elif response == 401:
            print("Unauthorized access. Check your API key.")
            return False
        else:
            print("Mobsf returned an unexpected status code:", response)
            return False
    except requests.ConnectionError:
        print("MobSF is not running. Please start MobSF and try again.")
        return False
    except requests.Timeout:
        print("Connection to MobSF timed out.")
        return False


def get_mobsf_ping_response():
    headers = {'Authorization': MOBSF_API}

    response = requests.get(
        "http://localhost:8000/api/v1/dynamic/get_apps", headers=headers, timeout=3)

    return response.status_code


def get_analyzed_files():
    """Get the list of analyzed files from the JSON file."""
    if os.path.exists("analyzed_files.json"):
        with open("analyzed_files.json", "r") as f:
            return json.load(f)
    return []


def save_analyzed_file(apk_name_without_extension):
    """Save the analyzed file name to the JSON file."""
    analyzed_files = get_analyzed_files()
    analyzed_files.append(apk_name_without_extension)
    with open("analyzed_files.json", "w") as f:
        json.dump(analyzed_files, f, indent=4)


def generate_summary_from_report(report_data):
    """Extract and print a summary of key static analysis findings from the MobSF JSON report."""

    app = {}
    app["name"] = report_data.get("app_name", "Unknown App")
    app["size"] = report_data.get("size", "Unknown Size")
    app["package_name"] = report_data.get("package_name", "Unknown Package")
    app["version"] = report_data.get("version_name", "Unknown Version")
    app["dangerous_permissions"] = []
    app["unknown_permissions"] = []
    app["hardcoded_secrets"] = []
    app["urls"] = []
    app["manifest_high_issues"] = []
    app["manifest_warning_issues"] = []

    # 1. Permissions
    permissions = report_data.get("permissions", {})

    for perm, data in permissions.items():
        if "dangerous" in data.get("status", "").lower():
            app["dangerous_permissions"].append(
                {"permission": perm, "description": data.get("description")})
        elif "unknown" in data.get("status", "").lower():
            app["unknown_permissions"].append(
                {"permission": perm, "description": data.get("description")})

    # 2. Secrets / Hardcoded strings
    secrets = report_data.get("secrets", [])
    app["hardcoded_secrets"] = secrets

    # 3. Network Security
    urls = report_data.get("urls", [])
    app["urls"] = urls

    # 5. Manifest Issues
    manifest_findings = report_data.get(
        "manifest_analysis", {}).get("manifest_findings", [])

    for finding in manifest_findings:
        if finding.get("severity") == "high":
            app["manifest_high_issues"].append(
                {"title": finding["title"], "description": finding["description"]})
        elif finding.get("severity") == "warning":
            app["manifest_warning_issues"].append(
                {"title": finding["title"], "description": finding["description"]})

    return app


def uploadAPK(apkFilePath):
    """Upload APK to MobSF."""
    url = "/api/v1/upload"

    with open(apkFilePath, 'rb') as apk_file:
        files = {'file': (apkFilePath, apk_file, 'application/octet-stream')}
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
    processed_files = get_analyzed_files()

    if apk_name_without_extension in processed_files:
        print(f"{apk_name_without_extension} has already been processed. Skipping.")
        return

    print(f"Uploading {apk_name}...")
    # upload apk file
    scan_hash = uploadAPK(APK_PATH)
    print(f"Uploaded {apk_name} with hash: {scan_hash}")

    if scan_hash:
        print(f"Performing scan on {apk_name}...")

        # Start the scan
        if performScan(scan_hash):
            # Wait for the scan to complete
            print("Waiting for scan to finish...")
            time.sleep(10)  # Wait 10 seconds, adjust as needed

            # Get the report
            print(f"Fetching report for {apk_name}...")
            report = getReport(scan_hash)

            # analyze the report
            app_summary = generate_summary_from_report(report)

            if report:
                save_report_to_file(
                    app_summary, filename=apk_name+"-report.json")

                # Save the processed file name so we don't reprocess it if we run the script again
                save_analyzed_file(apk_name_without_extension)
            else:
                print(f"No report generated for {APK_PATH}.")
        else:
            print(f"Scan failed for {APK_PATH}.")
    else:
        print(f"Failed to upload {APK_PATH} to MobSF.")


if __name__ == "__main__":

    # Check if MobSF is running
    if not is_mobsf_running():
        exit(1)

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
