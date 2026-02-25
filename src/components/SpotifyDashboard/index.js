import { useMemo, useEffect, useState } from 'react';
import { VegaLite } from 'react-vega';

import defaultSpotify from '../../assets/data/spotify/Charts/Muntakim_Standard.json';
import portraitSpotify from '../../assets/data/spotify/Charts/Muntakim_Portrait.json';
import landscapeSpotify from '../../assets/data/spotify/Charts/Muntakim_Landscape.json';
import tabletPortraitSpotify from '../../assets/data/spotify/Charts/Muntakim_TabletPortrait.json';
import tabletSpotify from '../../assets/data/spotify/Charts/Muntakim_Tablet.json';

import './index.scss';

const chartContainerStyle = {
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  width: '100%',
};

const getSpotifySpec = (width, height) => {
  if (width <= 550 && height >= width) return portraitSpotify;       // Phone Portrait
  if (width <= 900 && width > height) return landscapeSpotify;       // Phone Landscape
  if (width <= 900) return tabletPortraitSpotify;                    // iPad Mini / Air / small tablet portrait
  if (width <= 1200) return tabletSpotify;                           // Large tablet / iPad Pro
  return defaultSpotify;                                             // Desktop
};

const isPortrait = (w, h) => w <= 550 && h >= w;

/** Extract card data from a spec that has _cardData metadata + embedded datasets */
const extractCardData = (spec) => {
  const meta = spec._cardData;
  if (!meta || !spec.datasets) return null;
  const topSongs = spec.datasets[meta.topSongsDataset] || [];
  const recentlyPlayed = spec.datasets[meta.recentlyPlayedDataset] || [];
  return { topSongs, recentlyPlayed };
};

/** Spotify-style track card */
const TrackCard = ({ rank, song, artist, time }) => (
  <div className="spotify-track-card">
    <span className="spotify-track-rank">{rank}</span>
    <div className="spotify-track-info">
      <span className="spotify-track-title">{song}</span>
      <span className="spotify-track-artist">{artist}</span>
    </div>
    {time && <span className="spotify-track-time">{time}</span>}
  </div>
);

/** Section: Top Songs or Recently Played as cards */
const TrackCardList = ({ title, subtitle, tracks, showTime }) => (
  <div className="spotify-card-section">
    <h3 className="spotify-card-section-title">{title}</h3>
    {subtitle && <p className="spotify-card-section-subtitle">{subtitle}</p>}
    <div className="spotify-card-list">
      {tracks.map((t, i) => (
        <TrackCard
          key={i}
          rank={t.rank}
          song={t.song}
          artist={t.artist}
          time={showTime ? t.time : null}
        />
      ))}
    </div>
  </div>
);

const SpotifyDashboard = () => {
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

  const rawSpec = useMemo(() => {
    return getSpotifySpec(dimensions.width, dimensions.height);
  }, [dimensions]);

  const spec = useMemo(() => {
    return JSON.parse(JSON.stringify(rawSpec));
  }, [rawSpec]);

  const portrait = isPortrait(dimensions.width, dimensions.height);
  const cardData = portrait ? extractCardData(rawSpec) : null;

  return (
    <>
      <div className="vega-chart" style={chartContainerStyle}>
        <VegaLite spec={spec} actions={false} />
      </div>
      {portrait && cardData && (
        <div className="spotify-cards-row">
          <TrackCardList
            title="Top Songs"
            subtitle="All Time"
            tracks={cardData.topSongs}
            showTime={false}
          />
          <TrackCardList
            title="Recently Played"
            tracks={cardData.recentlyPlayed}
            showTime={true}
          />
        </div>
      )}
    </>
  );
};

export default SpotifyDashboard;
