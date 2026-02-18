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

            for track_info in saved_tracks.get("items", []):
                track_info = self._parseTrack(track_info["track"])
                track_info["added_at"] = track_info.get("added_at")
                saved_rows.append(track_info)

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
        self.top_tracks_medium_df = pd.DataFrame()
        self.top_tracks_long_df = pd.DataFrame()
        self.top_artists_short_df = pd.DataFrame()
        self.top_artists_medium_df = pd.DataFrame()
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

            # Fetch all data
            self.recent_df = self.api_client.getRecentTracks()

            self.top_tracks_short_df = self.api_client.getTopTracks("short_term")
            self.top_tracks_medium_df = self.api_client.getTopTracks("medium_term")
            self.top_tracks_long_df = self.api_client.getTopTracks("long_term")

            self.top_artists_short_df = self.api_client.getTopArtists("short_term")
            self.top_artists_medium_df = self.api_client.getTopArtists("medium_term")
            self.top_artists_long_df = self.api_client.getTopArtists("long_term")

            # NEW: Fetch Profile & Saved Tracks
            self.saved_tracks_df = self.api_client.getSavedTracks()  # Gets entire library!

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
                    # Extract stats from CSV
                    self.total_hours = self.stats_df.get('total_hours', [0]).iloc[0] if 'total_hours' in self.stats_df.columns else 0
                print("Data loaded from CSV backup")
            except Exception as e:
                print(f"Error loading from CSV: {e}")
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
            "medium_term": self.top_tracks_medium_df,
            "long_term": self.top_tracks_long_df
        }
        df = df_map.get(time_range, self.top_tracks_long_df)
        return df.head(n) if not df.empty else pd.DataFrame()

    def getTopArtists(self, n: int = 10, time_range: str = "long_term") -> pd.DataFrame:
        """Get Top N Artists by Time Range"""
        df_map = {
            "short_term": self.top_artists_short_df,
            "medium_term": self.top_artists_medium_df,
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

    def getLibraryGrowthPattern(self) -> pd.DataFrame:
        """Analyze when tracks were added to library (music discovery timeline)"""
        if self.saved_tracks_df.empty or 'added_at' not in self.saved_tracks_df.columns:
            return pd.DataFrame()

        # Convert added_at to datetime and analyze patterns
        df = self.saved_tracks_df.copy()
        df['added_at'] = pd.to_datetime(df['added_at'])
        df['year_month'] = df['added_at'].dt.to_period('M')

        growth_pattern = df.groupby('year_month').agg({
            'track': 'count',
            'duration_ms': 'sum'
        }).rename(columns={'track': 'tracks_added', 'duration_ms': 'total_duration_ms'})

        growth_pattern['hours_added'] = growth_pattern['total_duration_ms'] / (1000 * 60 * 60)
        growth_pattern = growth_pattern.reset_index()

        # Convert Period to string for JSON serialization
        growth_pattern['year_month'] = growth_pattern['year_month'].astype(str)
        return growth_pattern

    def getTopSavedArtists(self, n: int = 10) -> pd.DataFrame:
        """Get most saved/liked artists from library"""
        if self.saved_tracks_df.empty:
            return pd.DataFrame()

        # Split artists string and count occurrences
        all_artists = []
        for artists_str in self.saved_tracks_df['artists']:
            all_artists.extend([artist.strip() for artist in artists_str.split(',')])

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
            "top_tracks_medium": self.top_tracks_medium_df.to_dict('records') if not self.top_tracks_medium_df.empty else [],
            "top_tracks_long": self.top_tracks_long_df.to_dict('records') if not self.top_tracks_long_df.empty else [],
            "top_artists_short": self.top_artists_short_df.to_dict('records') if not self.top_artists_short_df.empty else [],
            "top_artists_medium": self.top_artists_medium_df.to_dict('records') if not self.top_artists_medium_df.empty else [],
            "top_artists_long": self.top_artists_long_df.to_dict('records') if not self.top_artists_long_df.empty else [],
            "total_hours": self.total_hours,
            "stats": self.stats,

            # NEW: Rich Profile & Library Data
            "saved_tracks": self.saved_tracks_df.to_dict('records') if not self.saved_tracks_df.empty else [],
            "library_stats": {
                "total_saved_tracks": self.getLibrarySize(),
                "subscription_tier": self.getSubscriptionTier(),
                "diversity_metrics": self.getLibraryDiversity(),
                "top_saved_artists": self.getTopSavedArtists(10).to_dict('records') if not self.saved_tracks_df.empty else [],
                "library_growth_timeline": self.getLibraryGrowthPattern().to_dict('records') if not self.saved_tracks_df.empty else []
            }
        }
class SpotifyDashboard:
    """Creates Visualizations for Spotify User Data"""

    def __init__(self, user: SpotifyUser):
        self.user = user
        self.colors = [
            "#1DB954", "#1ED760", "#191414", "#FFFFFF",
            "#535353", "#B3B3B3", "#000000", "#FF6B35",
            "#F037A5", "#7856FF", "#2D46B9", "#509BF5",
            "#FFD23F", "#FF4632", "#AF2896"
        ]

        self.dashboard = None
        self.generateDashboard()

    def _annual_stats_chart(self, width: int = 280, height: int = 140) -> alt.Chart:
        """Left top: Annual Stats — X.X Hrs Listened, X songs | X Artists (green numbers)."""
        hours = self.user.getTotalHours()
        stats = self.user.stats
        n_songs = stats.get("n_songs", 0)
        n_artists = stats.get("n_artists", 0)

        df = pd.DataFrame([
            {"line": 0, "text": f"{hours:.1f} Hrs Listened", "tip": f"{hours:.1f} hrs estimated annual listening"},
            {"line": 1, "text": f"{n_songs} songs | {n_artists} Artists", "tip": "Unique tracks and artists in your top 50"},
        ])

        return (
            alt.Chart(df)
            .mark_text(align="center", baseline="middle", fontSize=22, fontWeight="bold", color="#1DB954")
            .encode(
                y=alt.Y("line:O", title=None, axis=None, sort="ascending"),
                text=alt.Text("text:N"),
                tooltip=alt.Tooltip("tip:N", title=""),
            )
            .properties(
                width=width,
                height=height,
                title=alt.TitleParams(text="Annual Stats", anchor="start", fontSize=20),
            )
        )

    def _last_played_chart(self, width: int = 280, height: int = 140) -> alt.Chart:
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

        t = base.mark_text(align="right", baseline="middle", fontSize=16, fontWeight="bold", color="#1DB954", dy=-12).encode(x=x_right, y=y_center, text="title:N")
        s = base.mark_text(align="right", baseline="middle", fontSize=12, color="#555", dy=10).encode(x=x_right, y=y_center, text="time:N")

        return (t + s).resolve_scale(color="independent").properties(
            title=alt.TitleParams(text="Last Played", anchor="end", fontSize=20),
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

    def _top_songs_chart(self, top_n: int = 10, width: int = 380, height: int = 320) -> alt.Chart:
        """Table format: Top Songs with proper ranking and clean layout."""
        tracks_df = self.user.getTopTracks(top_n)

        if tracks_df.empty:
            df = pd.DataFrame([{"rank": 1, "song": "No data", "artist": "", "y_pos": 0}])
        else:
            rows = []
            for i, (_, t) in enumerate(tracks_df.iterrows()):
                song = (t["track"][:28] + "…") if len(t["track"]) > 28 else t["track"]
                artist = (t["artists"][:26] + "…") if len(t["artists"]) > 26 else t["artists"]
                rows.append({
                    "rank": i + 1,
                    "song": song,
                    "artist": artist,
                    "y_pos": i,
                    "full_track": f"{t['track']} by {t['artists']}"
                })
            df = pd.DataFrame(rows)

        # Create rank column
        rank_text = alt.Chart(df).mark_text(
            align="center",
            baseline="middle",
            fontSize=12,
            fontWeight="bold",
            color="#666"
        ).encode(
            x=alt.value(25),
            y=alt.Y("y_pos:O", title=None, axis=None, scale=alt.Scale(range=[30, height-30])),
            text=alt.Text("rank:O")
        )

        # Create song title column
        song_text = alt.Chart(df).mark_text(
            align="left",
            baseline="middle",
            fontSize=13,
            fontWeight="bold",
            color="#1DB954"
        ).encode(
            x=alt.value(50),
            y=alt.Y("y_pos:O", title=None, axis=None, scale=alt.Scale(range=[30, height-30])),
            text=alt.Text("song:N"),
            tooltip=alt.Tooltip("full_track:N", title="Track")
        )

        # Create artist column
        artist_text = alt.Chart(df).mark_text(
            align="left",
            baseline="middle",
            fontSize=11,
            color="#888"
        ).encode(
            x=alt.value(50),
            y=alt.Y("y_pos:O", title=None, axis=None, scale=alt.Scale(range=[15, height-45])),
            text=alt.Text("artist:N")
        )

        return (rank_text + song_text + artist_text).properties(
            width=width,
            height=height,
            title=alt.TitleParams(text="Top Songs", anchor="start", fontSize=20)
        ).resolve_scale(y="independent")

    # NEW: Sample visualization methods showcasing the rich data you can manipulate
    def _profile_stats_chart(self, width: int = 280, height: int = 140) -> alt.Chart:
        """Display User Profile Statistics - Subscription tier, followers, library size"""
        profile = self.user.profile
        library_stats = self.user.getLibraryDiversity()

        if not profile:
            df = pd.DataFrame([{"line": 0, "text": "Profile data unavailable", "tip": "Profile not loaded"}])
        else:
            df = pd.DataFrame([
                {
                    "line": 0,
                    "text": f"{profile['subscription_type'].title()} • {profile['followers']} followers",
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
            .mark_text(align="center", baseline="middle", fontSize=16, fontWeight="bold", color="#1DB954")
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
        growth_df = self.user.getLibraryGrowthPattern()

        if growth_df.empty:
            return alt.Chart(pd.DataFrame({"text": ["No saved tracks timeline data"]})).mark_text().encode(text="text:N").properties(width=width, height=height)

        # Convert period to string for visualization
        growth_df['period_str'] = growth_df['year_month'].astype(str)

        return (
            alt.Chart(growth_df)
            .mark_bar(color="#1DB954")
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
                color=alt.Color("type:N", scale=alt.Scale(range=["#1DB954", "#FF6B35"])),
                tooltip=["artist:N", "rank:O", "count:Q", "type:N"]
            )
            .properties(
                width=width,
                height=height,
                title=alt.TitleParams(text="Saved vs Current Preferences", anchor="start", fontSize=18)
            )
        )

    def _top_artists_pie_chart(self, top_n: int = 10, width: int = 380, height: int = 320) -> alt.Chart:
        """Pie chart: Top Artists with listening hours shown in legend."""
        artists_df = self.user.getTopArtists(top_n)
        recent_df = self.user.recent_df

        if artists_df.empty:
            return alt.Chart(pd.DataFrame({"name": ["No data"], "share": [1]})).mark_arc().encode(theta="share:Q").properties(width=width, height=height)

        # Calculate approximate hours per artist from recent plays
        artist_playtime = {}
        if not recent_df.empty:
            for _, play in recent_df.iterrows():
                for artist_name in play.get("artists", "").split(", "):
                    if artist_name in artist_playtime:
                        artist_playtime[artist_name] += play.get("duration_ms", 0)
                    else:
                        artist_playtime[artist_name] = play.get("duration_ms", 0)

        rows = []
        total_weight = 0
        for i, (_, a) in enumerate(artists_df.iterrows()):
            # Use playtime if available, otherwise use inverse rank as weight
            artist_name = a["name"]
            duration_ms = artist_playtime.get(artist_name, (11 - (i + 1)) * 180000)  # ~3min per rank as fallback
            hours = round(duration_ms / (1000 * 60 * 60), 1)
            weight = max(duration_ms, 1)  # Ensure positive weight
            total_weight += weight

            rows.append({
                "artist": artist_name,
                "rank": i + 1,
                "hours": hours,
                "weight": weight,
                "legend_label": f"{artist_name} ({hours}h)"
            })

        # Calculate percentages
        for row in rows:
            row["pct"] = round(100 * row["weight"] / total_weight, 1)

        df = pd.DataFrame(rows)
        return (
            alt.Chart(df)
            .mark_arc(innerRadius=0, stroke="white", strokeWidth=2, outerRadius=140)
            .encode(
                theta=alt.Theta("weight:Q", stack=True),
                color=alt.Color(
                    "artist:N",
                    scale=alt.Scale(scheme="category10"),
                    legend=alt.Legend(
                        orient="right",
                        title="Artist (Hours)",
                        labelLimit=150,
                        symbolSize=60
                    ),
                ),
                tooltip=[
                    alt.Tooltip("artist:N", title="Artist"),
                    alt.Tooltip("hours:Q", title="Est. Hours", format=".1f"),
                    alt.Tooltip("pct:Q", title="Share %", format=".1f"),
                ],
            )
            .properties(
                width=width,
                height=height,
                title=alt.TitleParams(text="Top Artists", anchor="start", fontSize=20),
            )
        )

    def generateDashboard(self, layout: str = "standard") -> None:
        """Layout: title, Annual Stats | Last Played, Favorites title, Top Songs table | Top Artists pie."""
        annual = self._annual_stats_chart()
        last_played = self._last_played_chart()
        favorites_title = self._favorites_title_chart()
        top_songs = self._top_songs_chart()
        top_artists = self._top_artists_pie_chart()

        spacer = alt.Chart(pd.DataFrame([{"x": 0}])).mark_text().encode(x=alt.value(0), text=alt.value("")).properties(width=10, height=24)

        top_row = annual | last_played
        bottom_row = top_songs | top_artists

        self.dashboard = top_row & favorites_title & spacer & bottom_row

        self.dashboard = self.dashboard.properties(
            title=alt.TitleParams(
                text=f"{self.user.username}'s Spotify Dashboard",
                anchor="middle",
                fontSize=36 if layout == "standard" else 28,
            ),
            padding={"left": 30, "right": 30, "top": 20, "bottom": 20},
            spacing=20,
            center=True
        ).configure_view(
            strokeWidth=0.5,
            strokeOpacity=0.3
        ).configure_axis(
            labelFontSize=11,
            titleFontSize=14,
        ).configure_legend(
            labelFontSize=10,
            titleFontSize=12,
            labelLimit=120
        )

    def save(self, filename: Optional[str] = None) -> None:
        """Save Dashboard to Files"""
        if self.dashboard is None:
            print("Dashboard Not Generated")
            return

        if filename is None:
            filename = f"{self.user.username}_Dashboard"

        script_dir = os.path.dirname(os.path.abspath(__file__))
        charts_dir = os.path.join(script_dir, "Charts")
        os.makedirs(charts_dir, exist_ok=True)

        # Generate different layouts
        layouts = [
            ("Standard", "standard"),
            ("Portrait", "portrait"),
            ("Landscape", "landscape"),
            ("Tablet", "tablet"),
        ]

        for layout_name, layout_type in layouts:
            print(f"Generating {layout_name} layout...")
            self.generateDashboard(layout_type)
            out_name = filename.replace("_Dashboard", f"_{layout_name}")
            path = os.path.join(charts_dir, f"{out_name}.json")
            spec = self.dashboard.to_dict()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(spec, f, indent=2, ensure_ascii=False)

        # Reset to standard and save other formats
        self.generateDashboard("standard")

        # Save as HTML (Interactive)
        with open(os.path.join(charts_dir, f"{filename}.html"), "w", encoding="utf-8") as f:
            f.write(self.dashboard.to_html())

        # Save as PNG and SVG
        self.dashboard.save(os.path.join(charts_dir, f"{filename}.png"))
        self.dashboard.save(os.path.join(charts_dir, f"{filename}.svg"))

        # Save standalone pie chart for React
        pie_chart = self._top_artists_pie_chart(10, 380, 320)
        pie_spec = pie_chart.properties(
            padding=20,
        ).configure_legend(labelFontSize=11, titleFontSize=12).to_dict()
        pie_path = os.path.join(charts_dir, f"{self.user.username}_PieOnly.json")
        with open(pie_path, "w", encoding="utf-8") as f:
            json.dump(pie_spec, f, indent=2, ensure_ascii=False)

        # Save comprehensive data as JSON
        data_path = os.path.join(script_dir, "spotify_data.json")
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(self.user.getComprehensiveData(), f, indent=2, ensure_ascii=False)

        print(f"Dashboard saved to {charts_dir}/ and {data_path}")


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
        user.saveCSVData()
        print("Spotify Dashboard Generated Successfully!")

    except Exception as e:
        print(f"Error During Execution: {e}")
        raise
