import AnimatedLetters from "../AnimatedLetters"
import Data_Collection_App from "../../assets/images/Data_Collection_App.jpeg"
import { useEffect, useState } from 'react';
import Loader from 'react-loaders'
import './index.scss';

const Projects = () => {
    const [letterClass, setLetterClass] = useState('text-animate')

    useEffect(() => {
        const timeoutId = setTimeout(() => {
            setLetterClass('text-animate-hover');
        }, 3000);

        // Clear the Timeout.
        return () => clearTimeout(timeoutId);
    }, []);

    return (
        <>
        <div className='container projects-page'>
            <div className='text-zone'>
                <h1 class="supertitle"><AnimatedLetters
                    letterClass={letterClass}
                    strArray={['P', 'r', 'o', 'j', 'e', 'c', 't', ' ', 'H', 'i', 'g', 'h', 'l', 'i', 'g', 'h', 't', 's']}
                    idx={7}
                /></h1>
                <p class="custom-card-text">
                    <strong>Reflow Oven Controller <a href="https://github.com/TZlindra/ELEC291Project1Code" class="external-links">[Github Repository]</a></strong><br/>
                    <hr class="hr-separator"/>
                    <iframe
                        title="Reflow Oven Controller"
                        src="https://www.youtube.com/embed/Bzm737dduOw"
                        class="float-left"
                        frameborder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowfullscreen
                    ></iframe>
                    <div>
                        An <span class="tech-highlight">8051 ASM</span> program that controls a reflow oven temperature profile for soldering <span class="tech-highlight">EFM8LB1</span> surface mount components.
                        A <span class="tech-highlight">Tkinter</span> desktop application was developed to visualize the temperature profile and send reflow logs to a <span class="tech-highlight">Google Cloud Platform</span> server for
                        storage and data post-processing.
                    </div>
                </p>

                <div class="section-separator"></div>

                <p class="custom-card-text">
                    <strong>Remote Controlled, Metal Detecting Robot <a href="https://github.com/TZlindra/ELEC291Project2" class="external-links">[Github Repository]</a></strong><br/>
                    <hr class="hr-separator"/>
                    <iframe
                        title="Remote Controlled, Metal Detecting Robot"
                        src="https://www.youtube.com/embed/mVCBSWdCpsY"
                        class="float-right"
                        frameborder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowfullscreen
                    ></iframe>
                    <div>
                        A wirelessly controlled, battery operated robot which detects metal with principles of electromagnetic induction. The <span class="tech-highlight">C</span> firmware was implemented
                        on an <span class="tech-highlight">STM32L0</span> microcontroller and <span class="tech-highlight">EFM8LB1</span> microcontrollers and validated with <span class="tech-highlight">matplotlib</span> data visualization.
                    </div>
                </p>

                <div class="section-separator"></div>

                <p class="custom-card-text contains-video">
                    <strong>STM32 Morse Code Translator <a href="https://github.com/Dipto9999/STM32-Morse_Translator" class="external-links">[Github Repository]</a></strong><br/>
                    <hr class="hr-separator"/>
                    <video controls className="float-left">
                        <source
                            title="STM32 Morse Code Translator"
                            src="https://user-images.githubusercontent.com/52113009/130340990-af157688-376e-429a-9239-4267415a930c.mp4"
                            type="video/mp4"
                        />
                        <i>This video is not supported by your browser.</i>
                    </video>
                    <div>
                        A <span class="tech-highlight">C</span> program which acquires a stream of ASCII characters from serial port via <span class="tech-highlight">UART</span>, and outputs the corresponding Morse code on
                        an <span class="tech-highlight">STM32L4 Nucleo</span> board LED.
                    </div>
                </p>

                <div class="section-separator"></div>

                <p class="custom-card-text contains-video">
                    <strong>Google PageRank Engine <a href="https://github.com/Dipto9999/Google_PageRank" class="external-links">[Github Repository]</a></strong><br/>
                    <hr class="hr-separator"/>
                    <video controls className="float-right">
                        <source
                            title="Google PageRank Engine"
                            src="https://user-images.githubusercontent.com/52113009/135669850-cdea2f2d-a0b1-475c-9969-27d526ef226e.mp4"
                            type="video/mp4"
                        />
                        <i>This video is not supported by your browser.</i>
                    </video>
                    <div>
                        A simplified implementation of Google's PageRank algorithm in <span class="tech-highlight">C</span>, which ranks web pages with a <span class="tech-highlight">MATLAB</span> engine based on hyperlink structure.
                    </div>
                </p>

                <div class="section-separator"></div>

                <p class="custom-card-text contains-video">
                    <strong>Stock Portfolio App <a href="https://github.com/Dipto9999/Stock_Portfolio_App" class="external-links">[Github Repository]</a></strong><br/>
                    <hr class="hr-separator"/>
                    <video controls className="float-left">
                        <source
                            title="Stock Portfolio App"
                            src="https://user-images.githubusercontent.com/52113009/197423041-074e3278-a808-49dd-a7a9-8ad1b2a625b8.mp4"
                            type="video/mp4"
                        />
                        <i>This video is not supported by your browser.</i>
                    </video>
                    <div>
                        A <span class="tech-highlight">Tkinter</span> desktop application for monitoring and analyzing stock market trends to support investment decisions.
                    </div>
                </p>

                <div class="section-separator"></div>

                <div class="custom-card">
                    <p class="custom-card-text">
                        <strong>Data Collection App <a href="https://github.com/Dipto9999/Data_Collection_App" class="external-links">[Github Repository]</a></strong><br/>
                        <hr class="hr-separator"/>
                        <img
                            src={Data_Collection_App}
                            class="float-right"
                            alt="Data Collection App"
                        />
                        <div>
                            A <span class="tech-highlight">Django</span> web application that collects user reported COVID-19 survey data in order to make economic decisions.
                        </div>
                    </p>
                </div>
            </div>
        </div>
        <Loader type="line-scale-pulse-out"/>
        </>
    )
}

export default Projects;
