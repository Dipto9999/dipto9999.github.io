import React, { useMemo, useEffect, useState } from 'react';
import { VegaLite } from 'react-vega';

import defaultSpec from "../../assets/data/steam/Charts/Dipto9999_Dashboard.json";
import portraitSpec from "../../assets/data/steam/Charts/Dipto9999_Portrait.json";
import landscapeSpec from "../../assets/data/steam/Charts/Dipto9999_Landscape.json";

import './index.scss';

const chartContainerStyle = {
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  width: '100%',
};

const getDashboardSpec = (width, height) => {
  if (width <= 430 && height >= width) return portraitSpec; // Mobile Portrait
  if (width <= 900 && width > height) return landscapeSpec; // Mobile Landscape
  return defaultSpec; // Default
};

const SteamDashboard = () => {
  // Track Window Dimensions to Update on Resize/Rotation
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
    // Clean Up Event on Unmount
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Pick Spec Dynamically Based on Dimensions
  const spec = useMemo(() => {
    return JSON.parse(JSON.stringify(
      getDashboardSpec(dimensions.width, dimensions.height)
    ));
  }, [dimensions]);

  return (
    <div className = "vega-chart" style = {chartContainerStyle}>
      <VegaLite spec = {spec} actions = {false} />
    </div>
  );
};

export default SteamDashboard;
