import { useEffect, useState } from 'react';
import Loader from 'react-loaders'
import AnimatedLetters from "../AnimatedLetters"

import Muntakim_UBC from "../../assets/images/Muntakim_Headshot_2025.jpg"
import Tesla_Interns_2023 from "../../assets/images/Tesla_Interns_2023.jpg"
import Geotab_Volleyball_2022 from "../../assets/images/Geotab_Volleyball_2022.jpg"
import UBC_Orbit_2019 from "../../assets/images/UBC_Orbit_2019.jpg"
import Optimus from "../../assets/images/Optimus.jpg"

import './index.scss';
import Resume from '../Resume';

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
            <div className = "loader">
                <Loader type = "line-scale-pulse-out" />
            </div>

            <div className = 'container experiences-page'>
                <span className = 'tags top-tags'>func main() &#123;</span>

                <div className = 'text-zone'>
                    <h1 className = "supertitle">
                        <AnimatedLetters
                            letterClass = {letterClass}
                            strArray = {['E', 'x', 'p', 'e', 'r', 'i', 'e', 'n', 'c', 'e', 's']}
                            idx = {1}
                        />
                    </h1>

                    <div className = "custom-card-content intro-card">
                        <div className = "intro-text">
                            <span className = "custom-card-text">
                                ⚡ I'm currently pursuing a <strong>Bachelors in Electrical Engineering</strong> at the <strong><a href = "https://ece.ubc.ca/undergraduates/programs/electrical-engineering-program/" className = "external-links">University of British Columbia</a></strong>,
                                with an expected graduation in May 2026. My academic background also includes a <strong><a href = "https://extendedlearning.ubc.ca/programs-credentials/key-capabilities-data-science-certificate" className = "external-links">Certificate in Data Science</a></strong>,
                                where I enhanced my skills in data analytics, data visualization, & machine learning. ⚡
                            </span>

                            <br/><br/>
                            <Resume />
                        </div>

                        <div className = "intro-image">
                            <img
                                src = {Muntakim_UBC}
                                id = "Muntakim_UBC"
                                alt = "Muntakim Rahman : UBC Graduation Headshot"
                            />
                        </div>
                    </div>

                    <div className = "custom-card-content">
                        <strong>3x Application Engineering Intern @ <a href = "https://www.tesla.com/en_eu/megapack" className = "external-links">TESLA</a> </strong> 🔋<span className = "exp-details"> [Jan 2023] - [Jan 2024],&nbsp;(May - Aug) [2024, 2025]</span>
                        <hr className = "hr-separator"/>
                        <img
                            src = {Tesla_Interns_2023}
                            id = "Tesla_Interns_2023"
                            className = "float-left"
                            alt = "Tesla Deer Creek Interns Fall 2023"
                        />

                        <br/>

                        <span className = "custom-card-text">
                            I worked on performance testing for utility-scale energy storage systems. Working with partner engineering teams, I helped standardize
                            data management best practices for reporting KPI fleet metrics to stakeholder groups, including org leadership. I also worked with Asset Management teams
                            to prototype and productize a software application for accurately assessing project performance.
                            <br/><br/>
                            During my recent internships, I took on the scope to expose new telemetry data on customer interfaces and update supporting documentation.
                        </span>
                    </div>

                    <div className = "custom-card-content">
                        <strong>Product Coordinator Intern @ <a href = "https://www.geotab.com/" className = "external-links">GEOTAB</a> 🌐</strong> <span className = "exp-details">(Jan - Dec) [2022]</span>
                        <hr className = "hr-separator"/>
                        <img
                            src = {Geotab_Volleyball_2022}
                            id = "Geotab_Volleyball_2022"
                            className = "float-right"
                            alt = "GEOTAB Interns 2022"
                        />

                        <br/>

                        <span className = "custom-card-text">
                            I coordinated UX research initiatives to help develop vehicle telematics technology and software platforms. I presented product insights, from both
                            customer interviews and statistical analysis, to developers, product managers, and executives in informing roadmap decisions.
                            <br/><br/>
                            I also participated as a speaker for the Junior Student Summer Program, providing secondary school students an Introduction to Big Data.
                        </span>
                    </div>

                    <div className = "custom-card-content">
                        <strong>Firmware Developer @ <a href = "https://www.ubcorbit.com/" className = "external-links">UBC Orbit</a> 🛰️</strong> <span className = "exp-details">[Sept 2019] - [Nov 2022]</span>
                        <hr className = "hr-separator"/>
                        <img
                            src = {UBC_Orbit_2019}
                            className = "float-left"
                            alt = "UBC Orbit Satellite Design Team 2019"
                        />

                        <br/>

                        <span className = "custom-card-text">
                            I've had the opportunity to work on the ALEASAT project as part of the Command and Data-Handling (CDH) subteam. I worked on developing the onboard-computer telemetry, to address
                            system failure risks and ensure critical orbital tasks were performed with deterministic execution.
                        </span>
                    </div>

                    <div className = "custom-card-content">
                        <hr className = "hr-separator"/>
                        <img
                            src = {Optimus}
                            className = "float-right"
                            alt = "Tesla Bot Optimus in Front of a Cybertruck"
                        />

                        <br/>

                        <span className = "custom-card-text">
                            A potential market that excites me is the emerging field of humanoid and autonomous robots! 🤖 I am keen to
                            closely follow new developments in this technological space!
                        </span>
                    </div>
                </div>

                <span className = 'tags bottom-tags'>&#125;</span>
            </div>
        </>
    )
}

export default Experiences
