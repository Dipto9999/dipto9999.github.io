"""
GoodReads Dashboard Generator
Author: Muntakim Rahman
Description: Fetches Library Data from GoodReads RSS Feeds (Public API Retired in 2020)
    and Generates Visualizations using Altair. Replaces the Manual CSV Export + Notebook Flow.
    Dashboard is Exported as Responsive Vega-Lite JSONs alongside goodreads.csv / goodreads_reviews.csv.

Usage
-----
    python goodreads.py            # Fetch Fresh Data from RSS (Requires GOODREADS_USER_ID in .env)
    python goodreads.py --offline  # Regenerate Charts from Existing goodreads.csv (No Network)
"""

# Import Packages
import pandas as pd
import altair as alt

import json
import shutil
import sys

import os
from dotenv import load_dotenv

import requests
import xml.etree.ElementTree as ET

from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Optional


class GoodReadsClient:
    """Fetches Shelf Data via GoodReads RSS Feeds (No Auth Needed for Public Profiles)"""

    RSS_URL = "https://www.goodreads.com/review/list_rss/{user_id}"
    SHELVES = ["read", "currently-reading", "to-read"]

    def __init__(self, user_id: str):
        self.user_id = user_id.strip()

    def _parseDate(self, rfc822: Optional[str]) -> str:
        """Convert RSS Date (RFC 822) to YYYY/MM/DD Format Used by the Dashboard"""
        if not rfc822 or not rfc822.strip():
            return ""
        try:
            return parsedate_to_datetime(rfc822.strip()).strftime("%Y/%m/%d")
        except (TypeError, ValueError):
            return ""

    def _parseItem(self, item: ET.Element, shelf: str) -> dict:
        """Parse a Single RSS <item> into a Flat Book Record"""
        def text(tag: str, default: str = "") -> str:
            el = item.find(tag)
            return (el.text or default).strip() if (el is not None and el.text) else default

        # num_pages May Be a Direct Element or Nested Under <book>
        pages = text("num_pages")
        if not pages:
            book_el = item.find("book")
            if book_el is not None:
                pages_el = book_el.find("num_pages")
                if (pages_el is not None) and pages_el.text:
                    pages = pages_el.text.strip()

        return {
            "Book Id": text("book_id"),
            "Title": text("title"),
            "ISBN": text("isbn"),
            "ISBN13": "",  # Not Exposed via RSS
            "Authors": text("author_name"),
            "Publisher": "",  # Not Exposed via RSS
            "Year Published": text("book_published"),
            "Date Added": self._parseDate(text("user_date_added")),
            "Date Read": self._parseDate(text("user_read_at")),
            "Number of Pages": pages,
            "My Rating": text("user_rating", "0"),
            "Average Rating": text("average_rating", "0"),
            "My Review": text("user_review", " ") or " ",
            "Spoiler": "",
            "Private Notes": "",
            "Owned Copies": "0",
            "Exclusive Shelf": shelf,
            "Read Count": "1" if (shelf == "read") else "0",
            "Bookshelves": text("user_shelves") or shelf,
        }

    def getShelf(self, shelf: str) -> list:
        """Fetch All Items on a Shelf (Handles Pagination — RSS Caps at 100 Items/Page)"""
        records = []
        page = 1

        while True:
            response = requests.get(
                self.RSS_URL.format(user_id = self.user_id),
                params = {"shelf": shelf, "page": page},
                headers = {"User-Agent": "Mozilla/5.0 (Portfolio Dashboard Generator)"},
                timeout = 30,
            )
            response.raise_for_status()

            items = ET.fromstring(response.content).findall("./channel/item")
            if not items:
                break

            records.extend(self._parseItem(item, shelf) for item in items)
            if len(items) < 100:  # Last Page
                break
            page += 1

        return records

    def getLibrary(self) -> pd.DataFrame:
        """Fetch All Shelves and Combine into a Single DataFrame"""
        records = []
        for shelf in self.SHELVES:
            shelf_records = self.getShelf(shelf)
            print(f"Fetched {len(shelf_records)} Books from '{shelf}' Shelf")
            records.extend(shelf_records)

        if not records:
            raise ValueError(
                f"No Books Found for GoodReads User {self.user_id}. "
                "Check that the Profile is Public and the User ID is Correct."
            )

        df = pd.DataFrame(records)
        df["My Rating"] = pd.to_numeric(df["My Rating"], errors = "coerce").fillna(0).astype(int)
        df["Average Rating"] = pd.to_numeric(df["Average Rating"], errors = "coerce").fillna(0.0)
        df["Number of Pages"] = pd.to_numeric(df["Number of Pages"], errors = "coerce").fillna(0).astype(int)
        return df

class GoodReadsDashboard:
    """Generates Responsive Vega-Lite Dashboards from GoodReads Library Data"""

    ORDERED_COLUMNS = [
        "Book Id", "Title", "ISBN", "ISBN13",
        "Authors", "Publisher", "Year Published",
        "Date Added", "Date Read", "Number of Pages",
        "My Rating", "Average Rating", "My Review",
        "Spoiler", "Private Notes",
        "Owned Copies", "Exclusive Shelf", "Read Count",
        "Bookshelves",
    ]

    def __init__(self, library_df: pd.DataFrame, username: str = "Muntakim"):
        self.username = username
        self.library_df = library_df[self.ORDERED_COLUMNS]

        read_df = self.library_df[self.library_df["Exclusive Shelf"] == "read"].copy()
        # Charts Need a Read Year — Fall Back to Date Added if GoodReads Has No Read Date
        read_df["Date Read"] = read_df["Date Read"].replace("", pd.NA).fillna(read_df["Date Added"])
        self.read_df = read_df[read_df["Date Read"].notna() & (read_df["Date Read"] != "")]

    def generateRatingsBarchart(self, width: int, height: int, settings: dict) -> alt.Chart:
        """Grouped Bar Chart — My Rating vs GoodReads Average per Book"""
        formatted_df = self.read_df.copy()
        formatted_df["SummarizedTitle"] = formatted_df["Title"].str.split(":").str[0]
        formatted_df["Date Read"] = formatted_df["Date Read"].str.split("/").str[0].astype(int)

        formatted_df.rename(
            columns = {
                "My Rating": self.username,
                "Average Rating": "GoodReads Average",
                "Date Read": "Year",
            },
            inplace = True
        )

        melted_df = pd.melt(
            formatted_df,
            id_vars = ["SummarizedTitle", "Title", "Authors", "Year"],
            value_vars = [self.username, "GoodReads Average"],
            var_name = "Reviewer",
            value_name = "Rating"
        )

        return alt.Chart(melted_df).mark_bar(size = settings["bar_size"]).encode(
            x = alt.X(
                "Rating:Q", title = "Rating",
                scale = alt.Scale(domain = [0, 5])
            ),
            y = alt.Y(
                "SummarizedTitle:N", title = "Book",
                sort = alt.EncodingSortField(field = "Rating", order = "descending"),
                axis = alt.Axis(labelLimit = settings["label_limit"]),
            ),
            color = alt.Color(
                "Reviewer:N",
                scale = alt.Scale(
                    domain = [self.username, "GoodReads Average"],
                    range = ["seagreen", "orange"]
                ),
                legend = alt.Legend(title = "Reviewer", symbolType = "square"),
            ),
            yOffset = "Reviewer:N",
            tooltip = [
                alt.Tooltip("Title", title = "Title"),
                alt.Tooltip("Authors", title = "Author(s)"),
                alt.Tooltip("Year", title = "Year Read"),
                alt.Tooltip("Reviewer", title = "Reviewer"),
                alt.Tooltip("Rating", title = "Rating"),
            ]
        ).properties(
            width = width,
            height = height,
            title = alt.Title(settings["ratings_title"], fontSize = settings["sub_title"]),
        )

    def generateYearBarchart(self, width: int, height: int, settings: dict) -> alt.Chart:
        """Annual Summary — Books Read per Year, Colored by Pages"""
        agg_df = self.read_df.copy()
        agg_df["Year Read"] = agg_df["Date Read"].str.split("/").str[0].astype(int)

        years_df = pd.DataFrame({"Year": range(agg_df["Year Read"].min(), agg_df["Year Read"].max() + 1)})
        agg_df = agg_df.groupby("Year Read")\
            .agg(Books = ("Title", "count"), Pages = ("Number of Pages", "sum"))\
            .reset_index()\
            .rename(columns = {"Year Read": "Year"})

        agg_df = pd.merge(years_df, agg_df, on = "Year", how = "left").fillna(0)
        agg_df["Books"] = agg_df["Books"].astype(int)
        agg_df["Pages"] = agg_df["Pages"].astype(int)
        agg_df.sort_values(by = "Year", inplace = True)

        return alt.Chart(agg_df).mark_bar().encode(
            x = alt.X("Year:N", title = "Year", axis = alt.Axis(labelAngle = settings["year_label_angle"])),
            y = alt.Y("Books:Q", title = "Books (#)"),
            color = alt.Color(
                "Pages:Q", title = "Pages (#)",
                scale = alt.Scale(scheme = "greens"),
                legend = alt.Legend(title = "Pages (#)"),
            ),
            tooltip = [
                alt.Tooltip("Year:O", title = "Year"),
                alt.Tooltip("Books:Q", title = "Books (#)"),
                alt.Tooltip("Pages:Q", title = "Pages (#)"),
            ]
        ).properties(
            width = width,
            height = height,
            title = alt.Title(settings["annual_title"], fontSize = settings["sub_title"]),
        )

    def generateDashboard(self, layout: str = "standard") -> alt.HConcatChart:
        """Generate Complete Dashboard

        Layouts
        -------
            Standard  → {username}_Standard.json (Desktop)
            Tablet    → {username}_Tablet.json (Tablet / Small Desktop)
            Landscape → {username}_Landscape.json (Mobile Landscape)
            Portrait  → {username}_Portrait.json (Mobile Portrait)
        """

        LAYOUTS = {
            "standard": dict(
                ratings_width = 300, ratings_height = 200,
                annual_width = 250, annual_height = 200,
                ratings_title = f"{self.username}'s Ratings", annual_title = "Annual Summary",
                sub_title = 24, top_title = 40, bar_size = 10, label_limit = 0,
                axis_label = 12, axis_title = 14, legend_label = 14, legend_title = 18,
                year_label_angle = -45, legend_orient = "right",
                padding = None, spacing = 20,
            ),
            "tablet": dict(
                ratings_width = 180, ratings_height = 160,
                annual_width = 120, annual_height = 160,
                ratings_title = f"{self.username}'s Ratings", annual_title = "Annual Summary",
                sub_title = 14, top_title = 18, bar_size = 6, label_limit = 80,
                axis_label = 8, axis_title = 10, legend_label = 8, legend_title = 9,
                year_label_angle = -45, legend_orient = "right",
                padding = {"left": 12, "right": 12, "top": 5, "bottom": 8}, spacing = 10,
            ),
            "landscape": dict(
                ratings_width = 200, ratings_height = 120,
                annual_width = 110, annual_height = 120,
                ratings_title = "Ratings", annual_title = "Annual",
                sub_title = 12, top_title = 14, bar_size = 5, label_limit = 60,
                axis_label = 7, axis_title = 9, legend_label = 6, legend_title = 8,
                year_label_angle = -45, legend_orient = "right",
                padding = {"left": 20, "right": 20, "top": 8, "bottom": 10}, spacing = 8,
            ),
            "portrait": dict(
                ratings_width = 90, ratings_height = 90,
                annual_width = 70, annual_height = 90,
                ratings_title = "Ratings", annual_title = "Annual",
                sub_title = 10, top_title = 12, bar_size = 4, label_limit = 50,
                axis_label = 7, axis_title = 8, legend_label = 7, legend_title = 8,
                year_label_angle = -45, legend_orient = "bottom",
                padding = {"left": 8, "right": 8, "top": 2, "bottom": 2}, spacing = 5,
            ),
        }

        # Fallback to Standard Layout if Unrecognized Layout Specified
        settings = LAYOUTS.get(layout.lower(), LAYOUTS["standard"])

        ratings_chart = self.generateRatingsBarchart(
            width = settings["ratings_width"], height = settings["ratings_height"], settings = settings
        )
        year_chart = self.generateYearBarchart(
            width = settings["annual_width"], height = settings["annual_height"], settings = settings
        )

        dashboard = alt.hconcat(
            ratings_chart,
            year_chart,
            spacing = settings["spacing"],
        ).properties(
            title = alt.TitleParams(
                text = f"{self.username}'s GoodReads Dashboard",
                anchor = "middle",
                fontSize = settings["top_title"],
            ),
        ).configure_view(
            strokeWidth = 1.5,
            strokeOpacity = 0,
        ).configure_axis(
            labelFontSize = settings["axis_label"],
            titleFontSize = settings["axis_title"],
        ).configure_legend(
            labelFontSize = settings["legend_label"],
            titleFontSize = settings["legend_title"],
            orient = settings["legend_orient"],
        )

        if settings["padding"] is not None:
            dashboard = dashboard.properties(padding = settings["padding"])

        return dashboard

    def save(self) -> None:
        """Save CSVs and All Responsive Dashboard Layouts

        Output Files
        -------------
            goodreads.csv (Cleaned Library Data)
            goodreads_reviews.csv (Read Books with Reviews — Rendered as Table in React)
            Charts/{username}_Standard.json (Desktop)
            Charts/{username}_Tablet.json (Tablet / Small Desktop)
            Charts/{username}_Landscape.json (Mobile Landscape)
            Charts/{username}_Portrait.json (Mobile Portrait)
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        charts_dir = os.path.join(script_dir, "Charts")
        os.makedirs(charts_dir, exist_ok = True)

        # Save Cleaned Library CSV
        self.library_df.to_csv(os.path.join(script_dir, "goodreads.csv"), index = False)

        # Save Reviews CSV (Index Column Kept — React Table Parser Expects It)
        review_df = self.read_df[self.read_df["My Review"].str.strip() != ""][
            ["Book Id", "Title", "Authors", "Date Read", "Number of Pages", "My Rating", "My Review"]
        ].sort_values(by = "Date Read", ascending = False).reset_index(drop = True)
        review_df.to_csv(os.path.join(script_dir, "goodreads_reviews.csv"))

        # Generate and Save Responsive Layouts
        layout_labels = {
            "standard": "Standard",
            "tablet": "Tablet",
            "landscape": "Landscape",
            "portrait": "Portrait",
        }

        for layout, label in layout_labels.items():
            dashboard = self.generateDashboard(layout)
            spec_dict = dashboard.to_dict()
            spec_dict["background"] = None # Transparent
            spec_dict["$schema"] = "https://vega.github.io/schema/vega-lite/v5.20.1.json" # Match Vega-Lite Version Used by Altair

            out_path = os.path.join(charts_dir, f"{self.username}_{label}.json")
            with open(out_path, "w", encoding = "utf-8") as f:
                json.dump(spec_dict, f, indent = 2, ensure_ascii = False)
            print(f"Saved {out_path}")

        # Remove __pycache__
        pycache_path = os.path.join(script_dir, "__pycache__")
        if os.path.isdir(pycache_path):
            shutil.rmtree(pycache_path)


if __name__ == "__main__":
    _script_dir = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(_script_dir, ".env"))

    OFFLINE = "--offline" in sys.argv
    USER_ID = os.getenv("GOODREADS_USER_ID")

    try:
        if OFFLINE:
            # Regenerate Charts from Existing goodreads.csv (No Network Needed)
            library_df = pd.read_csv(os.path.join(_script_dir, "goodreads.csv"), dtype = str).fillna("")
            library_df["My Rating"] = pd.to_numeric(library_df["My Rating"], errors = "coerce").fillna(0).astype(int)
            library_df["Average Rating"] = pd.to_numeric(library_df["Average Rating"], errors = "coerce").fillna(0.0)
            library_df["Number of Pages"] = pd.to_numeric(library_df["Number of Pages"], errors = "coerce").fillna(0).astype(int)
        else:
            if not USER_ID:
                raise ValueError(
                    "Missing GOODREADS_USER_ID. Create .env File With:\n"
                    "  GOODREADS_USER_ID = your_numeric_user_id\n"
                    "Find It in Your Profile URL: goodreads.com/user/show/<USER_ID>-name\n"
                    "(Profile Must Be Public — Or Run with --offline to Reuse goodreads.csv)"
                )
            client = GoodReadsClient(USER_ID)
            library_df = client.getLibrary()

        GoodReadsDashboard(library_df).save()
        print("GoodReads Dashboard Generated Successfully!")

    except Exception as e:
        print(f"Error During Execution: {e}")
        raise
