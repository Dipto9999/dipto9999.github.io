import { useEffect, useState } from 'react';
import Loader from 'react-loaders';
import AnimatedLetters from '../AnimatedLetters';

import 'slick-carousel/slick/slick.css';
import 'slick-carousel/slick/slick-theme.css';
import Slider from 'react-slick';

import './index.scss';
import SteamDashboard from '../SteamDashboard';
import GoodReadsDashboard from '../GoodReadsDashboard';
import SpotifyDashboard from '../SpotifyDashboard';

const gameImageCount = 41; // Number of Steam Game Images

// Vite Replaces CRA's Dynamic require() — Eager Glob Gives URL / Raw Text Modules
const gameImageModules = import.meta.glob('../../assets/images/Games/Games_*.jpeg', {
    eager: true,
    import: 'default',
});
const gameTextModules = import.meta.glob('../../assets/images/Games/Games_*.txt', {
    eager: true,
    query: '?raw',
    import: 'default',
});

const pickGlob = (modules, filename) => {
    const entry = Object.entries(modules).find(([path]) => path.endsWith(filename));
    return entry ? entry[1] : null;
};

const TABS = [
    { id: 'games', label: 'Games' },
    { id: 'spotify', label: 'Spotify' },
    { id: 'books', label: 'Books' },
];

const Interests = () => {
    const [letterClass, setLetterClass] = useState('text-animate');
    const [gameImages, setGameImages] = useState([]);
    const [tooltip, setTooltip] = useState({ content: '', visible: false, position: { top: 0, left: 0 } });
    const [activeTab, setActiveTab] = useState('games');

    useEffect(() => {
        const timeoutId = setTimeout(() => {
            setLetterClass('text-animate-hover');
        }, 3000);

        // Load Images and Alt Descriptions Dynamically
        const to_load = [];
        for (let i = 1; i <= gameImageCount; i++) {
            const src = pickGlob(gameImageModules, `Games_${i}.jpeg`);
            const alt = pickGlob(gameTextModules, `Games_${i}.txt`);
            if (src && alt != null) {
                to_load.push({ src, alt });
            } else {
                console.error(`Error Loading Image or Description for Games_${i}`);
            }
        }
        setGameImages(to_load);

        // Clear the Timeout
        return () => clearTimeout(timeoutId);
    }, []);

    // Slider Settings
    const settings = {
        dots: true,
        infinite: true,
        speed: 500,
        slidesToShow: 3,
        slidesToScroll: 3,
        autoplay: true,
        autoplaySpeed: 2000,
        cssEase: 'linear',
        responsive: [
            { breakpoint: 900, settings: { slidesToShow: 2, slidesToScroll: 2 } },
            { breakpoint: 600, settings: { slidesToShow: 1, slidesToScroll: 1 } },
        ],
    };

    const handleMouseEnter = (event, content) => {
        const { top, left, width } = event.target.getBoundingClientRect();
        setTooltip({
            content,
            visible: true,
            position: {
                top: top + window.scrollY,
                left: left + window.scrollX + width / 2
            }
        });
    };

    const handleMouseLeave = () => {
        setTooltip({ ...tooltip, visible: false });
    };

    const handleTabClick = (id) => {
        setActiveTab(id);
        window.scrollTo({ top: 0, left: 0 });
    };

    return (
        <>
            <div className = "loader">
                <Loader type = "line-scale-pulse-out" />
            </div>

            <div className = "container interests-page">
                <span className = "tags top-tags">func main() &#123;</span>

                <div className = "text-zone">
                    <h1 className = "supertitle">
                        <AnimatedLetters
                            letterClass = {letterClass}
                            strArray = {['I', 'n', 't', 'e', 'r', 'e', 's', 't', 's']}
                            idx = {1}
                        />
                    </h1>

                    <div className = "interests-tabs" role = "tablist" aria-label = "Interests">
                        {TABS.map((tab) => (
                            <button
                                key = {tab.id}
                                type = "button"
                                role = "tab"
                                aria-selected = {activeTab === tab.id}
                                className = {activeTab === tab.id ? 'active' : undefined}
                                onClick = {() => handleTabClick(tab.id)}
                            >
                                {tab.label}
                            </button>
                        ))}
                    </div>

                    {activeTab === 'games' && (
                        <section className = "interests-section">
                            <SteamDashboard />

                            <div className = "photo-gallery">
                                {
                                    tooltip.visible
                                    && (
                                        <div className = "tooltip" style = {{ top: tooltip.position.top, left: tooltip.position.left}}>
                                            {tooltip.content}
                                        </div>
                                    )
                                }
                                <Slider {...settings}>
                                    {gameImages.map((image, index) => (
                                        <div className = "photo-items" key = {index}>
                                            <img
                                                src = {image.src}
                                                alt = {image.alt}
                                                loading = "lazy"
                                                onMouseEnter = {(e) => handleMouseEnter(e, image.alt)}
                                                onMouseLeave = {handleMouseLeave}
                                            />
                                        </div>
                                    ))}
                                </Slider>
                            </div>
                        </section>
                    )}
                </div>

                {activeTab === 'spotify' && (
                    <section className = "interests-section">
                        <SpotifyDashboard />
                    </section>
                )}

                {activeTab === 'books' && (
                    <section className = "interests-section">
                        <GoodReadsDashboard />
                    </section>
                )}

                <span className = "tags bottom-tags">&#125;</span>
            </div>
        </>
    );
};

export default Interests;
