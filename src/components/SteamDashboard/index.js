import { useMemo, useEffect, useState } from 'react';
import { VegaLite } from 'react-vega';

import defaultSteam from "../../assets/data/steam/Charts/Dipto9999_Standard.json";
import portraitSteam from "../../assets/data/steam/Charts/Dipto9999_Portrait.json";
import landscapeSteam from "../../assets/data/steam/Charts/Dipto9999_Landscape.json";
import tabletSteam from "../../assets/data/steam/Charts/Dipto9999_Tablet.json";

import './index.scss';

const chartContainerStyle = {
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  width: '100%',
};

const getSteamSpec = (width, height) => {
  if (width <= 550 && height >= width) return portraitSteam; // Mobile Portrait
  if (width <= 900 && width > height) return landscapeSteam;  // Mobile Landscape
  if (width <= 1200) return tabletSteam; // Tablet Portrait
  return defaultSteam; // Default Desktop Steam
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

  // Pick Steam Dynamically Based on Dimensions
  const spec = useMemo(() => {
    return JSON.parse(JSON.stringify(
      getSteamSpec(dimensions.width, dimensions.height)
    ));
  }, [dimensions]);

  return (
    <div className="vega-chart" style={chartContainerStyle}>
      <VegaLite spec={spec} actions={false} />
    </div>
  );
};

export default SteamDashboard;
