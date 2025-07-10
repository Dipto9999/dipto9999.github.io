import { useEffect, useState } from 'react';
import Loader from 'react-loaders'
import AnimatedLetters from "../AnimatedLetters"

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
        <div>
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

                    <div className="custom-card-content contains-video">
                        <strong>Introducing WALL-E<a href="https://github.com/Dipto9999/Self_Balancing_Robot" className="external-links"> [Github Repository]</a></strong>

                        <hr className="hr-separator"/>

                        <iframe
                            title="WALL-E : Self Balancing Robot"
                            src="https://youtube.com/embed/UMmxqQl_EAc"
                            className="float-left"
                            frameBorder="0"
                            allow="autoplay; encrypted-media"
                            allowFullScreen
                        ></iframe>

                        <br/>

                        <span className="custom-card-text">
                            <span className="tech-highlight">WALL-E</span> is a <span className="tech-highlight">Bluetooth</span> controlled robot with
                            autonomous balancing capabilities, live video streaming, and secure <span className="tech-highlight">RFID</span> authentication.
                            The robot system is comprised of an <span className="tech-highlight">Arduino Nano 33 BLE Sense</span>, <span className="tech-highlight">STM32</span>, and <span className="tech-highlight">Raspberry Pi Zero</span>.
                            Together, these enable WALL-E to avoid obstacles in real time and stream live video via <span className="tech-highlight">HTTP</span>, uploading
                            saved footage to <span className="tech-highlight">AWS S3</span> for secure storage.
                        </span>
                    </div>

                    <div className="custom-card-content">
                        <strong>TCP Chat Server - Desktop App<a href="https://github.com/Dipto9999/TCP_Chat_Application" className="external-links"> [Github Repository]</a></strong>

                        <hr className="hr-separator"/>

                        <iframe
                            title="TCP Chat Server - Desktop App"
                            src="https://www.youtube.com/embed/xPEcu-LOH6w"
                            className="float-right"
                            frameBorder="0"
                            allow="autoplay; encrypted-media"
                            allowFullScreen
                        ></iframe>
                        <br/>
                        <span className="custom-card-text">
                            A TCP chat application build with <span className="tech-highlight">Python</span>'s concurrency implementations.
                            This uses <span className="tech-highlight">multiprocessing</span> for isolated client/server processes and <span className="tech-highlight">multithreading</span> for concurrent message handling.
                            The design supports error handling for disconnects, client reconnection, and synchronized message delivery using shared memory.
                        </span>
                    </div>

                    <div className="custom-card-content">
                        <strong>Reflow Oven Controller <a href="https://github.com/TZlindra/ELEC291Project1Code" className="external-links">[Github Repository]</a></strong>

                        <hr className="hr-separator"/>

                        <iframe
                            title="Reflow Oven Controller"
                            src="https://www.youtube.com/embed/Bzm737dduOw"
                            className="float-left"
                            frameBorder="0"
                            allow="autoplay; encrypted-media"
                            allowFullScreen
                        ></iframe>

                        <br/>

                        <span className="custom-card-text">
                            An <span className="tech-highlight">8051 ASM</span> program that controls a reflow oven temperature profile for soldering <span className="tech-highlight">EFM8LB1</span> surface mount components.
                            A <span className="tech-highlight">Tkinter</span> desktop application was developed to visualize the temperature profile and send reflow logs to a <span className="tech-highlight">Google Cloud Platform</span> server for
                            storage and data post-processing.
                        </span>
                    </div>

                    <div className="custom-card-content">
                        <strong>Metal Detector Robot <a href="https://github.com/TZlindra/ELEC291Project2" className="external-links">[Github Repository]</a></strong>

                        <hr className="hr-separator"/>

                        <iframe
                            title="Metal Detector Robot"
                            src="https://www.youtube.com/embed/mVCBSWdCpsY"
                            className="float-right"
                            frameBorder="0"
                            allow="autoplay; encrypted-media"
                            allowFullScreen
                        ></iframe>

                        <br/>

                        <span className="custom-card-text">
                            A wirelessly controlled, battery operated robot which detects metal with principles of electromagnetic induction. The <span className="tech-highlight">C</span> firmware was implemented
                            on an <span className="tech-highlight">STM32L0</span> microcontroller and <span className="tech-highlight">EFM8LB1</span> microcontrollers and validated with <span className="tech-highlight">matplotlib</span> data visualization.
                        </span>
                    </div>

                    <div className="custom-card-content contains-video">
                        <strong>Stock Portfolio - Desktop App <a href="https://github.com/Dipto9999/Stock_Portfolio_App" className="external-links">[Github Repository]</a></strong>

                        <hr className="hr-separator"/>

                        <iframe
                            title="Stock Portfolio - Desktop App"
                            src="https://www.youtube.com/embed/CrgSIBPTlN8"
                            className="float-left"
                            frameBorder="0"
                            allow="autoplay; encrypted-media"
                            allowFullScreen
                        ></iframe>

                        <br/>

                        <span className="custom-card-text">
                            A <span className="tech-highlight">Tkinter</span> desktop application for monitoring and analyzing stock market trends to support investment decisions.
                        </span>
                    </div>

                    <div className="custom-card-content">
                        <strong>Student Data Collection - Web App <a href="https://github.com/Dipto9999/Data_Collection_App" className="external-links">[Github Repository]</a></strong>

                        <hr className="hr-separator"/>

                        <iframe
                            title="Student Data Collection - Web App"
                            src="https://www.youtube.com/embed/v5BKOoV6Blw"
                            className="float-right"
                            frameBorder="0"
                            allow="autoplay; encrypted-media"
                            allowFullScreen
                        ></iframe>

                        <br/>

                        <span className="custom-card-text">
                            An <span className="tech-highlight">oTree</span> web application that collects user reported COVID-19 survey data in order to make economic decisions.
                        </span>
                    </div>
                </div>
                <span className='tags bottom-tags'>&#125;</span>
            </div>
        </div>
    )
}

export default Projects;
