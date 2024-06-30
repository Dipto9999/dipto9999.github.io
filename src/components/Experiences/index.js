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

        return () => clearTimeout(timeoutId);
    }, []);

    return (
        <>
            <div className="loader">
                <Loader type="line-scale-pulse-out" />
            </div>

            <div className='container experiences-page'>
                <span className='tags top-tags'>func main() &#123;</span>

                <div className='text-zone'>
                    <h1 className="supertitle">
                        <AnimatedLetters
                            letterClass={letterClass}
                            strArray={['E', 'x', 'p', 'e', 'r', 'i', 'e', 'n', 'c', 'e', 's']}
                            idx={1}
                        />
                    </h1>

                    <p className="custom-card-content">
                        <img
                            src={Muntakim_UBC}
                            className="float-right"
                            id="Muntakim_UBC"
                            alt="Muntakim Rahman : UBC Sauder School Headshot"
                        />

                        <br/>

                        <span className="custom-card-text">
                            ⚡ I'm currently pursuing a <strong>Bachelors in Electrical Engineering</strong> at the <strong><a href="https://ece.ubc.ca/undergraduates/programs/electrical-engineering-program/" className="external-links">University of British Columbia</a></strong>,
                            with an expected graduation in May 2026. My academic background also includes a <strong><a href="https://extendedlearning.ubc.ca/programs-credentials/key-capabilities-data-science-certificate" className="external-links">Certificate in Data Science</a></strong>,
                            where I enhanced my skills in data analytics and visualization, as well as some machine learning. ⚡
                        </span>
                    </p>

                    <p className="custom-card-content">
                        <strong>Software Applications Engineering Intern @ <a href="https://www.tesla.com/en_eu/megapack" className="external-links">TESLA, Inc</a> 🔋 </strong>(Jan 2023 - Jan 2024,&nbsp;May 2024 - Present)
                        <hr className="hr-separator"/>
                        <img
                            src={Tesla_Interns_2023}
                            className="float-left"
                            alt="Tesla Deer Creek Interns Fall 2023"
                        />

                        <br/>

                        <span className="custom-card-text">
                            As part of the Industrial Energy Storage organization, I developed software automation and tools to analyze project performance metrics and generate reports. I helped standardize data management best practices in reporting
                            key performance indicators to partner engineering teams and org leadership.
                        </span>
                    </p>

                    <p className="custom-card-content">
                        <strong>Product Coordinator Intern @ <a href="https://www.geotab.com/" className="external-links">GEOTAB, Inc</a> 🌐 </strong>(Jan 2022 - Jan 2023)
                        <hr className="hr-separator"/>
                        <img
                            src={Geotab_Volleyball_2022}
                            className="float-right"
                            alt="GEOTAB Interns 2022"
                        />

                        <br/>

                        <span className="custom-card-text">
                            I coordinated UX research initiatives across Product Management teams to help develop vehicle telematics hardware and software solutions. I presented product insights, from both
                            customer interviews and statistical analysis, to developers, product managers, and executives in informing roadmap decisions. During my time here, I also participated as a speaker for the Summer Junior Student Program,
                            and provided secondary school students an Introduction to Big Data.
                        </span>
                    </p>

                    <p className="custom-card-content">
                        <strong>Firmware Developer @ <a href="https://www.ubcorbit.com/" className="external-links">UBC Orbit</a> 🛰️ </strong>(Sept 2019 - Nov 2022)
                        <hr className="hr-separator"/>
                        <img
                            src={UBC_Orbit_2019}
                            className="float-left"
                            alt="UBC Orbit Satellite Design Team 2019"
                        />

                        <br/>

                        <span className="custom-card-text">
                            At university, I've had the opportunity to work on the ALEASAT project as part of the Command and Data-Handling (CDH) subteam. I worked on developing the onboard-computer telemetry functionality, intended to address
                            system failure risks and ensure critical orbital tasks were performed with deterministic execution.
                        </span>
                    </p>

                    <p className="custom-card-content">
                        <hr className="hr-separator"/>
                        <img
                            src={Optimus}
                            className="float-right"
                            alt="Tesla Bot Optimus in Front of a Cybertruck"
                        />

                        <br/>

                        <span className="custom-card-text">
                            A potential market that excites me is the emerging field of humanoid and autonomous robots! 🤖 I am keen to
                            closely follow new developments in this technological space!
                        </span>
                    </p>
                </div>

                <span className='tags bottom-tags'>&#125;</span>
            </div>
        </>
    )
}

export default Experiences
