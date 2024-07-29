import { useEffect, useState } from 'react';
import Loader from 'react-loaders';
import AnimatedLetters from '../AnimatedLetters';

import 'slick-carousel/slick/slick.css';
import 'slick-carousel/slick/slick-theme.css';
import Slider from 'react-slick';

import './index.scss';

const gameImageCount = 35; // Number of Steam Game Images

const Interests = () => {
    const [letterClass, setLetterClass] = useState('text-animate');
    const [gameImages, setGameImages] = useState([]);
    const [tooltip, setTooltip] = useState({ content: '', visible: false, position: { top: 0, left: 0 } });

    useEffect(() => {
        const timeoutId = setTimeout(() => {
            setLetterClass('text-animate-hover');
        }, 3000);

        // Load Images Dynamically
        const loadImages = () => {
            const to_load = [];
            for (let i = 1; i <= gameImageCount; i++) {
                try {
                    const imagePath = require(`../../assets/images/Games/Games_${i}.jpeg`);
                    to_load.push({ src: imagePath, alt: `Game ${i}` });
                } catch (error) {
                    console.error(`Error loading image Games_${i}.jpeg: ${error}`);
                }
            }
            setGameImages(to_load);
        };

        loadImages();

        // Clear the Timeout.
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

                    <div className="photo-gallery">
                        <Slider {...settings}>
                            {gameImages.map((image, index) => (
                                <div className="photo-items">
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

                {
                    tooltip.visible && (
                        <div
                            className="tooltip"
                            style={{ top: tooltip.position.top, left: tooltip.position.left }}
                        >
                            {tooltip.content}
                        </div>
                    )
                }

                <span className="tags bottom-tags">&#125;</span>
            </div>
        </>
    );
};

export default Interests;