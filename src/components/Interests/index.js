import { useEffect, useState } from 'react';
import Loader from 'react-loaders';
import AnimatedLetters from '../AnimatedLetters';

import 'slick-carousel/slick/slick.css';
import 'slick-carousel/slick/slick-theme.css';
import Slider from 'react-slick';
import { VegaLite } from 'react-vega';

import './index.scss';

const gameImageCount = 35; // Number of Steam Game Images

const Interests = () => {
    const [letterClass, setLetterClass] = useState('text-animate');
    const [gameImages, setGameImages] = useState([]);
    const [tooltip, setTooltip] = useState({ content: '', visible: false, position: { top: 0, left: 0 } });
    const [spec, setSpec] = useState({}); // Initial spec

    useEffect(() => {
        const timeoutId = setTimeout(() => {
            setLetterClass('text-animate-hover');
        }, 3000);

        // Load Images and Alt Descriptions Dynamically
        const loadGameFiles = async () => {
            const to_load = [];
            for (let i = 1; i <= gameImageCount; i++) {
                try {
                    const imagePath = require(`../../assets/images/Games/Games_${i}.jpeg`);
                    const descriptionPath = require(`../../assets/images/Games/Games_${i}.txt`);
                    const description = await fetch(descriptionPath).then(response => response.text());
                    to_load.push({ src: imagePath, alt: description });
                } catch (error) {
                    console.error(`Error Loading Image or Description for Games_${i}: ${error}`);
                }
            }
            setGameImages(to_load);
        };

        loadGameFiles();

        // Clear Timeout
        return () => clearTimeout(timeoutId);
    }, []);

    useEffect(() => {
        const updateSpecForScreenSize = () => {
            const windowWidth = window.innerWidth;
            const windowHeight = window.innerHeight;

            const calculateFontSize = (base, ratio) => Math.max(base, Math.round(base * ratio));
            const calculateDimension = (base, ratio) => Math.round(base * ratio);

            const ratioWidth = windowWidth / 1440; // Assume Base Width = 1440
            const ratioHeight = windowHeight / 900; // Assume Base Height = 900

            const newSpec = {
                config: {
                    view: {
                        continuousWidth: calculateDimension(300, ratioWidth),
                        continuousHeight: calculateDimension(300, ratioHeight),
                        strokeOpacity: 0,
                        strokeWidth: 1.5,
                    },
                    axis: {
                        labelFontSize: calculateFontSize(12, ratioWidth),
                        titleFontSize: calculateFontSize(16, ratioWidth),
                    },
                    legend: {
                        labelFontSize: calculateFontSize(12, ratioWidth),
                        titleFontSize: calculateFontSize(16, ratioWidth),
                    },
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
                                    color: '#141331',
                                    fontSize: calculateFontSize(80, ratioWidth),
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
                                        value: 50,
                                    },
                                },
                                height: calculateDimension(150, ratioHeight),
                                title: {
                                    text: 'Player Level',
                                    anchor: 'middle',
                                    fontSize: calculateFontSize(20, ratioWidth),
                                },
                                width: calculateDimension(300, ratioWidth),
                            },
                            {
                                data: {
                                    name: 'data-26154e4df75ff9a35b42d85a483593b2',
                                },
                                mark: {
                                    type: 'text',
                                    align: 'center',
                                    baseline: 'middle',
                                    color: '#141331',
                                    fontSize: calculateFontSize(80, ratioWidth),
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
                                        value: 50,
                                    },
                                },
                                height: calculateDimension(150, ratioHeight),
                                title: {
                                    text: 'Played Games',
                                    anchor: 'middle',
                                    fontSize: calculateFontSize(20, ratioWidth),
                                },
                                width: calculateDimension(300, ratioWidth),
                            },
                        ],
                        title: {
                            text: 'Player Stats',
                            anchor: 'middle',
                            fontSize: calculateFontSize(50, ratioWidth),
                        },
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
                                        '#00008B', '#800080', '#FFA500', '#FF4500', '#8B4513',
                                        '#006400', '#8B0000', '#FFD700', '#4682B4', '#2E8B57',
                                    ],
                                },
                                title: 'Games',
                                type: 'nominal',
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
                        height: calculateDimension(400, ratioHeight),
                        title: {
                            text: "Dipto9999's Top 15 Steam Games",
                            anchor: 'middle',
                            fontSize: calculateFontSize(20, ratioWidth),
                            subtitle: ['Total Playtime: 1450.21 Hours'],
                            subtitleFontSize: calculateFontSize(16, ratioWidth),
                        },
                        width: calculateDimension(400, ratioWidth),
                    },
                ],
                title: {
                    text: "Dipto9999's Steam Dashboard",
                    anchor: 'middle',
                    fontSize: calculateFontSize(60, ratioWidth),
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
                    ],
                },
            };

            setSpec(newSpec);
        };

        window.addEventListener('resize', updateSpecForScreenSize);
        updateSpecForScreenSize();

        return () => window.removeEventListener('resize', updateSpecForScreenSize);
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
    };

    const handleMouseEnter = (event, content) => {
        const { top, left, width } = event.target.getBoundingClientRect();
        setTooltip({
            content,
            visible: true,
            position: {
                top: top + window.scrollY,
                left: left + window.scrollX + width / 2,
            },
        });
    };

    const handleMouseLeave = () => {
        setTooltip({ ...tooltip, visible: false });
    };

    return (
        <>
            <div className="loader">
                <Loader type="line-scale-pulse-out" />
            </div>

            <div className="container interests-page">
                <span className="tags top-tags">func main() &#123;</span>

                <div className="text-zone">
                    <h1 className="supertitle">
                        <AnimatedLetters
                            letterClass={letterClass}
                            strArray={['I', 'n', 't', 'e', 'r', 'e', 's', 't', 's']}
                            idx={1}
                        />
                    </h1>

                    {/* Vega-Lite Visualization */}
                    <div className="vega-chart">
                        <VegaLite spec={spec} actions={false} />
                    </div>

                    <div className="photo-gallery">
                        {
                            tooltip.visible && (
                                <div className="tooltip" style={{ top: tooltip.position.top, left: tooltip.position.left }}>
                                    {tooltip.content}
                                </div>
                            )
                        }
                        <Slider {...settings}>
                            {gameImages.map((image, index) => (
                                <div className="photo-items" key={index}>
                                    <img
                                        src={image.src}
                                        alt={image.alt}
                                        onMouseEnter={(e) => handleMouseEnter(e, image.alt)}
                                        onMouseLeave={handleMouseLeave}
                                    />
                                </div>
                            ))}
                        </Slider>
                    </div>
                </div>

                <span className="tags bottom-tags">&#125;</span>
            </div>
        </>
    );
};

export default Interests;
