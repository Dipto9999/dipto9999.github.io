from IPython.display import display

import altair as alt
import pandas as pd
import vl_convert as vlc

import json
import requests
import os

# Fetch List of All Steam Apps
def fetch_apps_df():
    app_json=requests.get('https://api.steampowered.com/ISteamApps/GetAppList/v2/').json()

    global APPS_DF
    APPS_DF=pd.DataFrame(app_json['applist']['apps'])

def yield_df(json_data):
    return pd.DataFrame(json_data).merge(APPS_DF, left_on='appid', right_on='appid')

# Fetch Owned Games
def fetch_owned_df(api_key, steam_id):
    request_url=f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={steam_id}&format=json'
    response_json=requests.get(request_url).json()

    # print(json.dumps(response_json, indent=4))

    owned_df=pd.DataFrame()
    if 'games' in response_json['response']:
        owned_df=yield_df(response_json['response']['games'])
    return owned_df

# Fetch Recently Played Games
def fetch_recently_played_df(api_key, steam_id):
    request_url=f'http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={api_key}&steamid={steam_id}&format=json'
    response_json=requests.get(request_url).json()

    # print(json.dumps(response_json, indent=4))

    recent_df=pd.DataFrame()
    if 'games' in response_json['response']:
        recent_df=yield_df(response_json['response']['games'])
    return recent_df

# Fetch Badges
def fetch_badges_df(api_key, steam_id):
    request_url=f'http://api.steampowered.com/IPlayerService/GetBadges/v1/?key={api_key}&steamid={steam_id}&format=json'
    response_json=requests.get(request_url).json()

    # print(json.dumps(response_json, indent=4))

    badges_df=pd.DataFrame()
    if 'badges' in response_json['response']:
        badges_df=yield_df(response_json['response']['badges'])
    return badges_df


# Fetch Player Level
def fetch_player_level(api_key, steam_id):
    request_url=f'http://api.steampowered.com/IPlayerService/GetSteamLevel/v1/?key={api_key}&steamid={steam_id}&format=json'
    response_json=requests.get(request_url).json()

    # print(json.dumps(response_json, indent=4))

    return response_json['response']['player_level']

# Summarize Skyrim and Skyrim Special Edition
def summarize_skyrim(stats_df):
    SKYRIM_ID=72850
    SKYRIM_SE_ID=489830

    # Data for Skyrim and Skyrim Special Edition
    skyrim_data=stats_df.query(f'appid == {SKYRIM_ID}')
    skyrim_se_data=stats_df.query(f'appid == {SKYRIM_SE_ID}')

    skyrim_idx=stats_df.query(f'appid == {SKYRIM_ID}').index[0]
    skyrim_se_idx=stats_df.query(f'appid == {SKYRIM_SE_ID}').index[0]

    # print('Skyrim Data [ORIGINAL]:')
    # display(skyrim_data)
    # print('Skyrim Special Edition Data [ORIGINAL]:')
    # display(skyrim_se_data)

    # Replace Null Skyrim Data with Values from Skyrim Special Edition
    for col in skyrim_data.columns :
        if (pd.isna(skyrim_data.at[skyrim_idx, col]) or (skyrim_data.at[skyrim_idx, col] != skyrim_data.at[skyrim_idx, col])) :
            skyrim_data[col].at[skyrim_idx, col]=skyrim_se_data.at[skyrim_se_idx, col]

    accumulated_data=['playtime_forever', 'completion_time', 'xp']
    max_data=['rtime_last_played', 'badgeid', 'communityitemid', 'level']
    average_data=['scarcity']

    for col in accumulated_data :
        if (pd.notna(skyrim_se_data.at[skyrim_se_idx, col]) and (skyrim_se_data.at[skyrim_se_idx, col] == skyrim_se_data.at[skyrim_se_idx, col])):
            skyrim_data.loc[:, col].values[0] += skyrim_se_data[col].values[0]
    for col in max_data :
        skyrim_data.loc[:, col].values[0]=skyrim_se_data[col].values[0]\
            if skyrim_se_data[col].values[0] > float(skyrim_data[col].values[0])\
            else skyrim_data[col].values[0]
    for col in average_data :
        if (pd.notna(skyrim_se_data.at[skyrim_se_idx, col]) and (skyrim_se_data.at[skyrim_se_idx, col] == skyrim_se_data.at[skyrim_se_idx, col])):
            skyrim_data.loc[:, col].values[0]=(skyrim_data[col].values[0] + skyrim_se_data[col].values[0]) / 2

    # print('Skyrim Data [UPDATE]:')
    # display(skyrim_data)

    # print('Previous Data:')
    # display(stats_df.head())

    stats_df=stats_df[stats_df.appid != SKYRIM_SE_ID]
    stats_df.loc[stats_df.appid == SKYRIM_ID]=skyrim_data

    # print('Updated Data:')
    # display(stats_df.head())

    return stats_df

# Generate Playtime Chart
def generate_playtime_chart(stats_df, top_n=15):
    effective_df=stats_df.sort_values(
        'playtime_forever', ascending=False
    )[['name', 'playtime_forever', 'appid']].iloc[:top_n].assign(
        playtime_percentage=lambda x: round((x['playtime_forever'] / x['playtime_forever'].sum()) * 100, 2 )
    )

    # display(effective_df.head())
    # display(effective_df.tail())

    pie_chart_colors=[
        "#808080",  # Grey
        "#32CD32",  # Lime Green
        "#00CED1",  # Dark Turquoise
        "#ADD8E6",  # Light Blue
        "#0000FF",  # Blue
        "#00008B",  # Dark Blue
        "#800080",  # Purple
        "#FFA500",  # Orange
        "#FF4500",  # Orange Red
        "#8B4513",  # Saddle Brown
        "#006400",  # Dark Green
        "#8B0000",  # Dark Red
        "#FFD700",  # Gold
        "#4682B4",  # Steel Blue
        "#2E8B57"   # Sea Green
    ]

    playtime_chart=alt.Chart(effective_df).mark_arc(stroke='black', strokeWidth=1).encode(
        theta=alt.Theta(field="playtime_percentage", type="quantitative"),
        color=alt.Color(field="name", type="nominal", scale=alt.Scale(range=pie_chart_colors), title='Games'),
        tooltip=[
            alt.Tooltip('name:N', title='Game'),
            alt.Tooltip('playtime_forever:Q', title='Playtime (Hours)'),
            alt.Tooltip('playtime_percentage:Q', title='Playtime (%)')
        ]
    ).properties(
        width=400, height=400,
        title=alt.TitleParams(
            text=f'''{USERNAME}\'s Top {top_n} Steam Games\n''',
            subtitle=[f'''Total Playtime: {round(effective_df['playtime_forever'].sum(), 2)} Hours\n'''],
            anchor='middle', fontSize=20, subtitleFontSize=16
        )
    )

    with open(f'''{USERNAME}_Steam_Top_15_Games.jpg''', 'wb') as f:
        f.write(vlc.vegalite_to_png(playtime_chart.to_dict()))

    playtime_chart.save(f'''{USERNAME}_Steam_Top_15_Games.html''')

    return playtime_chart

# Generate Player Level Chart
def generate_player_level_chart(player_level):
    player_level_df=pd.DataFrame({
        'Metric': ['Player Level'],
        'Value': [player_level]
    })

    player_level_chart=alt.Chart(player_level_df).mark_text(
        align='center',
        baseline='middle',
        fontSize=80,
        fontWeight='bold',
        color='#141331'
    ).encode(
        x=alt.X('Metric:N', axis=None),
        y=alt.value(50),
        text='Value:Q'
    ).properties(
        width=300,
        height=150,
        title=alt.TitleParams(
            text='Player Level',
            anchor='middle',
            fontSize=20,
        )
    )

    with open(f'''{USERNAME}_Steam_Player_Level.jpg''', 'wb') as f:
        f.write(vlc.vegalite_to_png(player_level_chart.to_dict()))
    player_level_chart.save(f'''{USERNAME}_Steam_Player_Level.html''')

    return player_level_chart

# Generate Played Games Chart
def generate_played_games_chart(stats_df):
    played_df=pd.DataFrame({
        'Metric': ['Played Games'],
        'Value': [len(stats_df[stats_df['playtime_forever'] > 0])]
    })

    played_games_chart=alt.Chart(played_df).mark_text(
        align='center',
        baseline='middle',
        fontSize=80,
        fontWeight='bold',
        color='#141331'
    ).encode(
        x=alt.X('Metric:N', axis=None),
        y=alt.value(50),
        text='Value:Q'
    ).properties(
        width=300,
        height=150,
        title=alt.TitleParams(
            text='Played Games',
            anchor='middle',
            fontSize=20,
        )
    )

    with open(f'''{USERNAME}_Steam_Played_Games.jpg''', 'wb') as f:
        f.write(vlc.vegalite_to_png(played_games_chart.to_dict()))
    played_games_chart.save(f'''{USERNAME}_Steam_Played_Games.html''')

    return played_games_chart

# Generate Steam Dashboard
def generate_steam_dashboard(stats_df):
    playtime_chart=generate_playtime_chart(stats_df)
    stats_chart=(
        generate_player_level_chart(stats_df['player_level'].unique()[0]) & generate_played_games_chart(stats_df)
    ).properties(
        title=alt.TitleParams(
            text=f'''Player Stats\n''',
            anchor='middle',
            fontSize=50
        )
    )

    dashboard=(stats_chart | playtime_chart).properties(
        title=alt.TitleParams(
            text=f"{USERNAME}\'s Steam Dashboard",
            anchor='middle',
            fontSize=60
        )
    ).configure_view(strokeWidth=1.5, strokeOpacity=0).configure_axis(
        labelFontSize=12, titleFontSize=16
    ).configure_legend(
        labelFontSize=12,
        titleFontSize=16
    )

    with open(f'''{USERNAME}_Steam_Dashboard.jpg''', 'wb') as f:
        f.write(vlc.vegalite_to_png(dashboard.to_dict()))
    dashboard.save(f'''{USERNAME}_Steam_Dashboard.html''')

if __name__ == '__main__':
    USERNAME='Dipto9999'
    API_KEY='Nice Try!'

    fetch_apps_df()

    # print("Table of All Steam App Names :")
    # display(APPS_DF.head())

    stats_df=pd.DataFrame()
    try :
        request_url=f'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={API_KEY}&vanityurl={USERNAME}'
        STEAM_ID=requests.get(request_url).json()['response']['steamid']

        owned_df=fetch_owned_df(API_KEY, STEAM_ID)

        print("Owned Games:")
        display(owned_df)

        recent_df=fetch_recently_played_df(API_KEY, STEAM_ID)

        print("Recently Played Games:")
        display(recent_df)

        badges_df=fetch_badges_df(API_KEY, STEAM_ID)

        print("Badges:")
        display(badges_df)

        player_level=fetch_player_level(API_KEY, STEAM_ID)

        print("Player Level:")
        display(player_level)

        if recent_df.empty:
            print("No Recently Played Games")

            stats_df=pd.merge(
                owned_df, badges_df, on='appid', how='outer', suffixes=('', '_BADGES')
            ).assign(player_level=player_level)
            effective_cols=[
                col for col in stats_df.columns\
                    if (not col.endswith('_BADGES'))\
                    and (col.find('playtime') <= (int(col.startswith('playtime_forever')) - 1))
            ]
            stats_df=stats_df[effective_cols]

            stats_df=summarize_skyrim(stats_df).fillna(0).sort_values(
                ['playtime_forever', 'level'], ascending=False
            ).assign(
                playtime_forever=lambda x: round(x['playtime_forever'] / 60, 2)
            )

            display(stats_df.head())

            stats_df.to_csv('steam_data.csv', index=False)

        print("Data Exported Successfully!")
    except (KeyError, NameError, requests.exceptions.RequestException):
        if os.path.exists('steam_data.csv'):
            stats_df=pd.read_csv('steam_data.csv')
    finally :
        generate_steam_dashboard(stats_df)
        print("Execution Completed!")