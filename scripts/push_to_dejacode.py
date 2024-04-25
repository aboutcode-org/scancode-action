# SPDX-License-Identifier: Apache-2.0
#
# http://nexb.com and https://github.com/nexB/scancode.io
# The ScanCode.io software is licensed under the Apache License version 2.0.
# Data generated with ScanCode.io is provided as-is without warranties.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# Data Generated with ScanCode.io is provided on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, either express or implied. No content created from
# ScanCode.io should be considered or used as legal advice. Consult an Attorney
# for any legal advice.
#
# ScanCode.io is a free software code scanning tool from nexB Inc. and others.
# Visit https://github.com/nexB/scancode.io for support and download.

from pathlib import Path
import requests
import os

DEJACODE_URL = os.environ["DEJACODE_URL"]
DEJACODE_API_KEY = os.environ["DEJACODE_API_KEY"]

if not (DEJACODE_URL and DEJACODE_API_KEY):
    raise EnvironmentError("Missing required env vars.")

DEJACODE_API_URL = f"{DEJACODE_URL.rstrip('/')}/api/"
PRODUCTS_API_URL = f"{DEJACODE_API_URL}v2/products/"
DEFAULT_TIMEOUT = 10

session = requests.Session()
if DEJACODE_API_KEY:
    session.headers.update({"Authorization": f"Token {DEJACODE_API_KEY}"})


def request_post(url, **kwargs):
    """Return the response from an HTTP POST request on the provided `url` ."""
    if "timeout" not in kwargs:
        kwargs["timeout"] = DEFAULT_TIMEOUT

    # Do not `raise_for_status` as the response may contain valuable data
    # even on non 200 status code.
    try:
        response = session.post(url, **kwargs)
        return response.json()
    except (requests.RequestException, ValueError, TypeError) as exception:
        print(f"[Exception] {exception}")


def create_product(product_data):
    response = request_post(PRODUCTS_API_URL, data=product_data)
    print(response)
    return response["uuid"]


def push_scan_to_product(files):
    url = f"{PRODUCTS_API_URL}{product_uuid}/import_from_scan/"
    response = request_post(url, files=files)
    print(response)


if __name__ == "__main__":
    product_data = {
        "name": "Demo Push Product",
        "version": "1.0",
    }
    product_uuid = create_product(product_data)

    # Replace by args
    PROJECT_OUTPUTS = os.environ["PROJECT_OUTPUTS"]
    scan_location = list(Path(PROJECT_OUTPUTS).glob("*.json"))[0]
    print(scan_location)

    files = {"upload_file": open(scan_location, "rb")}
    push_scan_to_product(files)
