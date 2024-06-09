import AnimatedLetters from "../AnimatedLetters"
import Muntakim_UBC from "../../assets/images/Muntakim_Headshot_2019.jpg"
import Tesla_Interns_2023 from "../../assets/images/Tesla_Interns_2023.jpg"
import Geotab_Volleyball_2022 from "../../assets/images/Geotab_Volleyball_2022.jpg"
import UBC_Orbit_2019 from "../../assets/images/UBC_Orbit_2019.jpg"
import Optimus from "../../assets/images/Optimus.jpg"
import { useEffect, useState } from 'react';
import Loader from 'react-loaders'

import './index.scss';

const Experiences = () => {
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
        <div className='container experiences-page'>
            <div className='text-zone'>
                <h1 class="supertitle"><AnimatedLetters
                    letterClass={letterClass}
                    strArray={['E', 'x', 'p', 'e', 'r', 'i', 'e', 'n', 'c', 'e', 's']}
                    idx={10}
                /></h1>

                <p class="custom-card-text">
                    <img
                        src={Muntakim_UBC}
                        class="float-right"
                        id="Muntakim_UBC"
                        alt="Muntakim Rahman : UBC Sauder School Headshot"
                    /><br />
                    <div>
                        ⚡ I'm currently pursuing a <strong>Bachelors in Electrical Engineering</strong> at the <strong><a href="https://ece.ubc.ca/undergraduates/programs/electrical-engineering-program/" class="external-links">University of British Columbia</a></strong>,
                        with an expected graduation in May 2026. My academic background also includes a <strong><a href="https://extendedlearning.ubc.ca/programs-credentials/key-capabilities-data-science-certificate" class="external-links">Certificate in Data Science</a></strong>,
                        where I enhanced my skills in data analytics and visualization, as well as some machine learning. ⚡
                    </div>
                </p>

                <div class="section-separator"></div>

                <p class="custom-card-text">
                    <strong>Software Applications Engineering Intern @ <a href="https://www.tesla.com/en_eu/megapack" class="external-links">TESLA, Inc</a> 🔋 </strong>(Jan 2023 - Jan 2024,&nbsp;May 2024 - Present)<br/>
                    <hr class="hr-separator"/>
                    <img
                        src={Tesla_Interns_2023}
                        class="float-left"
                        alt="Tesla Deer Creek Interns Fall 2023"
                    /><br />
                    <div>
                        As part of the Industrial Energy Storage organization, I developed software automation and tools to analyze project performance metrics and generate reports. I helped standardize data management best practices in reporting
                        key performance indicators to partner engineering teams and org leadership.
                    </div>
                </p>

                <div class="section-separator"></div>

                <p class="custom-card-text">
                    <strong>Product Coordinator Intern @ <a href="https://www.geotab.com/" class="external-links">GEOTAB, Inc</a> 🌐 </strong>(Jan 2022 - Jan 2023)<br/>
                    <hr class="hr-separator"/>
                    <img
                        src={Geotab_Volleyball_2022}
                        class="float-right"
                        alt="GEOTAB Interns 2022"
                    /><br />
                    <div>
                        I coordinated UX research initiatives across Product Management teams to help develop vehicle telematics hardware and software solutions. I presented product insights, from both
                        customer interviews and statistical analysis, to developers, product managers, and executives in informing roadmap decisions. During my time here, I also participated as a speaker for the Summer Junior Student Program,
                        and provided secondary school students an Introduction to Big Data.
                    </div>
                </p>

                <div class="section-separator"></div>

                <p class="custom-card-text">
                    <strong>Firmware Developer @ <a href="https://www.ubcorbit.com/" class="external-links">UBC Orbit</a> 🛰️ </strong>(Sept 2019 - Nov 2022)<br/>
                    <hr class="hr-separator"/>
                    <img
                       src={UBC_Orbit_2019}
                       class="float-left"
                       alt="UBC Orbit Satellite Design Team 2019"
                    /><br />
                    <div class="custom-card-text">
                        At university, I've had the opportunity to work on the ALEASAT project as part of the Command and Data-Handling (CDH) subteam. I worked on developing the onboard-computer telemetry functionality, intended to address
                        system failure risks and ensure critical orbital tasks were performed with deterministic execution.
                    </div>
                </p>

                <div class="section-separator"></div>

                <p class="custom-card-text">
                    <img
                        src={Optimus}
                        class="float-right"
                        alt="Tesla Bot Optimus in Front of a Cybertruck"
                    /><br />
                    <div class="custom-card-text">
                        A potential market that excites me is the emerging field of humanoid and autonomous robots! 🤖 I am keen to
                        closely follow new developments in this technological space!
                    </div>
                </p>
            </div>
        </div>
        <Loader type="line-scale-pulse-out"/>
        </>
    )
}

export default Experiences