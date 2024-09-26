import { useEffect, useState } from 'react';
import Loader from 'react-loaders';
import AnimatedLetters from '../AnimatedLetters';

import Muntakim_Algonquin from '../../assets/images/Muntakim_Algonquin_2020.jpg';
import Python from '../../assets/images/Python.svg';
import SQL from '../../assets/images/SQL.svg';
import C from '../../assets/images/C.svg';
import Golang from '../../assets/images/Golang.svg';
import ASM from '../../assets/images/ASM.svg';
import Verilog from '../../assets/images/Verilog.svg';

import './index.scss';

const Home = () => {
    const [letterClass, setLetterClass] = useState('text-animate');
    const helloArray = ['H', 'i', ' ', 't', 'h', 'e', 'r', 'e', '!'];

    useEffect(() => {
        const timeoutId = setTimeout(() => {
            setLetterClass('text-animate-hover');
        }, 3000);

        // Clear the Timeout.
        return () => clearTimeout(timeoutId);
    }, []);

    return (
        <>
            <div className="loader">
                <Loader type="line-scale-pulse-out" />
            </div>

            <div className="container home-page">
                <span className='tags top-tags'>func main() &#123;</span>

                <div className="stage-cube-container">
                    <br/>
                    <div className="cubespinner">
                        <div className="face1"><img src={Python} alt="Python" /></div>
                        <div className="face2"><img src={SQL} alt="SQL" /></div>
                        <div className="face3"><img src={C} alt="C" /></div>
                        <div className="face4"><img src={Golang} alt="Golang" /></div>
                        <div className="face5"><img src={Verilog} alt="Verilog" /></div>
                        <div className="face6"><img src={ASM} alt="ASM" /></div>
                    </div>
                </div>

                <br/>

                <div className='text-zone'>
                    <h1>
                        <span className="supertitle">
                            <AnimatedLetters
                                letterClass={letterClass}
                                strArray={helloArray}
                                idx={1}
                            />
                        </span> 🙋🏽‍♂️
                    </h1>

                    <br/>

                    <div className="custom-card-content">
                        <h2 className="custom-card-text">
                            <img src={Muntakim_Algonquin} alt="Muntakim Rahman at Algonquin Park, 2020" className="profile-img" />

                            My name is Muntakim and I'm an Electrical Engineering undergraduate with an appetite for software development.&nbsp;
                            <span className="not-on-mobile">
                                I'm passionate about developing innovative technologies that integrate software and hardware. My experiences are in data science and embedded systems;
                                I love working on projects that leverage the intersection of these fields! <br /><br />
                            </span>
                            I've found that I thrive in environments that require first principles thinking, especially in the realm of big data. Whether working on satellite firmware or designing data-centric user interfaces,
                            my goal is to bring robust and scalable solutions to intricate engineering challenges.
                        </h2>
                    </div>
                </div>

                <span className='tags bottom-tags'>&#125;</span>
            </div>
        </>
    );
}

export default Home;