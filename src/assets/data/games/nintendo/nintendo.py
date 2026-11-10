"""
Nintendo Play History Fetcher
Author: Muntakim Rahman
Description: Interacts with Nintendo's Unofficial Play History API (Same One the Nintendo Store App Uses)
    to Fetch User Data (Played Games, Playtime, First / Last Played).
    Data is Saved to CSV for Backup, with the Same 'name' / 'playtime_forever' Columns as Steam and PSN.
    Visualized as Part of the Combined Games Dashboard (See games.py).

Usage:
    python nintendo.py login   # One Time : Sign In and Save Session Token to .env
    python nintendo.py         # Fetch Play History and Save CSV
    python nintendo.py raw     # Print Raw API Response (For Checking Field Names)

Note: This API is Undocumented and May Change Without Notice.
    The Session Token Works Like Account Credentials (Valid ~2 Years). Keep it Out of Git.
"""

# Import Packages
import pandas as pd

import requests
import json

import base64
import hashlib
import os
import secrets
import sys
from urllib.parse import urlencode, urlparse, parse_qs
from dotenv import load_dotenv

from typing import Optional

PWD = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(PWD, '.env')

class NintendoAPI:
    """Handles Nintendo Account Authentication and Play History API Interactions"""

    CLIENT_ID = '5c38e31cd085304b' # Nintendo Store App
    REDIRECT_URI = f'npf{CLIENT_ID}://auth'
    SCOPE = 'openid user user.mii user.email user.links[].id'

    ACCOUNTS_URL = 'https://accounts.nintendo.com/connect/1.0.0'
    HISTORY_URL = 'https://app-api.znej.nintendo.com/api/v2.0/users/me/play_histories'

    USER_AGENT = 'games-dashboard/0.1'
    TIMEOUT = 30

    PLATFORMS = {
        'BEE': 'Switch 2', # Console Model Prefixes
        'HAC': 'Switch',
    }
    def __init__(self, session_token: Optional[str] = None, locale: str = 'en-US'):
        self.session_token = session_token
        self.locale = locale # Sets Language of Game Names

    @staticmethod
    def _encode(data: bytes) -> str:
        """URL Safe Base64 without Padding"""
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

    def login(self) -> Optional[str]:
        """Interactive Sign In (PKCE) to Get a Long Lived Session Token"""
        verifier = self._encode(secrets.token_bytes(32))
        challenge = self._encode(hashlib.sha256(verifier.encode()).digest())
        state = self._encode(secrets.token_bytes(32))

        params = {
            'client_id': self.CLIENT_ID,
            'redirect_uri': self.REDIRECT_URI,
            'response_type': 'session_token_code',
            'scope': self.SCOPE,
            'state': state,
            'session_token_code_challenge': challenge,
            'session_token_code_challenge_method': 'S256',
        }

        print("1. Open this Link in a Browser and Sign In to Your Nintendo Account:\n")
        print(f"{self.ACCOUNTS_URL}/authorize?{urlencode(params)}\n")
        print("2. On the 'Select this Person' Button : Right Click -> Copy Link Address (Do Not Click It).")
        redirect_url = input("3. Paste the Copied Link Here (Starts with npf...): ").strip()

        fragment = parse_qs(urlparse(redirect_url).fragment)
        if fragment.get('state', [None])[0] != state:
            print("Failed to Sign In: State Mismatch (Link is from a Different Sign In Attempt)")
            return None

        code = fragment.get('session_token_code', [None])[0]
        if not code:
            print("Failed to Sign In: No session_token_code Found in Link")
            return None

        try:
            response = requests.post(
                f"{self.ACCOUNTS_URL}/api/session_token",
                data = {
                    'client_id': self.CLIENT_ID,
                    'session_token_code': code,
                    'session_token_code_verifier': verifier,
                },
                headers = {'User-Agent': self.USER_AGENT},
                timeout = self.TIMEOUT
            )
            response.raise_for_status()

            self.session_token = response.json()['session_token']
            return self.session_token
        except (requests.RequestException, KeyError) as e:
            print(f"Failed to Get Session Token: {e}")
            return None

    def getAccessToken(self) -> Optional[str]:
        """Exchange Session Token for Short Lived Access Token (~15 Min)"""
        try:
            response = requests.post(
                f"{self.ACCOUNTS_URL}/api/token",
                json = {
                    'client_id': self.CLIENT_ID,
                    'session_token': self.session_token,
                    'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer-session-token',
                },
                headers = {'User-Agent': self.USER_AGENT},
                timeout = self.TIMEOUT
            )
            response.raise_for_status()

            return response.json().get('access_token')
        except requests.RequestException as e:
            detail = e.response.text if e.response is not None else ''
            print(f"Failed to Get Access Token: {e} {detail}")
            return None

    def getPlayHistory(self) -> dict:
        """Fetch Raw Play History (Lifetime Totals + Last Week of Daily Records)"""
        access_token = self.getAccessToken()
        if not access_token:
            return {}

        try:
            response = requests.get(
                self.HISTORY_URL,
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/json',
                    'gentry-locale': self.locale,
                    'User-Agent': self.USER_AGENT,
                },
                timeout = self.TIMEOUT
            )
            response.raise_for_status()

            return response.json()
        except requests.RequestException as e:
            detail = e.response.text if e.response is not None else ''
            print(f"Failed to Get Play History: {e} {detail}")
            return {}

    def getTitleStats(self) -> pd.DataFrame:
        """Fetch User's Played Games with Playtime Data"""
        titles = []
        for title in self.getPlayHistory().get('playHistories', []):
            titles.append({
                'title_id': title.get('titleId'), # Unique Identifier for the Game
                'name': title.get('titleName'), # Game Title
                'category': self.PLATFORMS.get(title.get('platform'), title.get('platform') or 'UNKNOWN'), # Platform (Switch / Switch 2)
                'playtime_forever': round(title.get('totalPlayedMinutes', 0) / 60.0, 2), # Total Playtime in Hours
                'played_days': title.get('totalPlayedDays', 0),
                'first_played': title.get('firstPlayedAt'),
                'last_played': title.get('lastPlayedAt'),
            })

        if not titles:
            print("No Title Stats Found")
        return pd.DataFrame(titles)

class NintendoUser:
    """Represents a Nintendo User and Their Gaming Data"""

    CUSTOM_NAMES = {
        'The Legend of Zelda: Breath of the Wild – Nintendo Switch 2 Edition': 'Zelda: Breath of the Wild',
        'The Legend of Zelda: Ocarina of Time': 'Zelda: Ocarina of Time',
        'The Legend of Zelda: Skyward Sword HD': 'Zelda: Skyward Sword',
        'SUPER MARIO ODYSSEY': 'Super Mario Odyssey',
        'Super Mario Party Jamboree – Nintendo Switch 2 Edition + Jamboree TV': 'Super Mario Party Jamboree',
    }

    def __init__(self, username: str, api_client: NintendoAPI):
        self.username = username
        self.api_client = api_client

        # Nintendo Data
        self.stats_df = pd.DataFrame()

        self._getData()

    def _getData(self) -> None:
        """Get All User Data from Nintendo API"""
        stats_df = self.api_client.getTitleStats() if self.api_client.session_token else pd.DataFrame()

        if stats_df.empty:
            print("Error Fetching User Data")
            self._loadFromCSV()
            return

        stats_df['name'] = stats_df['name'].replace(self.CUSTOM_NAMES)
        self.stats_df = stats_df.sort_values('playtime_forever', ascending = False)
        self.saveData()

        print(f"Successfully Fetched Data for {self.username}")
        print(f"Games Played: {self.getNumberPlayed()}")
        print(f"Total Playtime: {self.getTotalPlaytime():.1f} Hrs")

    def _loadFromCSV(self) -> None:
        """Load Data from Backup CSV if API Fails"""
        csv_file = f"{self.username}_NintendoData.csv"
        if os.path.exists(os.path.join(PWD, csv_file)):
            print(f"Loading Data from CSV File: {csv_file}")
            self.stats_df = pd.read_csv(os.path.join(PWD, csv_file))
        else:
            print("No Backup Data Available")

    def saveData(self, filename: Optional[str] = None) -> None:
        """Save User Data to CSV"""
        if filename is None:
            filename = f"{self.username}_NintendoData.csv"

        if not self.stats_df.empty:
            self.stats_df.to_csv(os.path.join(PWD, filename), index = False)
            print(f"Data Saved to {filename}")

    def getTopData(self, n: int = 15) -> pd.DataFrame:
        """Get Top N Games By Playtime"""
        return self.stats_df.nlargest(n, 'playtime_forever')[
            ['name', 'playtime_forever', 'title_id']
        ].sort_values('playtime_forever', ascending = False)

    def getNumberPlayed(self) -> int:
        """Get Number of Games with Playtime > 0"""
        return (self.stats_df['playtime_forever'] > 0).sum()

    def getTotalPlaytime(self) -> float:
        """Get Total Playtime Across Games"""
        return self.stats_df['playtime_forever'].sum()

def saveSessionToken(session_token: str) -> None:
    """Write Session Token to .env (Ignored by Git)"""
    with open(ENV_PATH, 'w') as f:
        f.write(f"NINTENDO_SESSION_TOKEN={session_token}\n")
    os.chmod(ENV_PATH, 0o600)
    print(f"Session Token Saved to {ENV_PATH}")

if __name__ == '__main__':
    load_dotenv(ENV_PATH)

    USERNAME = 'Dipto9999' # Only Used for Naming Files
    COMMAND = sys.argv[1] if len(sys.argv) > 1 else 'fetch'

    api = NintendoAPI(os.getenv("NINTENDO_SESSION_TOKEN"))

    if COMMAND == 'login':
        session_token = api.login()
        if session_token:
            saveSessionToken(session_token)
    elif not api.session_token:
        print("No Session Token Found. Run: python nintendo.py login")
    elif COMMAND == 'raw':
        print(json.dumps(api.getPlayHistory(), indent = 2, ensure_ascii = False))
    else:
        user = NintendoUser(USERNAME, api)
        if not user.stats_df.empty:
            print(user.getTopData(10).to_string(index = False))
