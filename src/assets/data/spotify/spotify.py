"""
Spotify Dashboard Generator
Author: Muntakim Rahman
Description: Interacts with Spotify API to Fetch User Data
    (Recently Played, Top Tracks, Saved Library) and Generates Visualizations using Altair.
    Dashboard is Exported as JSON, HTML, PNG, SVG.
"""

# Import Packages
import pandas as pd
import altair as alt

import json
import shutil

import os
from dotenv import load_dotenv

from datetime import datetime
from typing import Optional

import spotipy
from spotipy.oauth2 import SpotifyOAuth


class SpotifyClient:
    """Handles Spotify API Interactions"""

    SCOPES = [
        "user-read-recently-played", # Recently Played Tracks
        "user-top-read", # Top Tracks and Artists
        "user-library-read" # Saved/Liked Tracks (Your Music Library)
    ]

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        redirect_uri = redirect_uri.strip().rstrip("/") # Remove Trailing Slash

        # Initialize Spotipy Client with OAuth
        _script_dir = os.path.dirname(os.path.abspath(__file__))
        self.client = spotipy.Spotify(
            auth_manager = SpotifyOAuth(
                scope = " ".join(self.SCOPES),
                client_id = client_id,
                client_secret = client_secret,
                redirect_uri = redirect_uri,
                cache_path = os.path.join(_script_dir, ".cache"),
            )
        )

    def _parseTrack(self, track: dict) -> dict:
        """Parse Track Data Structure"""
        return {
            "track": track["name"],
            "artists": ", ".join(artist["name"] for artist in track["artists"]),
        }

    def _getSavedTrackBatch(self, batch_size: int, offset: int) -> pd.DataFrame:
        """Fetch User's Saved/Liked Tracks in Batches (for Pagination)"""
        try:
            saved_tracks = self.client.current_user_saved_tracks(limit = batch_size, offset = offset)
            saved_rows = []

            for item in saved_tracks.get("items", []):
                track_data = self._parseTrack(item["track"])
                track_data["added_at"] = item.get("added_at") # Timestamp When Track Added to Library
                saved_rows.append(track_data)

            return pd.DataFrame(saved_rows)
        except Exception as e:
            print(f"Failed to Get Saved Tracks: {e}")
            return pd.DataFrame()

    def getTopTracks(self, limit: int = 10) -> pd.DataFrame:
        """Fetch User's Top Tracks (Long Term)"""
        try:
            tracks = self.client.current_user_top_tracks(limit = limit, time_range = "long_term")
            return pd.DataFrame([self._parseTrack(t) for t in tracks.get("items", [])] )
        except Exception as e:
            print(f"Failed to Get Top Tracks: {e}")
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
                offset += batch_size # Move to Next Batch

            if tracks: # Concatenate Batches
                return pd.concat(tracks, ignore_index = True)
            return pd.DataFrame()

        except Exception as e:
            print(f"Failed to Get All Saved Tracks: {e}")
            return pd.DataFrame()

class SpotifyUser:
    """Represents Artist Spotify User and Their Music Data"""

    def __init__(self, username: str, api_client: SpotifyClient):
        self.username = username
        self.api_client = api_client

        # Spotify Data
        self.recent_df = pd.DataFrame()
        self.top_tracks_df = pd.DataFrame()
        self.saved_tracks_df = pd.DataFrame()

        self._getData()

    def _getData(self) -> None:
        """Get All User Data from Spotify API"""
        print(f"Fetching Spotify Data for {self.username}...")

        self.recent_df = self.api_client.getRecentTracks()
        self.top_tracks_df = self.api_client.getTopTracks()
        self.saved_tracks_df = self.api_client.getSavedTracks()

    def getTopTracks(self, n: int = 10) -> pd.DataFrame:
        """Get Top N Tracks"""
        return self.top_tracks_df.head(n) if not self.top_tracks_df.empty else pd.DataFrame()

    def getYearlyLibraryGrowth(self) -> pd.DataFrame:
        """Analyze Yearly Library Growth (Cumulative Tracks + Artists)"""
        if (self.saved_tracks_df.empty) or ('added_at' not in self.saved_tracks_df.columns):
            return pd.DataFrame()

        # Filter Out None Values
        df = self.saved_tracks_df[self.saved_tracks_df['added_at'].notna()].copy()
        if df.empty:
            return pd.DataFrame()

        try:
            # Convert to Datetime and Group by Year
            df['added_at'] = pd.to_datetime(df['added_at'], utc = True).dt.tz_localize(None)
            df['time_period'] = df['added_at'].dt.to_period('Y')
        except Exception as e:
            print(f"Error Converting 'added_at' to Datetime: {e}")
            return pd.DataFrame()

        growth = df.groupby('time_period')['track'].count().reset_index()
        growth.columns = ['time_period', 'tracks_added']
        growth['time_period'] = growth['time_period'].astype(str)
        growth = growth.sort_values('time_period')
        growth['cumulative_tracks'] = growth['tracks_added'].cumsum()

        # Compute Cumulative Distinct Artists up to Each Year
        cumulative_artists: dict = {}
        for yr_str in sorted(growth['time_period'].unique()):
            total_artists: set = set()
            for artists_str in df.loc[df['time_period'].astype(str) <= yr_str, 'artists'].dropna():
                for artist in str(artists_str).split(', '):
                    if artist.strip(): # Avoid Empty Artist Names
                        total_artists.add(artist.strip())
            cumulative_artists[yr_str] = len(total_artists)
        # Map Cumulative Artist Counts to Growth DataFrame
        growth['cumulative_artists'] = growth['time_period'].map(cumulative_artists).fillna(0).astype(int)

        return growth

    # Map Known Collaboration / Variant Artist Names to Canonical Name
    _ARTIST_ALIASES: dict = {
        "Alka Yagnik & Arvind Hasabnish": "Alka Yagnik",
    }

    def _normalizeArtist(self, name: str) -> str:
        """Return Canonical Artist Name, Resolving Known Aliases."""
        return self._ARTIST_ALIASES.get(name, name)

    def getTopSavedArtists(self, n: int = 10) -> pd.DataFrame:
        """Get Most Saved/Liked Artists from Library, with Alias Consolidation."""
        if self.saved_tracks_df.empty:
            return pd.DataFrame()

        # Split Comma-Separated Artist Credits, Then Normalize Each Name
        artists = []
        for artists_str in self.saved_tracks_df['artists']:
            for artist in artists_str.split(','):
                artists.append(self._normalizeArtist(artist.strip()))

        artist_counts = pd.Series(artists).value_counts().head(n).reset_index()
        artist_counts.columns = ['artist', 'track_count']
        return artist_counts

class SpotifyDashboard:
    """Creates Visualizations for Spotify User Data"""

    GREEN = "#0e7a38" # Darkened Spotify Green
    def __init__(self, user: SpotifyUser):
        self.user = user
        self.colors = [
            "#00008B", "#FF8C00", "#32CD32", "#DC143C",
            "#800080", "#00CED1", "#FFA500", "#4E342E",
            "#00695C", "#B8860B",
        ]

        self.dashboard = None
        self.generateDashboard()

    def generateTrackTable(self, df: pd.DataFrame,
        title: str,
        subtitle: str = "",
        width: int = 380,
        height: int = 320,
        show_time: bool = False,
        hide_artist: bool = False,
        font_scale: float = 1.0,
    ) -> alt.Chart:
        """Generate Track Table for Top Songs and Recently Played Charts"""

        # Layout Constants
        ROW_PADDING = 20 # Vertical Inset from Top/Bottom Edges of the Chart
        ARTIST_TOP_OFFSET = 32 # Artist Row Starts Lower to Sit Below Song Title
        ARTIST_BOTTOM_PAD = 8 # Bottom Inset for Artist Range
        RANK_X = 18 # Horizontal Center of the Rank Number Column
        TEXT_START_X = 36 # Left Edge Where Song/Artist Text Begins
        TIME_RIGHT_MARGIN = 10 # Right Margin for the Time Column

        # Font Size Constants
        RANK_FONT = 13
        SONG_FONT = 14
        ARTIST_FONT = 12
        TIME_FONT = 12
        TITLE_FONT = 20
        SUBTITLE_FONT = 13
        MIN_LARGE_FONT = 9 # Floor for Rank / Song
        MIN_SMALL_FONT = 8 # Floor for Artist / Time

        # Text Overflow Constants
        TIME_TEXT_CHARS = 9 # Max Characters in Time Text (e.g. "12:34 PM")
        CHAR_WIDTH_RATIO = 0.6 # Average Character Width as Fraction of Font Size
        MIN_SONG_LIMIT = 40 # Minimum Pixel Width for Song Text
        SONG_TIME_GAP = 8 # Horizontal Gap Between Song and Time Text
        TEXT_RIGHT_PAD = 5 # Right Padding When No Time Column is Shown

        row_range = [ROW_PADDING, height - ROW_PADDING]
        artist_range = [ARTIST_TOP_OFFSET, height - ARTIST_BOTTOM_PAD]

        # Calculate Text Limits to Prevent Overflow
        time_x = width - TIME_RIGHT_MARGIN if show_time else None
        if time_x:
            time_font = max(MIN_SMALL_FONT, round(TIME_FONT * font_scale))
            time_text_width = round(TIME_TEXT_CHARS * time_font * CHAR_WIDTH_RATIO)
            song_limit = max(MIN_SONG_LIMIT, time_x - time_text_width - TEXT_START_X - SONG_TIME_GAP)
        else:
            song_limit = width - TEXT_START_X - TEXT_RIGHT_PAD
        artist_limit = song_limit

        rank_col = (
            alt.Chart(df)
            .mark_text(align = "center", baseline = "middle", fontSize = max(MIN_LARGE_FONT, round(RANK_FONT * font_scale)), fontWeight = "bold", color = "#333")
            .encode(
                x = alt.value(RANK_X),
                y = alt.Y("y_pos:O", title = None, axis = None, scale = alt.Scale(range = row_range)),
                text = alt.Text("rank:O"),
                tooltip = [alt.Tooltip("song:N", title = "Song"), alt.Tooltip("artist:N", title = "Artist")],
            )
        )
        song_col = (
            alt.Chart(df)
            .mark_text(align = "left", baseline = "middle", fontSize = max(MIN_LARGE_FONT, round(SONG_FONT * font_scale)), fontWeight = "bold", color = self.GREEN, limit = song_limit)
            .encode(
                x = alt.value(TEXT_START_X),
                y = alt.Y("y_pos:O", title = None, axis = None, scale = alt.Scale(range = row_range)),
                text = alt.Text("song:N"),
                tooltip = [alt.Tooltip("song:N", title = "Song"), alt.Tooltip("artist:N", title = "Artist")],
            )
        )
        artist_col = (
            alt.Chart(df)
            .mark_text(align = "left", baseline = "middle", fontSize = max(MIN_SMALL_FONT, round(ARTIST_FONT * font_scale)), color = "#444",
                       limit = artist_limit, opacity = 0 if hide_artist else 1)
            .encode(
                x = alt.value(TEXT_START_X),
                y = alt.Y("y_pos:O", title = None, axis = None, scale = alt.Scale(range = artist_range)),
                text = alt.Text("artist:N"),
            )
        )

        layers = [rank_col, song_col, artist_col]
        if show_time:
            time_col = (
                alt.Chart(df)
                .mark_text(align = "right", baseline = "middle", fontSize = max(MIN_SMALL_FONT, round(TIME_FONT * font_scale)), color = "#555")
                .encode(
                    x = alt.value(width - TIME_RIGHT_MARGIN),
                    y = alt.Y("y_pos:O", title = None, axis = None, scale = alt.Scale(range = row_range)),
                    text = alt.Text("time:N"),
                )
            )
            layers.append(time_col)

        title_params = alt.TitleParams(
            text = title,
            anchor = "start",
            fontSize = round(TITLE_FONT * font_scale),
            **(dict(subtitle = subtitle,  subtitleFontSize = round(SUBTITLE_FONT * font_scale), subtitleColor = "#444") if subtitle else {}),
        )

        return (
            alt.layer(*layers)
            .resolve_scale(y = "independent")
            .properties(width = width, height = height, title = title_params)
        )

    def generateTopSongsChart(self, top_n: int = 10, width: int = 380, height: int = 320, font_scale: float = 1.0, hide_artist: bool = False) -> alt.Chart:
        """Generate Top Songs Chart"""
        range_label = "Past Year"
        tracks_df = self.user.getTopTracks(top_n)

        if tracks_df.empty:
            df = pd.DataFrame([{"rank": 1, "song": "No data", "artist": "", "y_pos": 0}])
        else:
            rows = []
            for i, (_, t) in enumerate(tracks_df.iterrows()):
                rows.append({
                    "rank": i + 1,
                    "song": t["track"],
                    "artist": t["artists"],
                    "y_pos": i,
                })
            df = pd.DataFrame(rows)

        return self.generateTrackTable(df, "Top Songs", range_label, width, height, show_time = False, hide_artist = hide_artist, font_scale = font_scale)

    def generateRecentlyPlayedChart(self, top_n: int = 10, width: int = 760, height: int = 300, font_scale: float = 1.0, hide_artist: bool = False) -> alt.Chart:
        """Generate Recently Played Chart"""
        recent_df = self.user.recent_df

        if recent_df.empty:
            df = pd.DataFrame([{"rank": 1, "song": "No recent plays", "artist": "", "time": "", "y_pos": 0}])
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
                })
            df = pd.DataFrame(rows)

        return self.generateTrackTable(df, "Recently Played", "", width, height, show_time=True, hide_artist=hide_artist, font_scale=font_scale)

    def generateLibraryGrowthChart(self, width: int = 600, height: int = 300, font_scale: float = 1.0, title_anchor: str = "start") -> alt.Chart:
        """Generate Yearly Library Growth Area Chart"""

        # ── Layout Constants
        TRACKS_HEIGHT_RATIO = 0.55  # Fraction of Total Height for Tracks Sub-Chart
        ARTISTS_HEIGHT_RATIO = 0.45  # Fraction of Total Height for Artists Sub-Chart
        AREA_STROKE_WIDTH = 2 # Border Stroke Width on Area Marks
        TRACKS_AREA_OPACITY = 0.6 # Fill Opacity for Tracks Area
        ARTISTS_AREA_OPACITY = 0.5 # Fill Opacity for Artists Area
        LABEL_ANGLE = -45 # X-Axis Label Rotation (Deg)

        # Font Size Constants
        AXIS_LABEL_FONT = 9 # Axis Tick Label Font Size
        AXIS_TITLE_FONT = 10 # Axis Title Font Size
        CHART_TITLE_FONT = 16 # Sub-Chart Title Font Size

        # Point Marker Constants
        TRACKS_POINT_SIZE = 60 # Circle Size for Track Data Points
        TRACKS_POINT_STROKE = 1 # Stroke Width on Track Data Points
        ARTISTS_POINT_SIZE = 50 # Circle Size for Artist Data Points

        # Color Constants
        ARTIST_COLOR = "#1a237e" # Dark Blue for Artists Sub-Chart

        growth_df = self.user.getYearlyLibraryGrowth()
        if growth_df.empty:
            return alt.Chart(
                pd.DataFrame(
                    {"text": ["No Annual Library Growth Data"]}
                )
            ).mark_text().encode(
                text = "text:N"
            ).properties(
                width = width, height = height
            )
        growth_df['year'] = growth_df['time_period'].astype(str)

        def area_chart(y_field, y_title, color, opacity, height_ratio, chart_title):
            """Generate Area Sub-Chart for a Growth Metric"""
            tooltip = [alt.Tooltip("year:O", title = "Year"), alt.Tooltip(y_field, title = y_title)]
            return (
                alt.Chart(growth_df)
                .mark_area(color = color, opacity = opacity, stroke = color, strokeWidth = AREA_STROKE_WIDTH)
                .encode(
                    x = alt.X("year:O", title = "Year", axis = alt.Axis(
                        labelAngle = LABEL_ANGLE,
                        labelFontSize = round(AXIS_LABEL_FONT * font_scale),
                        titleFontSize = round(AXIS_TITLE_FONT * font_scale),
                    )),
                    y = alt.Y(y_field, title = y_title, axis = alt.Axis(
                        labelFontSize = round(AXIS_LABEL_FONT * font_scale),
                        titleFontSize = round(AXIS_TITLE_FONT * font_scale),
                    )),
                    tooltip = tooltip,
                )
                .properties(
                    width = width,
                    height = round(height * height_ratio),
                    title = alt.TitleParams(text = chart_title, anchor = title_anchor, fontSize = round(CHART_TITLE_FONT * font_scale)),
                )
            ), tooltip

        def points_chart(y_field, color, point_size, tooltip, stroke = None, stroke_width = None):
            """Generate Circle Point Overlay to Highlight Yearly Totals"""
            mark_kwargs = dict(color = color, size = point_size)
            if stroke:
                mark_kwargs.update(stroke = stroke, strokeWidth = stroke_width)
            return (
                alt.Chart(growth_df)
                .mark_circle(**mark_kwargs)
                .encode(x = alt.X("year:O"), y = alt.Y(y_field), tooltip = tooltip)
            )

        # Chart 1: Cumulative Tracks
        tracks_area, tracks_tooltip = area_chart(
            "cumulative_tracks:Q", "Total Tracks", self.GREEN, TRACKS_AREA_OPACITY,
            TRACKS_HEIGHT_RATIO, "Library Growth (Tracks)",
        )
        tracks_points = points_chart(
            "cumulative_tracks:Q", self.GREEN, TRACKS_POINT_SIZE, tracks_tooltip,
            stroke = "white", stroke_width = TRACKS_POINT_STROKE,
        )
        tracks_chart = tracks_area + tracks_points

        # Chart 2: Cumulative Artists
        if 'cumulative_artists' in growth_df.columns:
            artists_area, artists_tooltip = area_chart(
                "cumulative_artists:Q", "Total Artists", ARTIST_COLOR, ARTISTS_AREA_OPACITY,
                ARTISTS_HEIGHT_RATIO, "Library Growth (Artists)",
            )
            artists_points = points_chart(
                "cumulative_artists:Q", ARTIST_COLOR, ARTISTS_POINT_SIZE, artists_tooltip,
            )
            artists_chart = artists_area + artists_points
            return alt.vconcat(tracks_chart, artists_chart)

    def generateTopArtistsPieChart(self, top_n: int = 10, width: int = 400, height: int = 340, font_scale: float = 1.0, title_anchor: str = "start") -> alt.Chart:
        """Generate Top Artists Pie Chart"""

        # Layout Constants
        OUTER_RADIUS_RATIO = 0.44  # Pie Radius as Fraction of Smaller Dimension
        ARC_STROKE_WIDTH = 1 # Border Stroke Width on Arc Slices

        # Font Size Constants
        TITLE_FONT = 20 # Chart Title Font Size
        SUBTITLE_FONT = 13 # Chart Subtitle Font Size

        artists_df = self.user.getTopSavedArtists(top_n)
        if artists_df.empty:
            return alt.Chart(pd.DataFrame({"name": ["No data"], "share": [1]})).mark_arc().encode(theta = "share:Q").properties(width=width, height=height)

        total = artists_df["track_count"].sum()
        rows = []
        for i, (_, artist) in enumerate(artists_df.iterrows()):
            rows.append({
                "artist": artist["artist"],
                "count": int(artist["track_count"]),
                "pct": round(100 * artist["track_count"] / total, 1),
            })
        df = pd.DataFrame(rows)
        outer_r = int(min(width, height) * OUTER_RADIUS_RATIO)

        return (
            alt.Chart(df)
            .mark_arc(innerRadius = 0, stroke = "black", strokeWidth = ARC_STROKE_WIDTH, outerRadius = outer_r)
            .encode(
                theta = alt.Theta("count:Q", stack = True),
                color = alt.Color(
                    "artist:N",
                    scale = alt.Scale(range = self.colors),
                    legend = None,
                ),
                tooltip = [
                    alt.Tooltip("artist:N", title = "Artist"),
                    alt.Tooltip("count:Q", title = "Saved Tracks"),
                    alt.Tooltip("pct:Q", title = "Share (%)", format = ".1f"),
                ],
            )
            .properties(
                width = width,
                height = height,
                title = alt.TitleParams(
                    text = "Top Artists",
                    subtitle = "By Saved Tracks",
                    anchor = title_anchor,
                    fontSize = round(TITLE_FONT * font_scale),
                    subtitleFontSize = round(SUBTITLE_FONT * font_scale),
                    subtitleColor = "#444",
                ),
            )
        )

    def generateArtistsLegendChart(self, top_n: int = 10, width: int = 320, height: int = 340, font_scale: float = 1.0) -> alt.Chart:
        """Generate Artists Legend for Pie Chart"""

        # Layout Constants
        ROW_TOP_OFFSET = 30 # Vertical Start Position of First Legend Row
        VERTICAL_PADDING = 40 # Total Vertical Padding for Row Spacing
        MIN_ROW_STEP = 22 # Minimum Pixels Between Legend Rows
        DOT_X = 26 # Horizontal Position of Color Dots
        LABEL_X = 46 # Horizontal Position of Artist Labels
        LABEL_DX = 12 # Horizontal Offset Between Dot and Label

        # Dot Marker Constants
        LEGEND_MARKER_SIZE = 120 # Size of Legend Color Markers
        MARKER_STROKE_WIDTH = 1.5 # Border Stroke Width on Markers

        # Font Size Constants
        LABEL_FONT = 13 # Artist Label Font Size
        EMPTY_TITLE_FONT = 14 # Placeholder Title Font Size

        artists_df = self.user.getTopSavedArtists(top_n)

        rows = []
        for i, (_, artist) in enumerate(artists_df.head(top_n).iterrows()):
            artist_name = artist["artist"]
            count = int(artist["track_count"])
            rows.append({
                "artist": artist_name,
                "label": f"{artist_name} ({count:,})",
                "idx": i,
            })

        if not rows:
            return alt.Chart(
                pd.DataFrame({"t": [""]})
            ).mark_text().encode(
                text = "t:N"
            ).properties(width = width, height = height)

        df = pd.DataFrame(rows)
        ordered_domain = df["artist"].tolist() # Ensure Legend Colors Match Pie Slices
        color_scale = alt.Scale(range = self.colors, domain = ordered_domain)

        row_step = max(MIN_ROW_STEP, int((height - VERTICAL_PADDING) / len(df)))

        # Legend chart: colored legend_markers + artist legend_labels
        legend_markers = (
            alt.Chart(df)
            .mark_point(filled = True, size = LEGEND_MARKER_SIZE, stroke = "black", strokeWidth = MARKER_STROKE_WIDTH)
            .encode(
                y = alt.Y(
                    "idx:O",
                    title = None,
                    axis = None,
                    scale = alt.Scale(
                        range = [ROW_TOP_OFFSET, ROW_TOP_OFFSET + row_step * (len(df) - 1)]
                    )
                ),
                x = alt.value(DOT_X),
                color = alt.Color("artist:N", scale = color_scale, legend = None),
            )
        )
        legend_labels = (
            alt.Chart(df)
            .mark_text(align = "left", baseline = "middle", fontSize = round(LABEL_FONT * font_scale), dx = LABEL_DX)
            .encode(
                y = alt.Y(
                    "idx:O", title = None, axis = None,
                    scale = alt.Scale(
                        range = [ROW_TOP_OFFSET, ROW_TOP_OFFSET + row_step * (len(df) - 1)]
                    )
                ),
                x = alt.value(LABEL_X),
                text = alt.Text("label:N"),
                color = alt.value("#333"),
            )
        )
        return (
            (legend_markers + legend_labels)
            .resolve_scale(y = "shared")
            .properties(
                width = width,
                height = height,
                title = alt.TitleParams(
                    text = "", anchor = "start", fontSize = EMPTY_TITLE_FONT, color = "#555"
                ),
            )
        )

    def generateDashboard(self, layout: str = "standard") -> None:
        """Generate Complete Dashboard

        Layouts
        -------
            Standard  → {username}_Standard.json (Width > 1200 px)
            Tablet    → {username}_Tablet.json (Width ≤ 1200 px)
            Landscape → {username}_Landscape.json (Width ≤  900 px)
            Portrait  → {username}_Portrait.json (Width ≤  550 px)

        Row Structure
        -------------
            Spotify Library Growth | Top Artists Pie + Legend
            Top Songs | Recently Played
        """

        LAYOUTS = {
            "standard": dict(
                font_scale = 1.00, title_size = 40, spacer_height = 16,
                hide_recent_artist = True, hide_top_artist = True, # Hide Artist Names on Standard Dashboard to Maximize Space for Titles and Charts
                growth_width = 400, growth_height = 320,
                pie_width = 300, pie_height = 320,
                legend_width = 180, legend_height = 320,
                top_width = 370, top_height = 380,
                recent_width = 370, recent_height = 380,
                axis_label = 11, axis_title = 14, legend_label = 10, legend_title = 12,
                padding = {"left": 30, "right": 30, "top": 20, "bottom": 30}, spacing = 20,
            ),
            "tablet_portrait": dict( # Includes iPad Mini (768px), iPad Air (820px)
                font_scale = 0.50, title_size = 28, spacer_height = 5,
                hide_recent_artist = True, hide_top_artist = True, # Hide Artist Names on Smaller Tablet Layout
                vconcat = True, split_charts = True, hconcat_songs = True, # Vertically Concatenated with Pie Chart, Top Songs, Recently Played
                growth_width = 280, growth_height = 160,
                pie_width = 200, pie_height = 200,
                legend_width = 120, legend_height = 200,
                top_width = 280, top_height = 200,
                recent_width = 280, recent_height = 200,
                axis_label = 6, axis_title = 8, legend_label = 6, legend_title = 7,
                padding = {"left": 8, "right": 8, "top": 8, "bottom": 12}, spacing=6,
            ),
            "tablet": dict( # Includes Larger Tablets, iPad Pro, Small Desktops (901-1200px)
                font_scale = 0.65, title_size = 28, spacer_height = 8,
                hide_recent_artist = True, hide_top_artist = True, # Hide Artist Names on Smaller Tablet Layout
                vconcat = True, split_charts = True, hconcat_songs = True, # Vertically Concatenated with Pie Chart, Top Songs, Recently Played
                growth_width = 380, growth_height = 200,
                pie_width = 280, pie_height = 260,
                legend_width = 160, legend_height = 260,
                top_width = 360, top_height = 260,
                recent_width = 360, recent_height = 260,
                axis_label = 8, axis_title = 10, legend_label = 8, legend_title = 9,
                padding = {"left": 14, "right": 14, "top": 12, "bottom": 18}, spacing = 10,
            ),
            "landscape": dict(
                font_scale = 0.57, title_size = 18, spacer_height = 8,
                hide_recent_artist = True, hide_top_artist = True, # Hide Artist Names on Smaller Landscape Layout
                growth_width = 280, growth_height = 180,
                pie_width = 180, pie_height = 180,
                legend_width = 0, legend_height = 0, # No Legend
                top_width = 235, top_height = 200,
                recent_width = 235, recent_height = 200,
                axis_label = 7, axis_title = 9, legend_label = 6, legend_title = 8,
                padding = {"left": 10, "right": 10, "top": 12, "bottom": 18}, spacing = 10,
            ),
            "portrait": dict(
                # Stacked in Single Col; Each Chart Spans Full Width
                font_scale = 0.60, title_size = 14, spacer_height = 0,
                hide_recent_artist = False, hide_top_artist = True,  # No Artist Names on Mobile Top Songs
                growth_width = 200, growth_height = 150, # Narrower Growth
                pie_width = 90, pie_height = 90, # Compact Pie
                legend_width = 0, legend_height = 0, # No Legend
                top_width = 260, top_height = 220, # Full-Width Top Songs
                recent_width = 260, recent_height = 220, # Full-Width Recently Played
                axis_label = 8, axis_title = 9, legend_label = 7, legend_title = 8,
                title_anchor = "middle", # Center Sub-Chart Titles on Mobile
                padding = {"left": 5, "right": 5, "top": 0, "bottom": 15}, spacing = 0,
            ),
        }

        # Fallback to Standard Layout if Unrecognized Layout Specified
        settings = LAYOUTS.get(layout.lower(), LAYOUTS["standard"])

        spacer = alt.Chart(
            pd.DataFrame([{"x": 0}])
        ).mark_text().encode(
            x = alt.value(0),
            text = alt.value("")
        ).properties(width = 10, height = settings["spacer_height"])

        title_anchor = settings.get("title_anchor", "start")
        growth_chart = self.generateLibraryGrowthChart(
            width = settings["growth_width"], height = settings["growth_height"],
            font_scale = settings["font_scale"], title_anchor = title_anchor
        )
        pie_chart = self.generateTopArtistsPieChart(
            width = settings["pie_width"], height = settings["pie_height"],
            font_scale = settings["font_scale"], title_anchor = title_anchor
        )
        pie_legend = self.generateArtistsLegendChart(
            width = settings["legend_width"], height = settings["legend_height"],
            font_scale = settings["font_scale"]) if (settings["legend_width"] > 0) else None
        top_songs = self.generateTopSongsChart(
            width = settings["top_width"], height = settings["top_height"],
            font_scale = settings["font_scale"], hide_artist = settings.get("hide_top_artist", False)
        )
        recently_played = self.generateRecentlyPlayedChart(
            width = settings["recent_width"], height = settings["recent_height"],
            font_scale = settings["font_scale"], hide_artist = settings.get("hide_recent_artist", False)
        )

        if layout.lower() == "portrait":
            self.dashboard = growth_chart | pie_chart
            self._card_data = {
                "topSongs": top_songs,
                "recentlyPlayed": recently_played,
            }
        elif settings.get("vconcat"):
            if settings.get("split_charts"):
                pie_row = pie_chart | pie_legend if (pie_legend is not None) else pie_chart
                self.dashboard = (pie_row & spacer & growth_chart & spacer)
                if settings.get("hconcat_songs"):
                    table_row = (top_songs | recently_played)
                    self.dashboard &= table_row
                else:
                    self.dashboard &= (top_songs & spacer & recently_played)
            else:
                growth_row = (growth_chart | pie_chart)
                if pie_legend is not None:
                    growth_row |= pie_legend
                self.dashboard = (growth_row & spacer & top_songs & spacer & recently_played)
        else:
            growth_row = (growth_chart | pie_chart)
            if pie_legend is not None:
                growth_row |= pie_legend
            table_row = (top_songs | recently_played)
            self.dashboard = (growth_row & spacer & table_row)

        self.dashboard = self.dashboard.properties(
            title = alt.TitleParams(
                text = f"{self.user.username}'s Spotify Dashboard",
                anchor = "middle",
                fontSize = settings["title_size"],
            ),
            padding = settings["padding"],
            spacing = settings["spacing"],
            center = True,
        ).configure_view(
            strokeWidth = 0,
            strokeOpacity = 0,
        ).configure_axis(
            labelFontSize = settings["axis_label"],
            titleFontSize = settings["axis_title"],
        ).configure_legend(
            labelFontSize = settings["legend_label"],
            titleFontSize = settings["legend_title"],
            labelLimit = 120,
        )

    def save(self, filename: Optional[str] = None) -> None:
        """Generate and Save All Responsive Dashboard Layouts.

        Output Files
        -------------
            {username}_Standard.json (Desktop)
            {username}_Tablet.json (Large Tablet / Small Desktop)
            {username}_TabletPortrait.json ) (iPad Mini/Air)
            {username}_Landscape.json (Mobile Landscape)
            {username}_Portrait.json (Mobile Portrait)
            {username}_Dashboard.json (Standard Reference Copy)
            {username}_Dashboard.html (Interactive HTML Reference)
        """
        if filename is None:
            filename = f"{self.user.username}_Dashboard"

        script_dir = os.path.dirname(os.path.abspath(__file__))
        charts_dir = os.path.join(script_dir, "Charts")
        os.makedirs(charts_dir, exist_ok = True)

        def cleanup():
            """Cleanup Temporary Files or Resources if Needed"""
            # Remove .cache
            cache_path = os.path.join(script_dir, ".cache")
            if os.path.isfile(cache_path):
                os.remove(cache_path)

            # Remove __pycache__
            pycache_path = os.path.join(script_dir, "__pycache__")
            if os.path.isdir(pycache_path):
                shutil.rmtree(pycache_path)

        # Generate and Save Responsive Layouts
        responsive_layouts = ["standard", "tablet", "tablet_portrait", "landscape", "portrait"]
        layout_labels = {
            "standard": "Standard",
            "tablet": "Tablet",
            "tablet_portrait": "TabletPortrait",
            "landscape": "Landscape",
            "portrait": "Portrait",
        }

        # Iterate Through
        for layout in responsive_layouts:
            self.generateDashboard(layout)
            out_path = os.path.join(charts_dir, f"{self.user.username}_{layout_labels[layout]}.json")
            spec_dict = self.dashboard.to_dict()
            spec_dict["background"] = None # Transparent
            spec_dict["$schema"] = "https://vega.github.io/schema/vega-lite/v5.20.1.json" # Match Vega-Lite Version Used by Altair

            # For Portrait: Inject Card Data (Top Songs + Recently Played) to Render as Mobile Cards in React
            if (layout == "portrait") and (hasattr(self, "_card_data")):
                songs_spec = self._card_data["topSongs"].to_dict()
                recent_spec = self._card_data["recentlyPlayed"].to_dict()
                if ("datasets" not in spec_dict):
                    spec_dict["datasets"] = {}

                # Inject Top Songs and Recently Played Specs in Dashboard Datasets for Access in React
                songs_dataset = songs_spec.get("datasets", {})
                recent_dataset = recent_spec.get("datasets", {})

                # Update Dashboard Datasets with Card Specs
                spec_dict["datasets"].update(songs_dataset)
                spec_dict["datasets"].update(recent_dataset)

                # Store Dataset Keys for Easy Access
                spec_dict["_cardData"] = {
                    "topSongsDataset": list(songs_dataset.keys())[0] if songs_dataset else None,
                    "recentlyPlayedDataset": list(recent_dataset.keys())[0] if recent_dataset else None,
                }

            # Save Vega-Lite Spec JSON for Each Layout
            with open(out_path, "w", encoding = "utf-8") as f:
                json.dump(spec_dict, f, indent = 2, ensure_ascii = False)

        # Save Standard Layouts as Reference Copy
        self.generateDashboard("standard")
        spec_dict = self.dashboard.to_dict()
        spec_dict["background"] = None # Transparent
        spec_dict["$schema"] = "https://vega.github.io/schema/vega-lite/v5.20.1.json" # Match Vega-Lite Version Used by Altair
        dashboard_json_path = os.path.join(charts_dir, f"{filename}.json")

        # Export Vega-Lite Spec JSON
        with open(dashboard_json_path, "w", encoding = "utf-8") as f:
            json.dump(spec_dict, f, indent = 2, ensure_ascii = False)

        # Export HTML Reference Copy
        html_path = os.path.join(charts_dir, f"{filename}.html")
        with open(html_path, "w", encoding = "utf-8") as f:
            f.write(self.dashboard.to_html())

        # Export Static PNG/SVG of Dashboard
        self.dashboard.save(os.path.join(charts_dir, f"{filename}.png"))
        self.dashboard.save(os.path.join(charts_dir, f"{filename}.svg"))

        cleanup()


if __name__ == '__main__':
    _script_dir = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(_script_dir, ".env"))

    # Environment Variables for Spotify API Credentials
    CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

    try:
        if not CLIENT_ID or not CLIENT_SECRET:
            raise ValueError(
                "Missing SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET. "
                f"Create .env file With:\n"
                "  SPOTIFY_CLIENT_ID = your_client_id\n"
                "  SPOTIFY_CLIENT_SECRET = your_client_secret\n"
                "  SPOTIFY_REDIRECT_URI = your_redirect_uri\n"
            )

        client = SpotifyClient(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
        user = SpotifyUser(username = "Muntakim", api_client = client)
        SpotifyDashboard(user).save()
        print("Spotify Dashboard Generated Successfully!")

    except Exception as e:
        print(f"Error During Execution: {e}")
        raise
