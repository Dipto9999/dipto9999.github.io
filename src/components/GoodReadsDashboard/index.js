import { useMemo, useEffect, useState } from 'react';
import { VegaLite } from 'react-vega';
import DataTable from 'react-data-table-component';
import Papa from 'papaparse';

// Import Data
import defaultGoodReads from "../../assets/data/goodreads/Charts/Muntakim_Standard.json";
import portraitGoodReads from "../../assets/data/goodreads/Charts/Muntakim_Portrait.json";
import landscapeGoodReads from "../../assets/data/goodreads/Charts/Muntakim_Landscape.json";
import tabletGoodReads from "../../assets/data/goodreads/Charts/Muntakim_Tablet.json";
import reviewsCSV from "../../assets/data/goodreads/goodreads_reviews.csv";

import './index.scss';

//  --- GoodReads Cards ---
const GoodReadsCards = ({ data }) => {
  return(
    <div className = "goodreads-cards">{
      data.filter(
        row =>
          row["Title"].trim() ||
          row["Authors"].trim() ||
          row["Date Read"]?.trim() ||
          row["My Review"]?.trim()
      ).map((row, idx) => (
        <div className = "goodreads-card" key = {idx}>
          <h3 className = "goodreads-card-title">{row.Title}</h3>
          <div className = "goodreads-card-author-date">
            <b className = "goodreads-card-author">by {row.Authors}</b>
            <div className = "goodreads-card-date">
              <b>Read:</b> {row["Date Read"]}
            </div>
          </div>
          <div>
            <hr className = "goodreads-card-divider"/>
            <span>{row["My Review"]}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

// --- GoodReads Table ---
const GoodReadsTable = ({ data }) => {
  const tableCols = [
    { name: 'Title', selector: row => row.Title, sortable: true, wrap: true, style: { minWidth: '170px', maxWidth: '240px' } },
    { name: 'Authors', selector: row => row['Authors'], wrap: true, style: { minWidth: '120px', maxWidth: '180px' } },
    { name: 'Finished', selector: row => row['Date Read'], sortable: true, style: { minWidth: '90px', maxWidth: '110px' } },
    { name: 'Review', selector: row => row['My Review'], wrap: true, style: { minWidth: '220px', maxWidth: '1fr' } }, // Take Up Remaining Space
  ];

  const tableStyles = {
    rows: { style: { minHeight: '40px', fontSize: '1.16rem' } },
    headCells: {
      style: {
        fontWeight: '800',
        fontSize: '1.42rem',
        background: '#f4f8fb',
        letterSpacing: '0.02em',
        textTransform: 'none',
      },
    },
    cells: {
      style: {textAlign: 'left'}
    },
    table: { style: { borderRadius: 8, boxShadow: "0 2px 8px #0001" } },
  };

  return (
    <DataTable
      className = "goodreads-table"
      columns = {tableCols}
      data = {data}
      pagination
      paginationPerPage = {3}
      highlightOnHover
      striped
      responsive
      customStyles = {tableStyles}
      dense
    />
  );
};

// --- GoodReads Charts ---
const GoodReadsCharts = () => {
  const chartsDivStyle = {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    width: '100%',
  };

  // State for Dimensions
  const [dimensions, setDimensions] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });

  // Get Appropriate Chart Spec Based on Dimensions
  const getChartsSpec = (width, height) => {
    if (width <= 550 && height >= width) return portraitGoodReads; // Mobile Portrait
    if (width <= 900 && width > height) return landscapeGoodReads;  // Mobile Landscape
    if (width <= 1200) return tabletGoodReads; // Tablet Portrait
    return defaultGoodReads; // Default Desktop Spec
  };

  // Update Dimensions with Resize Listener
  useEffect(() => {
    const handleResize = () => {
      setDimensions({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };
    window.addEventListener('resize', handleResize); // Update on Resize
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Cache Spec to Avoid Unnecessary Re-Renders
  const spec = useMemo(() => {
    return JSON.parse(
      JSON.stringify(getChartsSpec(dimensions.width, dimensions.height))
    );
  }, [dimensions]); // Memoize Based on Dimensions

  return (
    <div className = "vega-chart" style = {chartsDivStyle}>
      <VegaLite spec = {spec} actions = {false} />
    </div>
  );
};

const GoodReadsDashboard = () => {
  const [data, setData] = useState([]); // State for CSV Data
  const [showCard, setCard] = useState(window.innerWidth <= 800); // State for Card View

  // Fetch CSV data
  useEffect(() => {
    fetch(reviewsCSV)
      .then(response => response.text())
      .then(text => {
        const results = Papa.parse(text, { header: true });
        let parsed = results.data;
        // Remove trailing blank entry if present
        if (parsed.length > 0 && Object.values(parsed[parsed.length - 1]).every(v => !v?.trim())) {
          parsed = parsed.slice(0, -1);
        }
        setData(parsed);
      });
  }, []);

  // Update Portrait Mode on Resize
  useEffect(() => {
    const handler = () => setCard(window.innerWidth <= 800);
    window.addEventListener('resize', handler); // Update on Resize
    return () => window.removeEventListener('resize', handler); //
  }, []);

  return (
    <div className = "goodreads-dashboard">
      <GoodReadsCharts/>

      {/* Display Reviews */}
      <div className = "goodreads-reviews-container">
        <h2>GoodReads Reviews</h2>
        {showCard ? <GoodReadsCards data = {data} /> : <GoodReadsTable data = {data} />}
      </div>
      <br/>
    </div>
  );
};

export default GoodReadsDashboard;
