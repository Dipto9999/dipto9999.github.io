import { Link, NavLink } from 'react-router-dom';
import './index.scss';
import Muntakim_Insignia from '../../assets/images/Insignia.png';
import Muntakim_Cursive from '../../assets/images/Muntakim_Cursive.png';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHome, faBriefcase, faCode, faGamepad, faEnvelope, faCalendar } from '@fortawesome/free-solid-svg-icons';
import { faGithub, faLinkedin, faTwitter, faYoutube } from '@fortawesome/free-brands-svg-icons';

const navClass = ({ isActive }) => (isActive ? 'active' : undefined);

const Navbar = () => (
    <div className = "nav-bar">
        <Link className = "logo" to = "/">
            <img src = {Muntakim_Insignia} alt = "Muntakim Insignia" id = "insignia" />
            <img src = {Muntakim_Cursive} className = "sub-logo" alt = "Muntakim Subtitle" id = "signature" />
        </Link>

        <div className = "content-container">
            <nav className = "nav-links" aria-label = "Primary">
                <NavLink className = {navClass} to = "/" end id = "home-link" aria-label = "Home">
                    <FontAwesomeIcon icon = {faHome} className = "nav-icon" />
                    <span className = "nav-label">Home</span>
                </NavLink>
                <NavLink className = {navClass} to = "/experiences" id = "experiences-link" aria-label = "Work">
                    <FontAwesomeIcon icon = {faBriefcase} className = "nav-icon" />
                    <span className = "nav-label">Work</span>
                </NavLink>
                <NavLink className = {navClass} to = "/projects" id = "projects-link" aria-label = "Projects">
                    <FontAwesomeIcon icon = {faCode} className = "nav-icon" />
                    <span className = "nav-label">Projects</span>
                </NavLink>
                <NavLink className = {navClass} to = "/interests" id = "interests-link" aria-label = "Fun">
                    <FontAwesomeIcon icon = {faGamepad} className = "nav-icon" />
                    <span className = "nav-label">Fun</span>
                </NavLink>
            </nav>

            <ul className = "social-links">
                <li>
                    <a target = "_blank" rel = "noreferrer" href = "https://github.com/Dipto9999" className = "social-icons" aria-label = "GitHub">
                        <FontAwesomeIcon icon = {faGithub} color = "#FAFAFA" />
                    </a>
                </li>
                <li>
                    <a target = "_blank" rel = "noreferrer" href = "https://www.linkedin.com/in/muntakim-rahman/" className = "social-icons" aria-label = "LinkedIn">
                        <FontAwesomeIcon icon = {faLinkedin} color = "#0077B5" />
                    </a>
                </li>
                <li>
                    <a target = "_blank" rel = "noreferrer" href = "https://x.com/Dipto9999" className = "social-icons" aria-label = "X / Twitter">
                        <FontAwesomeIcon icon = {faTwitter} color = "#1DA1F2" />
                    </a>
                </li>
                <li>
                    <a target = "_blank" rel = "noreferrer" href = "https://www.youtube.com/channel/UCNF7p6gRuxE0dFYeDnzxoHw" className = "social-icons" aria-label = "YouTube">
                        <FontAwesomeIcon icon = {faYoutube} color = "#CC181E" />
                    </a>
                </li>
                <li>
                    <a target = "_blank" rel = "noreferrer" href = "mailto:dipto100@alum.ubc.ca" className = "social-icons" aria-label = "Email">
                        <FontAwesomeIcon icon = {faEnvelope} color = "#EDEDED" />
                    </a>
                </li>
                <li>
                    <a target = "_blank" rel = "noreferrer" href = "https://calendly.com/muntakim-rahman" className = "social-icons" aria-label = "Schedule a call">
                        <FontAwesomeIcon icon = {faCalendar} color = "#00A2FF" />
                    </a>
                </li>
            </ul>
        </div>
    </div>
);

export default Navbar;
