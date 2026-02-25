"""
Spotify Dashboard Generator
Author: Muntakim Rahman
Description: Interacts with Spotify API to Fetch User Data
    (Total Playtime, Recently Played, Top Tracks/Artists) and Generates Visualizations using Altair.
    Data is Saved to CSV for Backup and Dashboard is Exported as JSON, HTML, PNG, SVG.
"""

# Import Packages
import pandas as pd
import altair as alt

import json
import shutil

import os
from dotenv import load_dotenv

from datetime import datetime, timezone
from typing import Optional

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from IPython.display import display

class SpotifyAPI:
    """Handles Spotify API Interactions"""

    SCOPES = [
        "user-read-recently-played", # Recently Played Tracks
        "user-top-read", # Top Tracks and Artists
        "user-library-read" # Saved/Liked Tracks (Your Music Library)
    ]

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = (redirect_uri).strip().rstrip("/") # Remove Trailing Slash

        # Initialize Spotipy Client with OAuth
        self.client = spotipy.Spotify(
            auth_manager = SpotifyOAuth(
                scope = " ".join(self.SCOPES),
                client_id = self.client_id,
                client_secret = self.client_secret,
                redirect_uri = self.redirect_uri,
            )
        )

    def _parseTrack(self, track: dict) -> dict:
        """Parse Track Data Structure"""
        return {
            "id": track["id"],
            "track": track["name"],
            "album": track["album"]["name"],
            "album_image": (track["album"]["images"][0]["url"] if track["album"]["images"] else None),
            "artists": ", ".join(a["name"] for a in track["artists"]),
            "duration_ms": track["duration_ms"],
            "spotify_url": track["external_urls"]["spotify"],
        }

    def _parseArtist(self, a: dict) -> dict:
        """Parse Artist Data Structure"""
        return {
            "id": a["id"],
            "name": a["name"],
            "genres": ", ".join(a.get("genres", [])),
            "popularity": a.get("popularity", 0),
            "followers": a.get("followers", {}).get("total", 0),
            "image": (a["images"][0]["url"] if a.get("images") else None),
            "spotify_url": a["external_urls"]["spotify"],
        }

    def _getSavedTrackBatch(self, batch_size: int, offset: int) -> pd.DataFrame:
        """Fetch User's Saved/Liked Tracks in Batches (for Pagination)"""
        try:
            saved_tracks = self.client.current_user_saved_tracks(limit = batch_size, offset = offset)
            saved_rows = []

            for item in saved_tracks.get("items", []):
                track_data = self._parseTrack(item["track"])

                # Debug: Check if added_at exists and capture it
                added_at_value = item.get("added_at")
                if added_at_value is None:
                    print(f"Warning: added_at is None for track: {track_data.get('track', 'Unknown')}")
                    # For debugging, print the item structure (first few items only)
                    if offset < 5:  # Only print for first batch
                        print(f"Item keys: {list(item.keys())}")

                track_data["added_at"] = added_at_value
                saved_rows.append(track_data)

            return pd.DataFrame(saved_rows)
        except Exception as e:
            print(f"Failed to Get Saved Tracks: {e}")
            return pd.DataFrame()

    def getTopTracks(self, time_range: str = "long_term", limit: int = 10) -> pd.DataFrame:
        """Fetch User's Top Tracks"""
        try:
            tracks = self.client.current_user_top_tracks(limit = limit, time_range = time_range)
            return pd.DataFrame([self._parseTrack(t) for t in tracks.get("items", [])] )
        except Exception as e:
            print(f"Failed to Get Top Tracks ({time_range}): {e}")
            return pd.DataFrame()

    def getTopArtists(self, time_range: str = "long_term", limit: int = 10) -> pd.DataFrame:
        """Fetch User's Top Artists"""
        try:
            artists = self.client.current_user_top_artists(limit = limit, time_range = time_range)
            return pd.DataFrame([self._parseArtist(a) for a in artists.get("items", [])])
        except Exception as e:
            print(f"Failed to Get Top Artists ({time_range}): {e}")
            return pd.DataFrame()

    def getRecentTracks(self, limit: int = 25) -> pd.DataFrame:
        """Fetch User's Recently Played Tracks"""
        try:
            recent_tracks = self.client.current_user_recently_played(limit = limit)
            recent_rows = []

            for track_info in recent_tracks.get("items", []):
                row = self._parseTrack(track_info["track"])
                row["played_at"] = track_info.get("played_at")
                recent_rows.append(row)

            return pd.DataFrame(recent_rows)
        except Exception as e:
            print(f"Failed to Get Recent Tracks: {e}")
            return pd.DataFrame()

    def getSavedTracks(self) -> pd.DataFrame:
        """Fetch User's Saved Tracks (Handles Pagination). Used to Retrieve 1K+ Liked Songs."""
        try:
            tracks = []
            offset = 0
            batch_size = 50

            while True:
                batch = self._getSavedTrackBatch(batch_size = batch_size, offset = offset)
                if batch.empty: # Assume All Tracks Retrieved
                    break

                tracks.append(batch)
                offset += batch_size

            if tracks: # Concatenate Batches
                return pd.concat(tracks, ignore_index = True)
            return pd.DataFrame()

        except Exception as e:
            print(f"Failed to Get All Saved Tracks: {e}")
            return pd.DataFrame()

class SpotifyUser:
    """Represents a Spotify User and Their Music Data"""

    def __init__(self, username: str, api_client: SpotifyAPI):
        self.username = username
        self.api_client = api_client

        # Spotify Data
        self.recent_df = pd.DataFrame()

        self.top_tracks_short_df = pd.DataFrame()
        self.top_tracks_long_df = pd.DataFrame()

        self.top_artists_short_df = pd.DataFrame()
        self.top_artists_long_df = pd.DataFrame()

        self.stats_df = pd.DataFrame()
        self.saved_tracks_df = pd.DataFrame()

        # Statistics
        self.total_hours = 0.0
        self.stats = {}

        self._getData()

    def _getData(self) -> None:
        """Get All User Data from Spotify API"""
        try:
            print(f"Fetching Spotify Data for {self.username}...")

            self.recent_df = self.api_client.getRecentTracks()

            self.top_tracks_short_df = self.api_client.getTopTracks("short_term")
            self.top_tracks_long_df = self.api_client.getTopTracks("long_term")

            self.top_artists_short_df = self.api_client.getTopArtists("short_term")
            self.top_artists_long_df = self.api_client.getTopArtists("long_term")

            self.saved_tracks_df = self.api_client.getSavedTracks()

            self._compileStats()

            print(f"Successfully Fetched Data for {self.username}")
            print(f"Recent Tracks: {len(self.recent_df)}")
            print(f"Top Tracks (Long Term): {len(self.top_tracks_long_df)}")
            print(f"Top Artists (Long Term): {len(self.top_artists_long_df)}")
            print(f"Saved/Liked Tracks: {len(self.saved_tracks_df)}")

        except Exception as e:
            print(f"Error Fetching User Data: {e}")
            self._loadFromCSV()

    def _loadFromCSV(self) -> None:
        """Load Data from Backup CSV if API Fails"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file = os.path.join(script_dir, f"{self.username}_SpotifyData.csv")

        if os.path.exists(csv_file):
            print(f"Loading Data from CSV File: {csv_file}")
            try:
                self.stats_df = pd.read_csv(csv_file)
                if not self.stats_df.empty:

                    self.total_hours = self.stats_df.get('total_hours', [0]).iloc[0] if 'total_hours' in self.stats_df.columns else 0
                print("Data Loaded from CSV Backup")
            except Exception as e:
                print(f"Error Loading from CSV: {e}")
        else:
            print("No Backup Data Available")

    def _compileStats(self) -> None:
        """Compile Stats from All Data Sources"""
        if self.top_tracks_long_df.empty:
            print("No Track Data Available for Stats")
            return

        # Calculate annual listening hours from long-term top tracks
        annual_ms = self.top_tracks_long_df['duration_ms'].sum() if not self.top_tracks_long_df.empty else 0
        self.total_hours = round(annual_ms * 2.5 / (1000 * 60 * 60), 1)  # 2.5x multiplier for full year estimate

        # Get last played timestamp
        last_played_at = None
        if not self.recent_df.empty:
            last_played_at = self.recent_df.iloc[0].get('played_at') if 'played_at' in self.recent_df.columns else None

        # Compile comprehensive stats
        self.stats = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_recent_plays": len(self.recent_df),
            "n_songs": len(self.top_tracks_long_df),
            "n_artists": len(self.top_artists_long_df),
            "top_artist_long": self.top_artists_long_df.iloc[0]['name'] if not self.top_artists_long_df.empty else "—",
            "top_track_long": f"{self.top_tracks_long_df.iloc[0]['track']} — {self.top_tracks_long_df.iloc[0]['artists']}" if not self.top_tracks_long_df.empty else "—",
            "last_played_at": last_played_at,
        }

        # Create comprehensive stats dataframe for saving
        self.stats_df = pd.DataFrame([{
            'username': self.username,
            'total_hours': self.total_hours,
            'total_recent_plays': self.stats["total_recent_plays"],
            'n_songs': self.stats["n_songs"],
            'n_artists': self.stats["n_artists"],
            'top_artist_long': self.stats["top_artist_long"],
            'top_track_long': self.stats["top_track_long"],
            'last_played_at': self.stats["last_played_at"],
            'generated_at': self.stats["generated_at"]
        }])

        self.saveData()

    def saveData(self, filename: Optional[str] = None) -> None:
        """Save User Data to CSV"""
        if filename is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            filename = os.path.join(script_dir, f"{self.username}_SpotifyData.csv")

        if not self.stats_df.empty:
            self.stats_df.to_csv(filename, index=False)
            print(f"Data Saved to {filename}")

    def saveCSVData(self) -> None:
        """Save Individual Data Components to CSV"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        charts_dir = os.path.join(script_dir, "Charts")
        os.makedirs(charts_dir, exist_ok=True)

        if not self.recent_df.empty:
            self.recent_df.to_csv(os.path.join(charts_dir, "recently_played.csv"), index=False)

        if not self.top_tracks_long_df.empty:
            self.top_tracks_long_df.to_csv(os.path.join(charts_dir, "top_tracks_long_term.csv"), index=False)

        if not self.top_artists_long_df.empty:
            self.top_artists_long_df.to_csv(os.path.join(charts_dir, "top_artists_long_term.csv"), index=False)

    def getTopTracks(self, n: int = 10, time_range: str = "long_term") -> pd.DataFrame:
        """Get Top N Tracks by Time Range"""
        df_map = {
            "short_term": self.top_tracks_short_df,
            "long_term": self.top_tracks_long_df
        }
        df = df_map.get(time_range, self.top_tracks_long_df)
        return df.head(n) if not df.empty else pd.DataFrame()

    def getTopArtists(self, n: int = 10, time_range: str = "long_term") -> pd.DataFrame:
        """Get Top N Artists by Time Range"""
        df_map = {
            "short_term": self.top_artists_short_df,
            "long_term": self.top_artists_long_df
        }
        df = df_map.get(time_range, self.top_artists_long_df)
        return df.head(n) if not df.empty else pd.DataFrame()

    def getTotalHours(self) -> float:
        """Get Total Estimated Annual Listening Hours"""
        return self.total_hours

    # NEW: Profile & Saved Tracks Analysis Methods
    def getLibrarySize(self) -> int:
        """Get total number of saved/liked tracks in user's library"""
        return len(self.saved_tracks_df)

    def getLibraryDiversity(self) -> dict:
        """Analyze diversity of saved tracks library"""
        if self.saved_tracks_df.empty:
            return {"unique_artists": 0, "unique_albums": 0, "avg_duration_min": 0}

        return {
            "unique_artists": self.saved_tracks_df['artists'].nunique(),
            "unique_albums": self.saved_tracks_df['album'].nunique(),
            "avg_duration_min": round(self.saved_tracks_df['duration_ms'].mean() / (1000 * 60), 2),
            "total_duration_hours": round(self.saved_tracks_df['duration_ms'].sum() / (1000 * 60 * 60), 2)
        }

    def getLibraryGrowthPattern(self, period: str = 'M') -> pd.DataFrame:
        """Analyze when tracks were added to library (music discovery timeline)

        Args:
            period: 'M' for monthly, 'Y' for yearly, 'Q' for quarterly
        """
        if self.saved_tracks_df.empty:
            print(f"Debug: saved_tracks_df is empty (length: {len(self.saved_tracks_df)})")
            return pd.DataFrame()

        if 'added_at' not in self.saved_tracks_df.columns:
            print(f"Debug: 'added_at' column missing. Available columns: {list(self.saved_tracks_df.columns)}")
            return pd.DataFrame()

        # Check for None values in added_at
        none_count = self.saved_tracks_df['added_at'].isna().sum()
        if none_count > 0:
            print(f"Warning: {none_count}/{len(self.saved_tracks_df)} tracks have None/NaN added_at values")
            # Filter out None values
            df = self.saved_tracks_df[self.saved_tracks_df['added_at'].notna()].copy()
            if df.empty:
                print("Error: All added_at values are None! Cannot generate growth pattern.")
                return pd.DataFrame()
        else:
            df = self.saved_tracks_df.copy()

        # Convert added_at to datetime and analyze patterns
        try:
            df['added_at'] = pd.to_datetime(df['added_at'])
            df['time_period'] = df['added_at'].dt.to_period(period)
        except Exception as e:
            print(f"Error converting added_at to datetime: {e}")
            return pd.DataFrame()

        growth_pattern = df.groupby('time_period').agg({
            'track': 'count',
            'duration_ms': 'sum'
        }).rename(columns={'track': 'tracks_added', 'duration_ms': 'total_duration_ms'})

        growth_pattern['hours_added'] = growth_pattern['total_duration_ms'] / (1000 * 60 * 60)
        growth_pattern = growth_pattern.reset_index()

        # Convert Period to string for JSON serialization
        growth_pattern['time_period'] = growth_pattern['time_period'].astype(str)

        # Calculate cumulative totals for area chart
        growth_pattern = growth_pattern.sort_values('time_period')
        growth_pattern['cumulative_tracks'] = growth_pattern['tracks_added'].cumsum()
        growth_pattern['cumulative_hours'] = growth_pattern['hours_added'].cumsum()

        # For yearly data: compute cumulative distinct artists up to each year
        if period == 'Y' and 'artists' in df.columns:
            seen_artists: set = set()
            cumulative_artists: dict = {}
            for yr_str in sorted(growth_pattern['time_period'].unique()):
                yr_mask = df['time_period'].astype(str) <= yr_str
                artists_up_to_year: set = set()
                for artists_str in df.loc[yr_mask, 'artists'].dropna():
                    for a in str(artists_str).split(', '):
                        if a.strip():
                            artists_up_to_year.add(a.strip())
                cumulative_artists[yr_str] = len(artists_up_to_year)
            growth_pattern['cumulative_artists'] = growth_pattern['time_period'].map(cumulative_artists).fillna(0).astype(int)

        print(f"Debug: Generated {len(growth_pattern)} {period} growth data points")
        return growth_pattern

    # Map known collaboration / variant artist names → canonical name.
    # Tracks credited to these names will count toward the canonical artist's total.
    _ARTIST_ALIASES: dict = {
        "Alka Yagnik & Arvind Hasabnish": "Alka Yagnik",
    }

    def _normalizeArtist(self, name: str) -> str:
        """Return the canonical artist name, resolving known aliases."""
        return self._ARTIST_ALIASES.get(name, name)

    def getTopSavedArtists(self, n: int = 10) -> pd.DataFrame:
        """Get most saved/liked artists from library, with alias consolidation."""
        if self.saved_tracks_df.empty:
            return pd.DataFrame()

        # Split comma-separated artist credits, then normalize each name
        all_artists = []
        for artists_str in self.saved_tracks_df['artists']:
            for artist in artists_str.split(','):
                all_artists.append(self._normalizeArtist(artist.strip()))

        artist_counts = pd.Series(all_artists).value_counts().head(n).reset_index()
        artist_counts.columns = ['artist', 'saved_tracks_count']
        return artist_counts

    def getComprehensiveData(self) -> dict:
        """Get All Data in Dictionary Format (for JSON export)"""
        return {
            "generated_at": self.stats.get("generated_at"),
            "username": self.username,
            "recently_played": self.recent_df.to_dict('records') if not self.recent_df.empty else [],
            "top_tracks_short": self.top_tracks_short_df.to_dict('records') if not self.top_tracks_short_df.empty else [],
            "top_tracks_long": self.top_tracks_long_df.to_dict('records') if not self.top_tracks_long_df.empty else [],
            "top_artists_short": self.top_artists_short_df.to_dict('records') if not self.top_artists_short_df.empty else [],
            "top_artists_long": self.top_artists_long_df.to_dict('records') if not self.top_artists_long_df.empty else [],
            "total_hours": self.total_hours,
            "stats": self.stats,

            # NEW: Rich Profile & Library Data
            "saved_tracks": self.saved_tracks_df.to_dict('records') if not self.saved_tracks_df.empty else [],
            "library_stats": {
                "total_saved_tracks": self.getLibrarySize(),
                "diversity_metrics": self.getLibraryDiversity(),
                "top_saved_artists": self.getTopSavedArtists(10).to_dict('records') if not self.saved_tracks_df.empty else [],
                "library_growth_timeline": self.getLibraryGrowthPattern('M').to_dict('records') if not self.saved_tracks_df.empty else [],
                "library_growth_yearly": self.getLibraryGrowthPattern('Y').to_dict('records') if not self.saved_tracks_df.empty else []
            }
        }
class SpotifyDashboard:
    """Creates Visualizations for Spotify User Data"""

    # Explicit artist-pie color palette (matches Steam dashboard style)
    ARTIST_COLORS = [
        "#00008B", "#FF8C00", "#32CD32", "#DC143C",
        "#800080", "#00CED1", "#FFA500", "#4E342E",
        "#00695C", "#B8860B",
    ]
    GREEN = "#0e7a38"  # Darkened Spotify green

    def __init__(self, user: SpotifyUser):
        self.user = user
        self.colors = [
            "#0e7a38", "#1ED760", "#191414", "#FFFFFF",
            "#535353", "#B3B3B3", "#000000", "#FF6B35",
            "#F037A5", "#7856FF", "#2D46B9", "#509BF5",
            "#FFD23F", "#FF4632", "#AF2896"
        ]

        self.dashboard = None
        self.generateDashboard()

    def _annual_stats_chart(self, width: int = 740, height: int = 52, font_scale: float = 1.0) -> alt.Chart:
        """Top banner: Unique Artists (left) · Saved Tracks (right), horizontal, no title."""
        library_size = self.user.getLibrarySize()
        diversity = self.user.getLibraryDiversity()
        unique_artists = diversity.get("unique_artists", 0)

        font_size = round(22 * font_scale)
        df = pd.DataFrame([{}])

        left = (
            alt.Chart(df)
            .mark_text(align="left", baseline="middle", fontSize=font_size, fontWeight="bold", color=self.GREEN)
            .encode(x=alt.value(0), y=alt.value(height / 2), text=alt.value(f"{unique_artists:,} Unique Artists"))
        )
        right = (
            alt.Chart(df)
            .mark_text(align="right", baseline="middle", fontSize=font_size, fontWeight="bold", color=self.GREEN)
            .encode(x=alt.value(width), y=alt.value(height / 2), text=alt.value(f"{library_size:,} Saved Tracks"))
        )
        return (left + right).properties(width=width, height=height)

    def _last_played_chart(self, width: int = 280, height: int = 140, font_scale: float = 1.0) -> alt.Chart:
        """Right top: Last Played — song title, with full UTC date/time."""
        recent_df = self.user.recent_df
        stats = self.user.stats

        if recent_df.empty:
            title_text, time_text = "No recent plays", ""
        else:
            r = recent_df.iloc[0]
            title_text = (r["track"][:30] + "…") if len(r["track"]) > 30 else r["track"]
            played_at = stats.get("last_played_at") or r.get("played_at")
            if played_at:
                try:
                    dt = datetime.fromisoformat(played_at.replace("Z", "+00:00"))
                    time_text = dt.strftime("%b %d, %Y at %H:%M UTC")
                except Exception:
                    time_text = ""
            else:
                time_text = ""

        df = pd.DataFrame([{"title": title_text, "time": time_text}])
        base = alt.Chart(df).properties(width=width, height=height)
        x_right = alt.value(width - 10)
        y_center = alt.value(height / 2)

        t = base.mark_text(align="right", baseline="middle", fontSize=round(16 * font_scale), fontWeight="bold", color=self.GREEN, dy=-12).encode(x=x_right, y=y_center, text="title:N")
        s = base.mark_text(align="right", baseline="middle", fontSize=round(12 * font_scale), color="#555", dy=10).encode(x=x_right, y=y_center, text="time:N")

        return (t + s).resolve_scale(color="independent").properties(
            title=alt.TitleParams(text="Last Played", anchor="end", fontSize=round(20 * font_scale)),
        )

    def _favorites_title_chart(self, width: int = 600, height: int = 44) -> alt.Chart:
        """Centered 'Favorites' section title."""
        df = pd.DataFrame([{"t": "Favorites"}])
        return (
            alt.Chart(df)
            .mark_text(align="center", baseline="middle", fontSize=24, fontWeight="bold", color="#141331")
            .encode(
                x=alt.value(width / 2),
                y=alt.value(height / 2),
                text="t:N",
            )
            .properties(width=width, height=height)
        )

    def _track_table_chart(
        self,
        df: pd.DataFrame,
        title: str,
        subtitle: str = "",
        width: int = 380,
        height: int = 320,
        show_time: bool = False,
        hide_artist: bool = False,
        font_scale: float = 1.0,
    ) -> alt.Chart:
        """Shared table renderer used by Top Songs and Recently Played.
        df must have columns: rank, song, artist, y_pos, full_track.
        Optionally: time (str) when show_time=True.
        hide_artist: make artist text invisible (useful when time overlaps).
        """
        row_range        = [20, height - 20]
        artist_range     = [32, height - 8]   # offset so artist sits below the song

        # Calculate text limits to prevent overflow
        text_start_x = 36
        time_x = width - 10 if show_time else None
        if time_x:
            # Account for time text width: "04:10 UTC" ≈ 9 chars
            time_font = max(8, round(12 * font_scale))
            time_text_width = round(9 * time_font * 0.6)  # approx char_width ≈ fontSize * 0.6
            song_limit = max(40, time_x - time_text_width - text_start_x - 8)
        else:
            song_limit = width - text_start_x - 5
        artist_limit = song_limit

        rank_col = (
            alt.Chart(df)
            .mark_text(align="center", baseline="middle", fontSize=max(9, round(13 * font_scale)), fontWeight="bold", color="#333")
            .encode(
                x=alt.value(18),
                y=alt.Y("y_pos:O", title=None, axis=None, scale=alt.Scale(range=row_range)),
                text=alt.Text("rank:O"),
                tooltip=[alt.Tooltip("song:N", title="Song"), alt.Tooltip("artist:N", title="Artist")],
            )
        )
        song_col = (
            alt.Chart(df)
            .mark_text(align="left", baseline="middle", fontSize=max(9, round(14 * font_scale)), fontWeight="bold", color=self.GREEN, limit=song_limit)
            .encode(
                x=alt.value(text_start_x),
                y=alt.Y("y_pos:O", title=None, axis=None, scale=alt.Scale(range=row_range)),
                text=alt.Text("song:N"),
                tooltip=[alt.Tooltip("song:N", title="Song"), alt.Tooltip("artist:N", title="Artist")],
            )
        )
        artist_col = (
            alt.Chart(df)
            .mark_text(align="left", baseline="middle", fontSize=max(8, round(12 * font_scale)), color="#444",
                       limit=artist_limit, opacity=0 if hide_artist else 1)
            .encode(
                x=alt.value(text_start_x),
                y=alt.Y("y_pos:O", title=None, axis=None, scale=alt.Scale(range=artist_range)),
                text=alt.Text("artist:N"),
            )
        )

        layers = [rank_col, song_col, artist_col]

        if show_time:
            time_col = (
                alt.Chart(df)
                .mark_text(align="right", baseline="middle", fontSize=max(8, round(12 * font_scale)), color="#555")
                .encode(
                    x=alt.value(width - 10),
                    y=alt.Y("y_pos:O", title=None, axis=None, scale=alt.Scale(range=row_range)),
                    text=alt.Text("time:N"),
                )
            )
            layers.append(time_col)

        title_params = alt.TitleParams(
            text=title,
            anchor="start",
            fontSize=round(20 * font_scale),
            **(dict(subtitle=subtitle, subtitleFontSize=round(13 * font_scale), subtitleColor="#444") if subtitle else {}),
        )

        return (
            alt.layer(*layers)
            .resolve_scale(y="independent")
            .properties(width=width, height=height, title=title_params)
        )

    def _top_songs_chart(self, top_n: int = 10, width: int = 380, height: int = 320, time_range: str = "long_term", font_scale: float = 1.0, hide_artist: bool = False) -> alt.Chart:
        """Table: Top Songs — same visual style as Recently Played."""
        _RANGE_LABELS = {"long_term": "All Time", "medium_term": "Last 6 Months", "short_term": "Last 4 Weeks"}
        range_label = _RANGE_LABELS.get(time_range, time_range)
        tracks_df = self.user.getTopTracks(top_n, time_range)

        if tracks_df.empty:
            df = pd.DataFrame([{"rank": 1, "song": "No data", "artist": "", "y_pos": 0, "full_track": ""}])
        else:
            rows = []
            for i, (_, t) in enumerate(tracks_df.iterrows()):
                rows.append({
                    "rank": i + 1,
                    "song": t["track"],
                    "artist": t["artists"],
                    "y_pos": i,
                    "full_track": f"{t['track']} by {t['artists']}",
                })
            df = pd.DataFrame(rows)

        return self._track_table_chart(df, "Top Songs", range_label, width, height, show_time=False, hide_artist=hide_artist, font_scale=font_scale)

    # NEW: Sample visualization methods showcasing the rich data you can manipulate
    def _profile_stats_chart(self, width: int = 280, height: int = 140) -> alt.Chart:
        """Display User Profile Statistics followers, library size"""
        profile = self.user.profile
        library_stats = self.user.getLibraryDiversity()

        if not profile:
            df = pd.DataFrame([{"line": 0, "text": "Profile data unavailable", "tip": "Profile not loaded"}])
        else:
            df = pd.DataFrame([
                {
                    "line": 0,
                    "tip": f"Account: {profile['display_name']} from {profile.get('country', 'Unknown')}"
                },
                {
                    "line": 1,
                    "text": f"{self.user.getLibrarySize()} saved tracks • {library_stats['unique_artists']} artists",
                    "tip": f"Library diversity: {library_stats['unique_albums']} albums, {library_stats['total_duration_hours']:.1f} hrs total"
                }
            ])

        return (
            alt.Chart(df)
            .mark_text(align="center", baseline="middle", fontSize=16, fontWeight="bold", color=self.GREEN)
            .encode(
                y=alt.Y("line:O", title=None, axis=None, sort="ascending"),
                text=alt.Text("text:N"),
                tooltip=alt.Tooltip("tip:N", title=""),
            )
            .properties(
                width=width,
                height=height,
                title=alt.TitleParams(text="Profile Stats", anchor="start", fontSize=18),
            )
        )

    def _library_growth_chart(self, width: int = 600, height: int = 200) -> alt.Chart:
        """Timeline showing when tracks were added to library (music discovery patterns)"""
        growth_df = self.user.getLibraryGrowthPattern('M')

        if growth_df.empty:
            return alt.Chart(pd.DataFrame({"text": ["No saved tracks timeline data"]})).mark_text().encode(text="text:N").properties(width=width, height=height)

        # Convert period to string for visualization
        growth_df['period_str'] = growth_df['time_period'].astype(str)

        return (
            alt.Chart(growth_df)
            .mark_bar(color=self.GREEN)
            .encode(
                x=alt.X("period_str:T", title="Month", axis=alt.Axis(labelAngle=-45)),
                y=alt.Y("tracks_added:Q", title="Tracks Added"),
                tooltip=[
                    alt.Tooltip("period_str:N", title="Month"),
                    alt.Tooltip("tracks_added:Q", title="Tracks Added"),
                    alt.Tooltip("hours_added:Q", title="Hours Added", format=".1f")
                ]
            )
            .properties(
                width=width,
                height=height,
                title=alt.TitleParams(text="Music Discovery Timeline", anchor="start", fontSize=18)
            )
        )

    def _yearly_library_growth_area_chart(self, width: int = 600, height: int = 300, font_scale: float = 1.0, title_anchor: str = "start") -> alt.Chart:
        """Area chart: cumulative library growth + new distinct artists per year (dual y-axis)."""
        growth_df = self.user.getLibraryGrowthPattern('Y')

        if growth_df.empty:
            return alt.Chart(pd.DataFrame({"text": ["No yearly library growth data"]})).mark_text().encode(text="text:N").properties(width=width, height=height)

        growth_df['year'] = growth_df['time_period'].astype(str)
        has_cumulative_artists = 'cumulative_artists' in growth_df.columns

        tooltip = [
            alt.Tooltip("year:O", title="Year"),
            alt.Tooltip("cumulative_tracks:Q", title="Total Tracks"),
        ]
        if has_cumulative_artists:
            tooltip.append(alt.Tooltip("cumulative_artists:Q", title="Total Artists"))

        # Chart 1: Cumulative Tracks
        tracks_tooltip = [
            alt.Tooltip("year:O", title="Year"),
            alt.Tooltip("cumulative_tracks:Q", title="Total Tracks"),
        ]
        area_tracks = (
            alt.Chart(growth_df)
            .mark_area(color=self.GREEN, opacity=0.6, stroke=self.GREEN, strokeWidth=2)
            .encode(
                x=alt.X("year:O", title="Year", axis=alt.Axis(labelAngle=-45, labelFontSize=round(9 * font_scale), titleFontSize=round(10 * font_scale))),
                y=alt.Y("cumulative_tracks:Q", title="Total Tracks",
                        axis=alt.Axis(titleColor=self.GREEN, labelFontSize=round(9 * font_scale), titleFontSize=round(10 * font_scale))),
                tooltip=tracks_tooltip,
            )
            .properties(
                width=width,
                height=round(height * 0.55),
                title=alt.TitleParams(
                    text="Library Growth (Tracks)",
                    anchor=title_anchor,
                    fontSize=round(16 * font_scale),
                )
            )
        )
        pts_tracks = (
            alt.Chart(growth_df)
            .mark_circle(color=self.GREEN, size=60, stroke="white", strokeWidth=1)
            .encode(x=alt.X("year:O"), y=alt.Y("cumulative_tracks:Q"), tooltip=tracks_tooltip)
        )
        chart_tracks = area_tracks + pts_tracks

        # Chart 2: Cumulative Artists
        if has_cumulative_artists:
            ARTIST_COLOR = "#1a237e"  # dark blue
            artists_tooltip = [
                alt.Tooltip("year:O", title="Year"),
                alt.Tooltip("cumulative_artists:Q", title="Total Artists"),
            ]
            area_artists = (
                alt.Chart(growth_df)
                .mark_area(color=ARTIST_COLOR, opacity=0.5, stroke=ARTIST_COLOR, strokeWidth=2)
                .encode(
                    x=alt.X("year:O", title="Year", axis=alt.Axis(labelAngle=-45, labelFontSize=round(9 * font_scale), titleFontSize=round(10 * font_scale))),
                    y=alt.Y("cumulative_artists:Q", title="Total Artists",
                            axis=alt.Axis(titleColor=ARTIST_COLOR, labelFontSize=round(9 * font_scale), titleFontSize=round(10 * font_scale))),
                    tooltip=artists_tooltip,
                )
                .properties(
                    width=width,
                    height=round(height * 0.45),
                    title=alt.TitleParams(
                        text="Library Growth (Artists)",
                        anchor=title_anchor,
                        fontSize=round(16 * font_scale),
                    )
                )
            )
            pts_artists = (
                alt.Chart(growth_df)
                .mark_circle(color=ARTIST_COLOR, size=50)
                .encode(x=alt.X("year:O"), y=alt.Y("cumulative_artists:Q"), tooltip=artists_tooltip)
            )
            chart_artists = area_artists + pts_artists
            return alt.vconcat(chart_tracks, chart_artists)
        else:
            return chart_tracks

    def _saved_vs_top_comparison_chart(self, width: int = 380, height: int = 320) -> alt.Chart:
        """Compare most-saved artists vs current top artists (taste evolution analysis)"""
        saved_artists_df = self.user.getTopSavedArtists(10)
        top_artists_df = self.user.getTopArtists(10)

        if saved_artists_df.empty and top_artists_df.empty:
            return alt.Chart(pd.DataFrame({"text": ["No comparison data"]})).mark_text().encode(text="text:N").properties(width=width, height=height)

        # Combine data for comparison visualization
        comparison_data = []

        for i, (_, row) in enumerate(saved_artists_df.iterrows() if not saved_artists_df.empty else []):
            comparison_data.append({
                "artist": row['artist'][:20] + ("..." if len(row['artist']) > 20 else ""),
                "rank": i + 1,
                "count": row['saved_tracks_count'],
                "type": "Saved Library"
            })

        for i, (_, row) in enumerate(top_artists_df.iterrows() if not top_artists_df.empty else []):
            comparison_data.append({
                "artist": row['name'][:20] + ("..." if len(row['name']) > 20 else ""),
                "rank": i + 1,
                "count": 10 - i,  # Inverse rank as pseudo-score
                "type": "Current Top"
            })

        df = pd.DataFrame(comparison_data)

        return (
            alt.Chart(df)
            .mark_circle(size=100)
            .encode(
                x=alt.X("rank:O", title="Rank"),
                y=alt.Y("count:Q", title="Score/Count"),
                color=alt.Color("type:N", scale=alt.Scale(range=[self.GREEN, "#FF6B35"])),
                tooltip=["artist:N", "rank:O", "count:Q", "type:N"]
            )
            .properties(
                width=width,
                height=height,
                title=alt.TitleParams(text="Saved vs Current Preferences", anchor="start", fontSize=18)
            )
        )

    def _recently_played_chart(self, top_n: int = 10, width: int = 760, height: int = 300, font_scale: float = 1.0, hide_artist: bool = False) -> alt.Chart:
        """Table listing recent tracks with played-at timestamps."""
        recent_df = self.user.recent_df

        if recent_df.empty:
            df = pd.DataFrame([{"rank": 1, "song": "No recent plays", "artist": "", "time": "", "y_pos": 0, "full_track": ""}])
        else:
            rows = []
            for i, (_, t) in enumerate(recent_df.head(top_n).iterrows()):
                played_at = t.get("played_at", "")
                time_str = ""
                if played_at:
                    try:
                        dt = datetime.fromisoformat(str(played_at).replace("Z", "+00:00"))
                        time_str = dt.strftime("%H:%M") + " UTC"
                    except Exception:
                        time_str = str(played_at)[:16]
                rows.append({
                    "rank": i + 1,
                    "song": t["track"],
                    "artist": t["artists"],
                    "time": time_str,
                    "y_pos": i,
                    "full_track": f"{t['track']} by {t['artists']}",
                })
            df = pd.DataFrame(rows)

        return self._track_table_chart(df, "Recently Played", "", width, height, show_time=True, hide_artist=hide_artist, font_scale=font_scale)

    def _top_artists_pie_chart(self, top_n: int = 10, width: int = 400, height: int = 340, font_scale: float = 1.0, title_anchor: str = "start") -> alt.Chart:
        """Pie chart: Top Artists by saved-track count (real library data)."""
        artists_df = self.user.getTopSavedArtists(top_n)

        if artists_df.empty:
            return alt.Chart(pd.DataFrame({"name": ["No data"], "share": [1]})).mark_arc().encode(theta="share:Q").properties(width=width, height=height)

        total = artists_df["saved_tracks_count"].sum()
        rows = []
        for i, (_, a) in enumerate(artists_df.iterrows()):
            rows.append({
                "artist": a["artist"],
                "count": int(a["saved_tracks_count"]),
                "pct": round(100 * a["saved_tracks_count"] / total, 1),
                "rank": i + 1,
            })
        df = pd.DataFrame(rows)
        outer_r = int(min(width, height) * 0.44)

        return (
            alt.Chart(df)
            .mark_arc(innerRadius=0, stroke="black", strokeWidth=1, outerRadius=outer_r)
            .encode(
                theta=alt.Theta("count:Q", stack=True),
                color=alt.Color(
                    "artist:N",
                    scale=alt.Scale(range=self.ARTIST_COLORS),
                    legend=None,
                ),
                tooltip=[
                    alt.Tooltip("artist:N", title="Artist"),
                    alt.Tooltip("count:Q", title="Saved Tracks"),
                    alt.Tooltip("pct:Q", title="Share (%)", format=".1f"),
                ],
            )
            .properties(
                width=width,
                height=height,
                title=alt.TitleParams(
                    text="Top Artists",
                    subtitle="By Saved Tracks",
                    anchor=title_anchor,
                    fontSize=round(20 * font_scale),
                    subtitleFontSize=round(13 * font_scale),
                    subtitleColor="#444",
                ),
            )
        )

    def _artists_legend_chart(self, top_n: int = 10, width: int = 320, height: int = 340, font_scale: float = 1.0) -> alt.Chart:
        """Manual legend for the top artists pie — colored dot + artist name + saved count."""
        artists_df = self.user.getTopSavedArtists(top_n)
        radius = min(width, height) // 2 - 18

        rows = []
        for i, (_, a) in enumerate(artists_df.head(top_n).iterrows()):
            artist_name = a["artist"]
            count = int(a["saved_tracks_count"])
            rows.append({
                "artist": artist_name,
                "label": f"{artist_name} ({count:,})",
                "idx": i,
            })

        if not rows:
            return alt.Chart(pd.DataFrame({"t": [""]})).mark_text().encode(text="t:N").properties(width=width, height=height)

        df = pd.DataFrame(rows)
        # Share the same domain order so colors match the arc
        ordered_domain = df["artist"].tolist()
        color_scale = alt.Scale(range=self.ARTIST_COLORS, domain=ordered_domain)

        row_step = max(22, int((height - 40) / len(df)))

        pie = (
            alt.Chart(artists_df)
            .mark_arc(innerRadius=0, outerRadius=radius, stroke="black", strokeWidth=1)
            .encode(
                theta=alt.Theta("track_count:Q", stack=True),
                color=alt.Color("artist:N", scale=alt.Scale(range=self.ARTIST_COLORS)),
                tooltip=[
                    alt.Tooltip("artist:N", title="Artist"),
                    alt.Tooltip("track_count:Q", title="Tracks"),
                    alt.Tooltip("share:Q", title="Share (%)", format=".1f")
                ]
            )
            .properties(width=width, height=height)
        )

        # Restore legend chart: colored dots + artist labels
        dots = (
            alt.Chart(df)
            .mark_point(filled=True, size=120, stroke="black", strokeWidth=1.5)
            .encode(
                y=alt.Y("idx:O", title=None, axis=None,
                         scale=alt.Scale(range=[30, 30 + row_step * (len(df) - 1)])),
                x=alt.value(26),
                color=alt.Color("artist:N", scale=color_scale, legend=None),
            )
        )
        labels = (
            alt.Chart(df)
            .mark_text(align="left", baseline="middle", fontSize=round(13 * font_scale), dx=12)
            .encode(
                y=alt.Y("idx:O", title=None, axis=None,
                         scale=alt.Scale(range=[30, 30 + row_step * (len(df) - 1)])),
                x=alt.value(46),
                text=alt.Text("label:N"),
                color=alt.value("#333"),
            )
        )
        return (
            (dots + labels)
            .resolve_scale(y="shared")
            .properties(
                width=width,
                height=height,
                title=alt.TitleParams(text="", anchor="start", fontSize=14, color="#555"),
            )
        )

    def _top_artists_table_chart(self, top_n: int = 10, width: int = 360, height: int = 340) -> alt.Chart:
        """Table of top artists by saved-track count — real library data."""
        artists_df = self.user.getTopSavedArtists(top_n)

        if artists_df.empty:
            df = pd.DataFrame([{"rank": 1, "song": "No data", "artist": "", "y_pos": 0, "full_track": ""}])
        else:
            rows = []
            for i, (_, row) in enumerate(artists_df.iterrows()):
                name = (row["artist"][:34] + "\u2026") if len(row["artist"]) > 34 else row["artist"]
                count = int(row["saved_tracks_count"])
                rows.append({
                    "rank": i + 1,
                    "song": name,
                    "artist": f"{count} saved tracks",
                    "y_pos": i,
                    "full_track": f"{name} — {count} saved tracks",
                })
            df = pd.DataFrame(rows)

        return self._track_table_chart(df, "Top Artists", "By Saved Tracks", width, height, show_time=False)

    def generateDashboard(self, layout: str = "standard") -> None:
        """Generate the dashboard at the given responsive layout scale.
        Layouts (maps to Charts/ output files):
            standard  → {username}_Standard.json   (desktop,          w > 1200 px)
            tablet    → {username}_Tablet.json      (tablet,  w ≤ 1200 px)
            landscape → {username}_Landscape.json   (mobile landscape, w ≤  900 px)
            portrait  → {username}_Portrait.json    (mobile portrait,  w ≤  550 px)
        Row structure (top → bottom):
            Library Stats | Last Played
            Spotify Library Growth | Top Artists pie + Legend
            Top Songs | Recently Played
        """
        LAYOUTS = {
            "standard": dict(
                font_scale=1.00, title_size=40, spacer_h=16, hide_rp_artist=True, hide_ts_artist=True,
                stats_h=52,
                growth_w=400, growth_h=320, pie_w=300, pie_h=320, legend_w=180, legend_h=320,
                songs_w=370, songs_h=380, recent_w=370, recent_h=380,
                axis_label=11, axis_title=14, legend_label=10, legend_title=12,
                padding={"left": 30, "right": 30, "top": 20, "bottom": 30}, spacing=20,
            ),
            "tablet_portrait": dict(
                # iPad Mini (768px), iPad Air (820px), small tablets in portrait
                # Vertical with pie first, songs+RP side by side
                font_scale=0.50, title_size=28, spacer_h=5, hide_rp_artist=True, hide_ts_artist=True,
                stats_h=28, vconcat=True, split_charts=True, hconcat_songs=True,
                growth_w=280, growth_h=160, pie_w=200, pie_h=200, legend_w=120, legend_h=200,
                songs_w=280, songs_h=200, recent_w=280, recent_h=200,
                axis_label=6, axis_title=8, legend_label=6, legend_title=7,
                padding={"left": 8, "right": 8, "top": 8, "bottom": 12}, spacing=6,
            ),
            "tablet": dict(
                # Larger tablets, iPad Pro, small desktops (901-1200px)
                # Vertical with pie first, songs+RP side by side
                font_scale=0.65, title_size=28, spacer_h=8, hide_rp_artist=True, hide_ts_artist=True,
                stats_h=36, vconcat=True, split_charts=True, hconcat_songs=True,
                growth_w=380, growth_h=200, pie_w=280, pie_h=260, legend_w=160, legend_h=260,
                songs_w=360, songs_h=260, recent_w=360, recent_h=260,
                axis_label=8, axis_title=10, legend_label=8, legend_title=9,
                padding={"left": 14, "right": 14, "top": 12, "bottom": 18}, spacing=10,
            ),
            "landscape": dict(
                font_scale=0.57, title_size=18, spacer_h=8, hide_rp_artist=True, hide_ts_artist=True,
                stats_h=36,
                growth_w=280, growth_h=180, pie_w=180, pie_h=180, legend_w=0, legend_h=0,
                songs_w=235, songs_h=200, recent_w=235, recent_h=200,
                axis_label=7, axis_title=9, legend_label=6, legend_title=8,
                padding={"left": 10, "right": 10, "top": 12, "bottom": 18}, spacing=10,
            ),
            "portrait": dict(
                # Single-column stacked layout — each chart spans full width
                # Legend is REMOVED on portrait to match Steam mobile pattern
                font_scale=0.60, title_size=14, spacer_h=0,
                stats_h=0,
                growth_w=200, growth_h=150,              # narrower growth for hconcat
                pie_w=90,     pie_h=90,                   # compact pie (no legend on mobile)
                legend_w=0,   legend_h=0,                 # legend removed
                songs_w=260,  songs_h=220,                # full-width songs (taller for readability)
                recent_w=260, recent_h=220,               # full-width recently played (taller)
                axis_label=8, axis_title=9, legend_label=7, legend_title=8,
                hide_rp_artist=False, hide_ts_artist=True,  # no RP on portrait (cards instead)
                title_anchor="middle",                     # center sub-chart titles on mobile
                padding={"left": 5, "right": 5, "top": 0, "bottom": 15}, spacing=0,
            ),
        }

        s = LAYOUTS.get(layout.lower(), LAYOUTS["standard"])
        fs = s["font_scale"]

        spacer = alt.Chart(pd.DataFrame([{"x": 0}])).mark_text().encode(
            x=alt.value(0), text=alt.value("")
        ).properties(width=10, height=s["spacer_h"])

        t_anchor = s.get("title_anchor", "start")
        yearly_growth   = self._yearly_library_growth_area_chart(width=s["growth_w"], height=s["growth_h"], font_scale=fs, title_anchor=t_anchor)
        pie             = self._top_artists_pie_chart(width=s["pie_w"],   height=s["pie_h"],    font_scale=fs, title_anchor=t_anchor)
        pie_legend      = self._artists_legend_chart(width=s["legend_w"], height=s["legend_h"], font_scale=fs) if s["legend_w"] > 0 else None
        top_songs       = self._top_songs_chart(width=s["songs_w"],      height=s["songs_h"],   font_scale=fs, hide_artist=s.get("hide_ts_artist", False))
        recently_played = self._recently_played_chart(width=s["recent_w"], height=s["recent_h"], font_scale=fs, hide_artist=s.get("hide_rp_artist", False))

        if layout.lower() == "portrait":
            # Desktop-style: growth charts | pie (no legend, no stats on mobile)
            # Songs + Recently Played are rendered as React cards on mobile
            growth_pie_row = yearly_growth | pie
            if s["stats_h"] > 0:
                banner_w = s["songs_w"]
                stats_banner = self._annual_stats_chart(width=banner_w, height=s["stats_h"], font_scale=fs)
                self.dashboard = (stats_banner & spacer & growth_pie_row)
            else:
                self.dashboard = growth_pie_row
            # Store card data metadata for React to extract from datasets
            self._card_data = {
                "topSongs": top_songs,
                "recentlyPlayed": recently_played,
            }
        elif s.get("vconcat"):
            if s.get("split_charts"):
                # Vertical with pie first: banner / pie+legend / growth / songs(+RP)
                if s.get("hconcat_songs"):
                    banner_w = s["songs_w"] + s["recent_w"] + s["spacing"]
                else:
                    banner_w = max(s["songs_w"], s["pie_w"] + s["legend_w"] + s["spacing"])
                stats_banner = self._annual_stats_chart(width=banner_w, height=s["stats_h"], font_scale=fs)
                if pie_legend is not None:
                    pie_row = pie | pie_legend
                else:
                    pie_row = pie
                if s.get("hconcat_songs"):
                    bottom_row = top_songs | recently_played
                    self.dashboard = (stats_banner & spacer & pie_row & spacer & yearly_growth & spacer & bottom_row)
                else:
                    self.dashboard = (stats_banner & spacer & pie_row & spacer & yearly_growth & spacer & top_songs & spacer & recently_played)
            else:
                # Vertical stacked: banner / (growth | pie | legend) / songs / recently_played
                banner_w = s["growth_w"] + s["pie_w"] + s["legend_w"] + 2 * s["spacing"]
                stats_banner = self._annual_stats_chart(width=banner_w, height=s["stats_h"], font_scale=fs)
                if pie_legend is not None:
                    growth_row = yearly_growth | pie | pie_legend
                else:
                    growth_row = yearly_growth | pie
                self.dashboard = (stats_banner & spacer & growth_row & spacer & top_songs & spacer & recently_played)
        else:
            # Side-by-side: banner / (growth | pie | legend) / (songs | recent)
            banner_w = s["growth_w"] + s["pie_w"] + s["legend_w"] + 2 * s["spacing"]
            stats_banner = self._annual_stats_chart(width=banner_w, height=s["stats_h"], font_scale=fs)
            if pie_legend is not None:
                growth_row = yearly_growth | pie | pie_legend
            else:
                growth_row = yearly_growth | pie
            bottom_row = top_songs | recently_played
            self.dashboard = (stats_banner & spacer & growth_row & spacer & bottom_row)

        self.dashboard = self.dashboard.properties(
            title=alt.TitleParams(
                text=f"{self.user.username}'s Spotify Dashboard",
                anchor="middle",
                fontSize=s["title_size"],
            ),
            padding=s["padding"],
            spacing=s["spacing"],
            center=True,
        ).configure_view(
            strokeWidth=0,
            strokeOpacity=0,
        ).configure_axis(
            labelFontSize=s["axis_label"],
            titleFontSize=s["axis_title"],
        ).configure_legend(
            labelFontSize=s["legend_label"],
            titleFontSize=s["legend_title"],
            labelLimit=120,
        )

    def save(self, filename: Optional[str] = None) -> None:
        """Generate all responsive dashboard layouts and save them to Charts/.
        Output files (mirroring the Steam dashboard pattern):
            {username}_Standard.json        ← imported by React for desktop
            {username}_Tablet.json          ← imported by React for large tablet / small desktop
            {username}_TabletPortrait.json  ← imported by React for iPad Mini/Air
            {username}_Landscape.json       ← imported by React for mobile landscape
            {username}_Portrait.json        ← imported by React for mobile portrait
            {username}_Dashboard.json       ← full-size reference copy (Standard)
            {username}_Dashboard.html       ← interactive HTML reference
        Also saves spotify_data.json for the React recently-played / top-songs tables.
        """
        if filename is None:
            filename = f"{self.user.username}_Dashboard"

        script_dir = os.path.dirname(os.path.abspath(__file__))
        charts_dir = os.path.join(script_dir, "Charts")
        os.makedirs(charts_dir, exist_ok=True)

        # ── Generate and save each responsive layout ──────────────────────────
        responsive_layouts = ["standard", "tablet", "tablet_portrait", "landscape", "portrait"]
        layout_labels = {
            "standard": "Standard",
            "tablet": "Tablet",
            "tablet_portrait": "TabletPortrait",
            "landscape": "Landscape",
            "portrait": "Portrait",
        }
        for layout in responsive_layouts:
            print(f"Generating {layout} layout...")
            self.generateDashboard(layout)
            label = layout_labels.get(layout, layout.capitalize())
            out_path = os.path.join(charts_dir, f"{self.user.username}_{label}.json")
            spec_dict = self.dashboard.to_dict()
            spec_dict["background"] = None  # Transparent — no white box in React
            spec_dict["$schema"] = "https://vega.github.io/schema/vega-lite/v5.20.1.json"  # Match react-vega bundled vega-lite

            # For portrait: inject card data (Top Songs + Recently Played)
            # so React can render them as mobile cards instead of VegaLite text charts
            if layout == "portrait" and hasattr(self, "_card_data"):
                songs_spec = self._card_data["topSongs"].to_dict()
                recent_spec = self._card_data["recentlyPlayed"].to_dict()
                # Merge their datasets into the main spec
                if "datasets" not in spec_dict:
                    spec_dict["datasets"] = {}
                songs_ds = songs_spec.get("datasets", {})
                recent_ds = recent_spec.get("datasets", {})
                spec_dict["datasets"].update(songs_ds)
                spec_dict["datasets"].update(recent_ds)
                # Add metadata so React knows which dataset keys to use
                songs_key = list(songs_ds.keys())[0] if songs_ds else None
                recent_key = list(recent_ds.keys())[0] if recent_ds else None
                spec_dict["_cardData"] = {
                    "topSongsDataset": songs_key,
                    "recentlyPlayedDataset": recent_key,
                }
                print(f"  Injected _cardData: songs={songs_key}, recent={recent_key}")

            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(spec_dict, f, indent=2, ensure_ascii=False)
            print(f"  Saved: {out_path}")

        # ── Save Dashboard.json + Dashboard.html (standard, for reference) ────
        print("Saving reference dashboard (standard)...")
        self.generateDashboard("standard")
        spec_dict = self.dashboard.to_dict()
        spec_dict["background"] = None
        spec_dict["$schema"] = "https://vega.github.io/schema/vega-lite/v5.20.1.json"
        dashboard_json_path = os.path.join(charts_dir, f"{filename}.json")
        with open(dashboard_json_path, "w", encoding="utf-8") as f:
            json.dump(spec_dict, f, indent=2, ensure_ascii=False)
        print(f"  Saved: {dashboard_json_path}")

        html_path = os.path.join(charts_dir, f"{filename}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(self.dashboard.to_html())
        print(f"  Saved: {html_path}")

        self.dashboard.save(os.path.join(charts_dir, f"{filename}.png"))  # Save as PNG (Static)
        self.dashboard.save(os.path.join(charts_dir, f"{filename}.svg"))  # Save as SVG (Vector)
        print(f"  Saved: {filename}.png, {filename}.svg")

        # ── Save comprehensive user data for React tables ─────────────────────
        data_path = os.path.join(script_dir, "spotify_data.json")
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(self.user.getComprehensiveData(), f, indent=2, ensure_ascii=False)
        print(f"  Saved: {data_path}")

        # ── Clean up temp files from Charts/ ─────────────────────────────────
        keep = {
            f"{self.user.username}_Standard.json",
            f"{self.user.username}_Tablet.json",
            f"{self.user.username}_TabletPortrait.json",
            f"{self.user.username}_Landscape.json",
            f"{self.user.username}_Portrait.json",
            f"{filename}.json",
            f"{filename}.html",
            f"{filename}.png",
            f"{filename}.svg",
        }
        for entry in os.listdir(charts_dir):
            if entry not in keep:
                entry_path = os.path.join(charts_dir, entry)
                try:
                    if os.path.isfile(entry_path):
                        os.remove(entry_path)
                    elif os.path.isdir(entry_path):
                        shutil.rmtree(entry_path)
                except Exception as e:
                    print(f"  Warning: could not remove {entry_path}: {e}")

        # ── Clean up __pycache__ from the script directory ────────────────────
        pycache = os.path.join(script_dir, "__pycache__")
        if os.path.isdir(pycache):
            shutil.rmtree(pycache)
            print(f"  Removed: {pycache}")

        print(f"\nSpotify dashboard saved to {charts_dir}/")

    def generateYearlyGrowthChart(self, filename: Optional[str] = None) -> None:
        """Generate and save just the yearly library growth area chart"""
        if filename is None:
            filename = f"{self.user.username}_LibraryGrowth"

        script_dir = os.path.dirname(os.path.abspath(__file__))
        charts_dir = os.path.join(script_dir, "Charts")
        os.makedirs(charts_dir, exist_ok=True)

        # Generate the yearly growth area chart
        yearly_chart = self._yearly_library_growth_area_chart(width=800, height=400)

        # Save as different formats
        yearly_chart_spec = yearly_chart.to_dict()

        # Save as JSON
        with open(os.path.join(charts_dir, f"{filename}.json"), "w", encoding="utf-8") as f:
            json.dump(yearly_chart_spec, f, indent=2, ensure_ascii=False)

        # Save as HTML
        with open(os.path.join(charts_dir, f"{filename}.html"), "w", encoding="utf-8") as f:
            f.write(yearly_chart.to_html())

        # Save as PNG and SVG
        yearly_chart.save(os.path.join(charts_dir, f"{filename}.png"))
        yearly_chart.save(os.path.join(charts_dir, f"{filename}.svg"))

        print(f"📈 Yearly library growth chart saved to {charts_dir}/{filename}.*")


if __name__ == '__main__':
    load_dotenv()

    # Environment Variables for Spotify API Credentials
    USERNAME = os.getenv("SPOTIFY_DASHBOARD_USERNAME", "Muntakim")
    CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

    try:
        if not CLIENT_ID or not CLIENT_SECRET:
            raise ValueError(
                "Missing SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET. "
                f"Create a .env file with:\n"
                "  SPOTIFY_CLIENT_ID=your_client_id\n"
                "  SPOTIFY_CLIENT_SECRET=your_client_secret\n"
                "  SPOTIFY_REDIRECT_URI=your_redirect_uri\n"
            )

        user = SpotifyUser(USERNAME, SpotifyAPI(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI))
        SpotifyDashboard(user).save()
        print("Spotify Dashboard Generated Successfully!")

    except Exception as e:
        print(f"Error During Execution: {e}")
        raise
