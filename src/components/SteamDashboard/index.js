import { useMemo, useEffect, useState } from 'react';
import { VegaLite } from 'react-vega';

import defaultGames from "../../assets/data/games/Charts/Dipto_9999_Games_Dashboard_Standard.json";
import portraitGames from "../../assets/data/games/Charts/Dipto_9999_Games_Dashboard_Portrait.json";
import landscapeGames from "../../assets/data/games/Charts/Dipto_9999_Games_Dashboard_Landscape.json";
import tabletGames from "../../assets/data/games/Charts/Dipto_9999_Games_Dashboard_Tablet.json";

import './index.scss';

const chartContainerStyle = {
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  width: '100%',
};

const getGamesSpec = (width, height) => {
  if (width <= 550 && height >= width) return portraitGames; // Mobile Portrait
  if (width <= 900 && width > height) return landscapeGames;  // Mobile Landscape
  if (width <= 1200) return tabletGames; // Tablet Portrait
  return defaultGames; // Default Desktop
};

const SteamDashboard = () => {
  const [dimensions, setDimensions] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });

  useEffect(() => {
    const handleResize = () => {
      setDimensions({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Pick Games Chart Dynamically Based on Dimensions
  const spec = useMemo(() => {
    return JSON.parse(JSON.stringify(
      getGamesSpec(dimensions.width, dimensions.height)
    ));
  }, [dimensions]);

  return (
    <div className = "vega-chart" style = {chartContainerStyle}>
      <VegaLite spec = {spec} actions = {false} />
    </div>
  );
};

export default SteamDashboard;
