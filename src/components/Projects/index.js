import { useEffect, useState } from 'react';
import Loader from 'react-loaders'
import AnimatedLetters from "../AnimatedLetters"

import Data_Collection_App from "../../assets/images/Data_Collection_App.jpeg"
import './index.scss';

const Projects = () => {
    const [letterClass, setLetterClass] = useState('text-animate')

    useEffect(() => {
        const timeoutId = setTimeout(() => {
            setLetterClass('text-animate-hover');
        }, 3000);

        return () => clearTimeout(timeoutId);
    }, []);

    return (
        <>
            <div className="loader">
                <Loader type="line-scale-pulse-out" />
            </div>

            <div className='container projects-page'>
                <span className='tags top-tags'>func main() &#123;</span>

                <div className='text-zone'>
                    <h1 className="supertitle">
                        <AnimatedLetters
                            letterClass={letterClass}
                            strArray={['P', 'r', 'o', 'j', 'e', 'c', 't', 's']}
                            idx={1}
                        />
                    </h1>

                    <p className="custom-card-content">
                        <strong>Reflow Oven Controller <a href="https://github.com/TZlindra/ELEC291Project1Code" className="external-links">[Github Repository]</a></strong>

                        <hr className="hr-separator"/>

                        <iframe
                            title="Reflow Oven Controller"
                            src="https://www.youtube.com/embed/Bzm737dduOw"
                            className="float-left"
                            frameBorder="0"
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                            allowFullScreen
                        ></iframe>

                        <br/>

                        <span className="custom-card-text">
                            An <span className="tech-highlight">8051 ASM</span> program that controls a reflow oven temperature profile for soldering <span className="tech-highlight">EFM8LB1</span> surface mount components.
                            A <span className="tech-highlight">Tkinter</span> desktop application was developed to visualize the temperature profile and send reflow logs to a <span className="tech-highlight">Google Cloud Platform</span> server for
                            storage and data post-processing.
                        </span>
                    </p>

                    <p className="custom-card-content">
                        <strong>Remote Controlled, Metal Detecting Robot <a href="https://github.com/TZlindra/ELEC291Project2" className="external-links">[Github Repository]</a></strong>

                        <hr className="hr-separator"/>

                        <iframe
                            title="Remote Controlled, Metal Detecting Robot"
                            src="https://www.youtube.com/embed/mVCBSWdCpsY"
                            className="float-right"
                            frameBorder="0"
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                            allowFullScreen
                        ></iframe>

                        <br/>

                        <span className="custom-card-text">
                            A wirelessly controlled, battery operated robot which detects metal with principles of electromagnetic induction. The <span className="tech-highlight">C</span> firmware was implemented
                            on an <span className="tech-highlight">STM32L0</span> microcontroller and <span className="tech-highlight">EFM8LB1</span> microcontrollers and validated with <span className="tech-highlight">matplotlib</span> data visualization.
                        </span>
                    </p>

                    <p className="custom-card-content contains-video">
                        <strong>STM32 Morse Code Translator <a href="https://github.com/Dipto9999/STM32-Morse_Translator" className="external-links">[Github Repository]</a></strong>

                        <hr className="hr-separator"/>

                        <video controls className="float-left">
                            <source
                                title="STM32 Morse Code Translator"
                                src="https://user-images.githubusercontent.com/52113009/130340990-af157688-376e-429a-9239-4267415a930c.mp4"
                                type="video/mp4"
                            />
                            <i>This video is not supported by your browser.</i>
                        </video>

                        <br/>

                        <span className="custom-card-text">
                            A <span className="tech-highlight">C</span> program which acquires a stream of ASCII characters from serial port via <span className="tech-highlight">UART</span>, and outputs the corresponding Morse code on
                            an <span className="tech-highlight">STM32L4 Nucleo</span> board LED.
                        </span>
                    </p>

                    <p className="custom-card-content contains-video">
                        <strong>Google PageRank Engine <a href="https://github.com/Dipto9999/Google_PageRank" className="external-links">[Github Repository]</a></strong>

                        <hr className="hr-separator"/>

                        <video controls className="float-right">
                            <source
                                title="Google PageRank Engine"
                                src="https://user-images.githubusercontent.com/52113009/135669850-cdea2f2d-a0b1-475c-9969-27d526ef226e.mp4"
                                type="video/mp4"
                            />
                            <i>This video is not supported by your browser.</i>
                        </video>

                        <br/>

                        <span className="custom-card-text">
                            A simplified implementation of Google's PageRank algorithm in <span className="tech-highlight">C</span>, which ranks web pages with a <span className="tech-highlight">MATLAB</span> engine based on hyperlink structure.
                        </span>
                    </p>

                    <p className="custom-card-content contains-video">
                        <strong>Stock Portfolio App <a href="https://github.com/Dipto9999/Stock_Portfolio_App" className="external-links">[Github Repository]</a></strong>

                        <hr className="hr-separator"/>

                        <video controls className="float-left">
                            <source
                                title="Stock Portfolio App"
                                src="https://user-images.githubusercontent.com/52113009/197423041-074e3278-a808-49dd-a7a9-8ad1b2a625b8.mp4"
                                type="video/mp4"
                            />
                            <i>This video is not supported by your browser.</i>
                        </video>

                        <br/>

                        <span className="custom-card-text">
                            A <span className="tech-highlight">Tkinter</span> desktop application for monitoring and analyzing stock market trends to support investment decisions.
                        </span>
                    </p>

                    <p className="custom-card-content">
                        <strong>Data Collection App <a href="https://github.com/Dipto9999/Data_Collection_App" className="external-links">[Github Repository]</a></strong>

                        <hr className="hr-separator"/>

                        <img
                            src={Data_Collection_App}
                            className="float-right"
                            alt="Data Collection App"
                        />

                        <br/>

                        <span className="custom-card-text">
                            A <span className="tech-highlight">Django</span> web application that collects user reported COVID-19 survey data in order to make economic decisions.
                        </span>
                    </p>
                </div>

                <span className='tags bottom-tags'>&#125;</span>
            </div>
        </>
    )
}

export default Projects;
