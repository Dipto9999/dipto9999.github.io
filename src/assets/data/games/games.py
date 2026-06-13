"""
Games Dashboard Generator
Author: Muntakim Rahman
Description: Combines PlayStation Network and Steam gaming data for the same player,
    merging playtime for cross-platform games and generating unified Altair visualizations.
    Loads from CSV backups (steam/, psn/) or fetches live from both APIs.
    Dashboard exported as JSON (Standard, Tablet, Landscape, Portrait), HTML, PNG, SVG.
"""

# Import Packages
import pandas as pd
import altair as alt

import json
import os
import sys
from dotenv import load_dotenv

from typing import Optional

# Resolve Sub-Module Paths
current_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, os.path.join(current_dir, 'steam'))
sys.path.insert(0, os.path.join(current_dir, 'psn'))

from steam import SteamUser, SteamAPI
from psn import PSN_User, PSN_API

PWD = os.path.dirname(os.path.abspath(__file__))

class Games_User:
    """Combines PSN and Steam Gaming Data for the Same Player"""

    # Games with Different Store Names on Each Platform after Custom Name Mapping.
    # Key = Steam Custom Name, Value = PSN Custom Name (Label Kept in Combined Data).
    CROSS_PLATFORM_NAMES = {
        'SoS: A Wonderful Life': 'Harvest Moon: AWL',
    }

    def __init__(self, steam_user: SteamUser, psn_user: PSN_User):
        self.steam_user  = steam_user
        self.psn_user    = psn_user

        # Combined Data
        self.combined_df = pd.DataFrame()

        self._merge()

    def _merge(self) -> None:
        """Merge Steam and PSN Game Data, Summing Playtime for Cross-Platform Titles"""
        steam_df = self.steam_user.stats_df[['name', 'playtime_forever']].copy()
        psn_df   = self.psn_user.stats_df[['name',  'playtime_forever']].copy()

        # Remap Steam-Side Aliases to PSN Label so Groupby Merges Them
        for steam_name, psn_name in self.CROSS_PLATFORM_NAMES.items():
            steam_df.loc[steam_df['name'] == steam_name, 'name'] = psn_name

        combined = pd.concat([steam_df, psn_df], ignore_index = True)

        self.combined_df = (
            combined
            .groupby('name', as_index = False)['playtime_forever']
            .sum()
            .sort_values('playtime_forever', ascending = False)
            .reset_index(drop = True)
        )

    def getTopData(self, n: int = 10) -> pd.DataFrame:
        """Get Top N Games by Combined Playtime"""
        return (
            self.combined_df
            .nlargest(n, 'playtime_forever')
            .sort_values('playtime_forever', ascending = False)
        )

    def getNumberPlayed(self) -> int:
        """Get Number of Unique Games Played Across Both Platforms"""
        return (self.combined_df['playtime_forever'] > 0).sum()

    def getTotalPlaytime(self) -> float:
        """Get Total Combined Playtime Across Both Platforms"""
        return self.combined_df['playtime_forever'].sum()

class Games_Dashboard:
    """Creates Unified Visualizations for Combined PSN + Steam Data"""

    # Responsive Layout Configurations — Scaled per Breakpoint
    BREAKPOINTS = {
        'Standard': { # Desktop (> 1200px)
            'view':            {'continuousWidth': 300,  'continuousHeight': 300},
            'axis':            {'labelFontSize': 12,     'titleFontSize': 16},
            'legend':          {'columns': 5,  'columnPadding': 75, 'padding': 75, 'labelFontSize': 10, 'titleFontSize': 16},
            'level':           {'width': 150,  'height': 150, 'fontSize': 60, 'y': 50,  'titleFontSize': 18},
            'played':          {'width': 300,  'height': 150, 'fontSize': 80, 'y': 50,  'titleFontSize': 20},
            'trophy_bar':      {'width': 250,  'height': 150, 'labelFontSize': 13, 'titleFontSize': 20, 'subtitleFontSize': 14},
            'pie':             {'width': 700,  'height': 400, 'titleFontSize': 26, 'subtitleFontSize': 16},
            'stats_title':     30,
            'dashboard_title': 40,
            'padding':         {'left': 250, 'right': 250, 'top': 0,  'bottom': 0},
        },
        'Tablet': { # Tablet (900px - 1200px)
            'view':            {'continuousWidth': 200,  'continuousHeight': 200},
            'axis':            {'labelFontSize': 14,     'titleFontSize': 18},
            'legend':          {'columns': 3,  'columnPadding': 18, 'padding': 35, 'labelFontSize': 9,  'titleFontSize': 13},
            'level':           {'width': 100,  'height': 120, 'fontSize': 50, 'y': 40,  'titleFontSize': 16},
            'played':          {'width': 200,  'height': 120, 'fontSize': 70, 'y': 40,  'titleFontSize': 18},
            'trophy_bar':      {'width': 200,  'height': 120, 'labelFontSize': 11, 'titleFontSize': 18, 'subtitleFontSize': 12},
            'pie':             {'width': 400,  'height': 320, 'titleFontSize': 22, 'subtitleFontSize': 15},
            'stats_title':     22,
            'dashboard_title': 28,
            'padding':         {'left': 40,  'right': 40,  'top': 10, 'bottom': 10},
        },
        'Landscape': { # Mobile Landscape (< 900px, width > height)
            'view':            {'continuousWidth': 130,  'continuousHeight': 130},
            'axis':            {'labelFontSize': 10,     'titleFontSize': 11},
            'legend':          None,
            'level':           {'width': 65,   'height': 60,  'fontSize': 16, 'y': 35,  'titleFontSize': 12},
            'played':          {'width': 130,  'height': 60,  'fontSize': 20, 'y': 45,  'titleFontSize': 16},
            'trophy_bar':      {'width': 110,  'height': 60,  'labelFontSize': 7,  'titleFontSize': 12, 'subtitleFontSize': 9},
            'pie':             {'width': 130,  'height': 130, 'titleFontSize': 18, 'subtitleFontSize': 13},
            'stats_title':     18,
            'dashboard_title': 18,
            'padding':         {'left': 10,  'right': 10,  'top': 0,  'bottom': 0},
        },
        'Portrait': { # Mobile Portrait (< 550px, height > width)
            'view':            {'continuousWidth': 90,   'continuousHeight': 90},
            'axis':            {'labelFontSize': 7,      'titleFontSize': 8},
            'legend':          None,
            'level':           {'width': 50,   'height': 40,  'fontSize': 11, 'y': 25,  'titleFontSize': 9},
            'played':          {'width': 100,  'height': 40,  'fontSize': 13, 'y': 30,  'titleFontSize': 10},
            'trophy_bar':      {'width': 85,   'height': 45,  'labelFontSize': 5,  'titleFontSize': 8,  'subtitleFontSize': 7},
            'pie':             {'width': 90,   'height': 90,  'titleFontSize': 12, 'subtitleFontSize': 10},
            'stats_title':     12,
            'dashboard_title': 14,
            'padding':         {'left': 10,  'right': 10,  'top': 0,  'bottom': 0},
        },
    }

    def __init__(self, user: Games_User):
        self.user = user
        self.colors = [
            "#00008B", "#FF4500", "#32CD32", "#C2185B",
            "#00CED1", "#FFD700", "#7B1FA2", "#2E8B57",
            "#FF8C00", "#4682B4", "#808080", "#8B0000",
            "#20B2AA", "#E91E63", "#006400"
        ]

        self.dashboard = None
        self.generateDashboard()

    def _buildDashboard(self, cfg: dict) -> alt.Chart:
        """Build Complete Dashboard for a Given Breakpoint Config"""
        lc  = cfg['level']      # Level Box Config
        pc  = cfg['played']     # Played Box Config
        tc  = cfg['trophy_bar'] # Trophy Bar Config
        ic  = cfg['pie']        # Pie Chart Config
        lgd = cfg['legend']     # Legend Config (None for Small Breakpoints)

        # Pie Chart
        top_df = self.user.getTopData(10).copy()
        total  = top_df['playtime_forever'].sum()
        top_df['playtime_percentage'] = (top_df['playtime_forever'] / total * 100).round(2)

        playtime_chart = alt.Chart(top_df).mark_arc(
            stroke = 'black', strokeWidth = 1
        ).encode(
            theta = alt.Theta('playtime_percentage:Q'),
            color = alt.Color(
                'name:N',
                scale  = alt.Scale(range = self.colors),
                legend = alt.Legend(
                    orient        = 'bottom', direction = 'horizontal',
                    columns       = lgd['columns'],
                    padding       = lgd['padding'], rowPadding = 10,
                    columnPadding = lgd['columnPadding'],
                    title         = '', titleAlign = 'center',
                    labelFontSize = lgd['labelFontSize'],
                    titleFontSize = lgd['titleFontSize'],
                ) if lgd else None,
                sort = None
            ),
            tooltip = [
                alt.Tooltip('name:N',                title = 'Game'),
                alt.Tooltip('playtime_forever:Q',    title = 'Time (Hrs)',   format = '.1f'),
                alt.Tooltip('playtime_percentage:Q', title = 'Playtime (%)', format = '.2f'),
            ]
        ).properties(
            width  = ic['width'], height = ic['height'],
            title  = alt.TitleParams(
                text             = 'Top Games',
                subtitle         = f'Total Playtime: {self.user.getTotalPlaytime():.1f} Hrs',
                anchor           = 'middle',
                fontSize         = ic['titleFontSize'],
                subtitleFontSize = ic['subtitleFontSize']
            )
        )

        # Steam Level Display
        steam_data  = pd.DataFrame({'Metric': ['Steam Level'], 'Value': [self.user.steam_user.player_level]})
        steam_level = alt.Chart(steam_data).mark_text(
            align = 'center', baseline = 'middle',
            fontSize = lc['fontSize'], fontWeight = 'bold', color = '#141331'
        ).encode(
            x    = alt.X('Metric:N', axis = None),
            y    = alt.value(lc['y']),
            text = 'Value:Q'
        ).properties(
            width  = lc['width'], height = lc['height'],
            title  = alt.TitleParams(text = 'Steam Level', anchor = 'middle', fontSize = lc['titleFontSize'])
        )

        # PSN Level Display
        psn_data  = pd.DataFrame({'Metric': ['PSN Level'], 'Value': [self.user.psn_user.trophy_level]})
        psn_level = alt.Chart(psn_data).mark_text(
            align = 'center', baseline = 'middle',
            fontSize = lc['fontSize'], fontWeight = 'bold', color = '#141331'
        ).encode(
            x    = alt.X('Metric:N', axis = None),
            y    = alt.value(lc['y']),
            text = 'Value:Q'
        ).properties(
            width  = lc['width'], height = lc['height'],
            title  = alt.TitleParams(text = 'PSN Level', anchor = 'middle', fontSize = lc['titleFontSize'])
        )

        # Played Display
        played_data = pd.DataFrame({'Metric': ['Played'], 'Value': [self.user.getNumberPlayed()]})
        played      = alt.Chart(played_data).mark_text(
            align = 'center', baseline = 'middle',
            fontSize = pc['fontSize'], fontWeight = 'bold', color = '#141331'
        ).encode(
            x    = alt.X('Metric:N', axis = None),
            y    = alt.value(pc['y']),
            text = 'Value:Q'
        ).properties(
            width  = pc['width'], height = pc['height'],
            title  = alt.TitleParams(text = 'Played', anchor = 'middle', fontSize = pc['titleFontSize'])
        )

        # PSN Trophies Bar Chart
        trophy_df = pd.DataFrame([
            {'type': 'Platinum', 'count': self.user.psn_user.trophy_counts.get('platinum', 0)},
            {'type': 'Gold',     'count': self.user.psn_user.trophy_counts.get('gold',     0)},
            {'type': 'Silver',   'count': self.user.psn_user.trophy_counts.get('silver',   0)},
            {'type': 'Bronze',   'count': self.user.psn_user.trophy_counts.get('bronze',   0)},
        ])

        # Remove Trophy Types with Zero Count
        trophy_df      = trophy_df[trophy_df['count'] > 0]
        total_trophies = trophy_df['count'].sum()

        psn_trophies = alt.Chart(trophy_df).mark_bar(
            stroke = 'black', strokeWidth = 1
        ).encode(
            x = alt.X('count:Q', axis = alt.Axis(title = '', tickMinStep = 1)),
            y = alt.Y(
                'type:N',
                sort = ['Platinum', 'Gold', 'Silver', 'Bronze'],
                axis = alt.Axis(title = '', labelFontSize = tc['labelFontSize'])
            ),
            color = alt.Color(
                'type:N',
                scale = alt.Scale(
                    domain = ['Platinum', 'Gold', 'Silver', 'Bronze'],
                    range  = ['#B9F2FF', '#FFD700', '#C0C0C0', '#CD7F32']
                ),
                legend = None
            ),
            tooltip = [
                alt.Tooltip('type:N',  title = 'Trophy'),
                alt.Tooltip('count:Q', title = 'Count'),
            ]
        ).properties(
            width  = tc['width'], height = tc['height'],
            title  = alt.TitleParams(
                text             = 'PSN Trophies',
                subtitle         = f'Total: {total_trophies:,}',
                anchor           = 'middle',
                fontSize         = tc['titleFontSize'],
                subtitleFontSize = tc['subtitleFontSize']
            )
        )

        # Assemble Dashboard
        level_row   = steam_level | psn_level # Steam Level | PSN Level (Side by Side)
        stats_chart = (
            level_row & played & psn_trophies
        ).properties(
            title = alt.TitleParams(text = 'Player Stats', anchor = 'middle', fontSize = cfg['stats_title'])
        )

        return (stats_chart | playtime_chart).resolve_scale(color = 'independent').properties(
            padding = cfg['padding'],
            title   = alt.TitleParams(
                text   = f"{self.user.steam_user.username}'s Games Dashboard",
                anchor = 'middle', fontSize = cfg['dashboard_title']
            ),
        ).configure_view(
            continuousWidth  = cfg['view']['continuousWidth'],
            continuousHeight = cfg['view']['continuousHeight'],
            strokeWidth      = 1.5,
            strokeOpacity    = 0,
        ).configure_axis(
            labelFontSize = cfg['axis']['labelFontSize'],
            titleFontSize = cfg['axis']['titleFontSize']
        ).configure_legend(
            labelFontSize = lgd['labelFontSize'] if lgd else 12,
            titleFontSize = lgd['titleFontSize'] if lgd else 16
        )

    def generateDashboard(self) -> None:
        """Generate Default (Standard) Dashboard"""
        self.dashboard = self._buildDashboard(self.BREAKPOINTS['Standard'])

    def updateTemplate(self, template_json: dict, fresh_json: dict, output_path: str) -> None:
        """Update Existing JSON Template with Fresh Data while Preserving Structure"""
        def _get_keys(current_json: dict) -> dict:
            keys = {
                'SteamLevel': None,
                'PSNLevel':   None,
                'Played':     None,
                'Trophies':   None,
                'Games':      None,
            }
            for key, data in current_json.get('datasets', {}).items():
                if not (isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict)):
                    continue
                metric = data[0].get('Metric')
                if metric == 'Steam Level':
                    keys['SteamLevel'] = key
                elif metric == 'PSN Level':
                    keys['PSNLevel'] = key
                elif metric == 'Played':
                    keys['Played'] = key
                elif data[0].get('type') in {'Platinum', 'Gold', 'Silver', 'Bronze'}:
                    keys['Trophies'] = key
                elif ('name' in data[0]) and ('playtime_forever' in data[0]):
                    keys['Games'] = key
            return keys

        try:
            fresh_datasets  = fresh_json.get('datasets', {})
            template_keys   = _get_keys(template_json)
            fresh_keys      = _get_keys(fresh_json)

            for key in template_keys:
                t_key = template_keys[key]
                f_key = fresh_keys[key]
                if t_key and f_key:
                    template_json['datasets'][t_key] = fresh_datasets[f_key]
                elif t_key:
                    print(f"Warning: No Fresh Data for '{key}' - Skipping Update for this Dataset")

            with open(output_path, 'w') as f:
                json.dump(template_json, f, indent = 2)

            print(f"Template Updated Successfully: {output_path}")
        except Exception as e:
            print(f"Error Updating Template: {e}")

    def save(self, filename: Optional[str] = None) -> None:
        """Save Dashboard as JSON (All Breakpoints), HTML, PNG, SVG"""
        if self.dashboard is None:
            print("Dashboard Not Generated")
            return

        if filename is None:
            filename = f"{self.user.psn_user.username}_Games_Dashboard"

        if not os.path.exists(os.path.join(PWD, 'Charts')):
            os.makedirs(os.path.join(PWD, 'Charts'))

        # Save Main Dashboard JSON (Standard Layout)
        with open(os.path.join(PWD, f"Charts/{filename}.json"), 'w') as f:
            json.dump(self.dashboard.to_dict(), f, indent = 2)

        # Load Dashboard from JSON File
        with open(os.path.join(PWD, f"Charts/{filename}.json"), 'r') as f:
            spec = json.load(f)

        self.dashboard = alt.Chart.from_dict(spec)

        # Save as HTML (Interactive)
        with open(os.path.join(PWD, f"Charts/{filename}.html"), 'w') as f:
            f.write(self.dashboard.to_html())

        self.dashboard.save(os.path.join(PWD, f"Charts/{filename}.png")) # Save as PNG (Static)
        self.dashboard.save(os.path.join(PWD, f"Charts/{filename}.svg")) # Save as SVG (Vector)

        # Save Responsive JSON Variants for Each Breakpoint
        for name, cfg in self.BREAKPOINTS.items():
            chart = self._buildDashboard(cfg)
            path  = os.path.join(PWD, f"Charts/{filename}_{name}.json")

            if os.path.exists(path):
                # Template exists — update datasets only, preserve background/structure
                with open(path, 'r') as f:
                    template_json = json.load(f)
                self.updateTemplate(template_json, chart.to_dict(), path)
            else:
                # First run — write fresh JSON
                with open(path, 'w') as f:
                    json.dump(chart.to_dict(), f, indent = 2)
                print(f"Saved: {filename}_{name}.json")

if __name__ == '__main__':
    load_dotenv(os.path.join(current_dir, 'steam', '.env'))
    load_dotenv(os.path.join(current_dir, 'psn',   '.env'))

    STEAM_USERNAME = 'Dipto9999'
    PSN_USERNAME = 'Dipto_9999'
    USE_PSN_CLIENT = True # True = Authenticated Account, False = Lookup by Online ID

    STEAM_API_KEY = os.getenv("STEAM_API_KEY")
    NPSSO_CODE = os.getenv("NPSSO_CODE")

    try:
        games_user = Games_User(
            steam_user = SteamUser(STEAM_USERNAME, SteamAPI(STEAM_API_KEY)),
            psn_user = PSN_User(PSN_USERNAME, PSN_API(NPSSO_CODE), use_client = USE_PSN_CLIENT)
        )
        Games_Dashboard(games_user).save()
        print("Execution Completed Successfully!")

    except Exception as e:
        print(f"Error During Execution: {e}")
