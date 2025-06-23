import React, { useMemo, useEffect, useState } from 'react';
import { VegaLite } from 'react-vega';

import defaultGoodReads from "../../assets/data/goodreads/Charts/Muntakim_Dashboard.json";
import portraitGoodReads from "../../assets/data/goodreads/Charts/Muntakim_Portrait.json";
import landscapeGoodReads from "../../assets/data/goodreads/Charts/Muntakim_Landscape.json";
import tabletGoodReads from "../../assets/data/goodreads/Charts/Muntakim_Tablet.json";

import './index.scss';

const chartContainerStyle = {
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  width: '100%',
};

const getGoodReadsSpec = (width, height) => {
  if (width <= 550 && height >= width) return portraitGoodReads; // Mobile Portrait
  if (width <= 900 && width > height) return landscapeGoodReads;  // Mobile Landscape
  if (width <= 1200) return tabletGoodReads; // Tablet Portrait
  return defaultGoodReads; // Default Desktop Spec
};

const GoodReadsDashboard = () => {
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

  // Pick Spec Dynamically Based on Dimensions
  const spec = useMemo(() => {
    return JSON.parse(JSON.stringify(
      getGoodReadsSpec(dimensions.width, dimensions.height)
    ));
  }, [dimensions]);

  return (
    <div className="vega-chart" style={chartContainerStyle}>
      <VegaLite spec={spec} actions={false} />
    </div>
  );
};

export default GoodReadsDashboard;
