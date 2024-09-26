import { VegaLite } from 'react-vega';
import './index.scss'; // Importing the SCSS file for styling

const SteamDashboard = () => {
    var screenWidth = window.innerWidth;
    var screenHeight = window.innerHeight;
    // console.log(`Screen Width: ${screenWidth}, Screen Height: ${screenHeight}`)

    var supertitleFontSize;
    var titleFontSize;
    var subtitleFontSize;

    var bigNumberFontSize;
    var chartLength;

    var legendConfig;

    if (screenHeight <= 400 || screenWidth <= 400) {
        supertitleFontSize = 20;
        titleFontSize = 15;
        subtitleFontSize = 10;

        bigNumberFontSize = 40;
        chartLength = 150;

    } else {
        supertitleFontSize = 50;
        titleFontSize = 30;
        subtitleFontSize = 20;

        bigNumberFontSize = 80;
        if (screenHeight <= 800 || screenWidth <= 800) {
            chartLength = 300;
        } else {
            chartLength = 350;
        }
    }

    if (screenWidth <= 400) {
        legendConfig = null;
    } else {
        legendConfig = {
            labelFontSize: 10,
            titleFontSize: 12,
        };
    }

  const dashboardSpec = {
    config: {
      view: {
        continuousWidth: chartLength,
        continuousHeight: chartLength,
        strokeOpacity: 0,
      }
    },
    background: null,
    hconcat: [
      {
        vconcat: [
          {
            data: {
              name: 'data-a9dbdc8b82fd0fde59eff4040164a1aa',
            },
            mark: {
              type: 'text',
              align: 'center',
              baseline: 'middle',
              color: '#00008B',
              fontSize: bigNumberFontSize,
              fontWeight: 'bold',
            },
            encoding: {
              text: {
                field: 'Value',
                type: 'quantitative',
              },
              x: {
                axis: null,
                field: 'Metric',
                type: 'nominal',
              },
              y: {
                value: 30,
              },
            },
            height: 75,
            title: {
              text: 'Player Level',
              anchor: 'middle',
              fontSize: titleFontSize,
            },
            // width: 300,
          },
          {
            data: {
              name: 'data-26154e4df75ff9a35b42d85a483593b2',
            },
            mark: {
              type: 'text',
              align: 'center',
              baseline: 'middle',
              color: '#00008B',
              fontSize: bigNumberFontSize,
              fontWeight: 'bold',
            },
            encoding: {
              text: {
                field: 'Value',
                type: 'quantitative',
              },
              x: {
                axis: null,
                field: 'Metric',
                type: 'nominal',
              },
              y: {
                value: 0,
              },
            },
            // height: 150,
            title: {
              text: 'Played Games',
              anchor: 'middle',
            },
            // width: 300,
          },
        ],
      },
      {
        data: {
          name: 'data-6e31785fc98ccdd309cde1228cc1136e',
        },
        mark: {
          type: 'arc',
          stroke: 'black',
          strokeWidth: 1,
        },
        encoding: {
          color: {
            field: 'name',
            scale: {
              range: [
                '#808080', '#32CD32', '#00CED1', '#ADD8E6', '#0000FF',
                '#006400', '#800080', '#FFA500', '#FF4500', '#8B4513',
                '#00008B', '#8B0000', '#FFD700', '#4682B4', '#2E8B57',
              ],
            },
            title: 'Games',
            type: 'nominal',
            legend: legendConfig
          },
          theta: {
            field: 'playtime_percentage',
            type: 'quantitative',
          },
          tooltip: [
            {
              field: 'name',
              title: 'Game',
              type: 'nominal',
            },
            {
              field: 'playtime_forever',
              title: 'Playtime (Hours)',
              type: 'quantitative',
            },
            {
              field: 'playtime_percentage',
              title: 'Playtime (%)',
              type: 'quantitative',
            },
          ],
        },
        // height: 400,
        title: {
          text: "Dipto9999's Top 15 Steam Games",
          anchor: 'middle',
          fontSize: titleFontSize,
          subtitle: ['Total Playtime: 1450.21 Hours'],
          subtitleFontSize: subtitleFontSize,
        },
        // width: 400,
      },
    ],
    title: {
      text: "Dipto9999's Steam Dashboard",
      anchor: 'middle',
      fontSize: supertitleFontSize,
    },
    $schema: 'https://vega.github.io/schema/vega-lite/v5.17.0.json',
    datasets: {
      'data-a9dbdc8b82fd0fde59eff4040164a1aa': [
        {
          Metric: 'Player Level',
          Value: 18,
        },
      ],
      'data-26154e4df75ff9a35b42d85a483593b2': [
        {
          Metric: 'Played Games',
          Value: 37,
        },
      ],
      'data-6e31785fc98ccdd309cde1228cc1136e': [
        {
          name: 'The Elder Scrolls V: Skyrim',
          playtime_forever: 845.28,
          appid: 72850.0,
          playtime_percentage: 58.29,
        },
        {
          name: 'Batman™: Arkham Knight',
          playtime_forever: 96.12,
          appid: 208650.0,
          playtime_percentage: 6.63,
        },
        {
          name: 'The Lord of the Rings Online™',
          playtime_forever: 84.38,
          appid: 212500.0,
          playtime_percentage: 5.82,
        },
        {
          name: 'Batman - The Telltale Series',
          playtime_forever: 66.22,
          appid: 498240.0,
          playtime_percentage: 4.57,
        },
        {
          name: 'Paladins',
          playtime_forever: 54.27,
          appid: 444090.0,
          playtime_percentage: 3.74,
        },
        {
          name: 'Stardew Valley',
          playtime_forever: 49.5,
          appid: 413150.0,
          playtime_percentage: 3.41,
        },
        {
          name: 'Game of Thrones - A Telltale Games Series',
          playtime_forever: 47.68,
          appid: 330840.0,
          playtime_percentage: 3.29,
        },
        {
          name: 'The Walking Dead',
          playtime_forever: 40.52,
          appid: 207610.0,
          playtime_percentage: 2.79,
        },
        {
          name: 'Middle-earth™: Shadow of Mordor™',
          playtime_forever: 37.05,
          appid: 241930.0,
          playtime_percentage: 2.55,
        },
        {
          name: 'Batman: The Enemy Within - The Telltale Series',
          playtime_forever: 35.93,
          appid: 675260.0,
          playtime_percentage: 2.48,
        },
        {
          name: 'Batman: Arkham City GOTY',
          playtime_forever: 21.1,
          appid: 200260.0,
          playtime_percentage: 1.45,
        },
        {
          name: 'DOOM',
          playtime_forever: 20.92,
          appid: 379720.0,
          playtime_percentage: 1.44,
        },
        {
          name: 'Trine 2',
          playtime_forever: 19.88,
          appid: 35720.0,
          playtime_percentage: 1.37,
        },
        {
          name: 'Tomb Raider',
          playtime_forever: 17.98,
          appid: 203160.0,
          playtime_percentage: 1.24,
        },
        {
          name: 'Batman: Arkham Asylum GOTY Edition',
          playtime_forever: 13.38,
          appid: 35140.0,
          playtime_percentage: 0.92,
        },
      ],
    },
  };

  return (
    <div className="vega-chart">
      <VegaLite spec={dashboardSpec} actions={false} />
    </div>
  );
};

export default SteamDashboard;