import argparse
import json
import os
import sys
from datetime import datetime
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_URL = "https://api.hevyapp.com/v1"


class HevySync:
    def __init__(self, api_key: str, output_file: str = "hevy_data.json"):
        self.api_key = api_key
        self.output_file = output_file
        self.headers = {
            "api-key": self.api_key,
            "Accept": "application/json"
        }
        self.data = self._load_existing_data()

    def _load_existing_data(self) -> dict:
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[!] Warning: Failed to parse existing {self.output_file} ({e}). Starting fresh.")
        
        return {
            "workouts": {},
            "routines": {},
            "templates": [],
            "measurements": {},
            "last_sync": None
        }

    def _save_data(self):
        self.data["last_sync"] = datetime.now().isoformat()
        os.makedirs(os.path.dirname(os.path.abspath(self.output_file)), exist_ok=True)
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def _get(self, endpoint: str, params: dict = None):
        url = f"{BASE_URL}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                print(f"[!] Unauthorized: Invalid Hevy API Key for {endpoint}")
                return None
            else:
                print(f"[!] Error fetching {endpoint} (HTTP {response.status_code}): {response.text}")
                return None
        except requests.RequestException as e:
            print(f"[!] Network error fetching {endpoint}: {e}")
            return None

    def sync_workouts(self):
        print("-> Syncing workouts...")
        page = 1
        total_fetched = 0

        while True:
            params = {"page": page, "per_page": 50}
            result = self._get("/workouts", params)
            if not result or "workouts" not in result:
                break

            workouts = result["workouts"]
            if not workouts:
                break

            print(f"   Processing page {page} ({len(workouts)} workouts)...")
            for w in workouts:
                w_id = w.get("id")
                if not w_id:
                    continue
                if w_id not in self.data["workouts"]:
                    details = self._get(f"/workouts/{w_id}")
                    if details:
                        self.data["workouts"][w_id] = details
                        total_fetched += 1
                else:
                    self.data["workouts"][w_id] = w

            page_count = result.get("page_count") or result.get("total_pages", 1)
            if page >= page_count:
                break
            page += 1

        print(f"   Done. Total workouts recorded: {len(self.data['workouts'])}")

    def sync_routines(self):
        print("-> Syncing routines...")
        result = self._get("/routines")
        if result and "routines" in result:
            routines = result["routines"]
            for r in routines:
                r_id = r.get("id")
                if not r_id:
                    continue
                if r_id not in self.data["routines"]:
                    details = self._get(f"/routines/{r_id}")
                    if details:
                        self.data["routines"][r_id] = details
                else:
                    self.data["routines"][r_id] = r

        print(f"   Done. Total routines recorded: {len(self.data['routines'])}")

    def sync_measurements(self):
        print("-> Syncing body measurements...")
        page = 1
        while True:
            params = {"page": page, "per_page": 50}
            result = self._get("/body_measurements", params)
            if not result or "body_measurements" not in result:
                break

            measurements = result["body_measurements"]
            if not measurements:
                break

            for m in measurements:
                m_date = m.get("date")
                if m_date:
                    self.data["measurements"][m_date] = m

            page_count = result.get("page_count") or result.get("total_pages", 1)
            has_next = result.get("has_next_page", False)
            if not has_next or page >= page_count:
                break
            page += 1

        print(f"   Done. Total measurements recorded: {len(self.data['measurements'])}")

    def sync_templates(self):
        print("-> Syncing exercise templates...")
        result = self._get("/exercise_templates")
        if result and "exercise_templates" in result:
            self.data["templates"] = result["exercise_templates"]
            print(f"   Done. Total exercise templates: {len(self.data['templates'])}")

    def run(self, sync_workouts=True, sync_routines=True, sync_measurements=True, sync_templates=True):
        if not self.api_key:
            print("[!] Error: No Hevy API key provided.")
            print("    Set the HEVY_API_KEY environment variable or pass --api-key.")
            sys.exit(1)

        print(f"[*] Starting Hevy data sync...")
        if sync_workouts:
            self.sync_workouts()
        if sync_routines:
            self.sync_routines()
        if sync_measurements:
            self.sync_measurements()
        if sync_templates:
            self.sync_templates()

        self._save_data()
        print(f"[✓] Sync completed successfully! Data saved to {self.output_file}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Sync and backup workout data from Hevy to a JSON file."
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=os.getenv("HEVY_API_KEY"),
        help="Hevy API Key (defaults to HEVY_API_KEY environment variable)",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="hevy_data.json",
        help="Path to output JSON file (default: hevy_data.json)",
    )
    parser.add_argument(
        "--skip-workouts",
        action="store_true",
        help="Skip syncing workouts",
    )
    parser.add_argument(
        "--skip-routines",
        action="store_true",
        help="Skip syncing routines",
    )
    parser.add_argument(
        "--skip-measurements",
        action="store_true",
        help="Skip syncing body measurements",
    )
    parser.add_argument(
        "--skip-templates",
        action="store_true",
        help="Skip syncing exercise templates",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    sync = HevySync(api_key=args.api_key, output_file=args.output)
    sync.run(
        sync_workouts=not args.skip_workouts,
        sync_routines=not args.skip_routines,
        sync_measurements=not args.skip_measurements,
        sync_templates=not args.skip_templates,
    )


if __name__ == "__main__":
    main()
