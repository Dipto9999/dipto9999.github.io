import { Link, NavLink } from 'react-router-dom';
import './index.scss';
import Muntakim_Insignia from '../../assets/images/Insignia.png';
import Muntakim_Cursive from '../../assets/images/Muntakim_Cursive.png';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHome, faBriefcase, faCode, faGamepad, faEnvelope, faCalendar } from '@fortawesome/free-solid-svg-icons';
import { faGithub, faLinkedin, faTwitter, faYoutube } from '@fortawesome/free-brands-svg-icons';

const Navbar = () => (
    <div className="nav-bar">
        <Link className="logo" to="/">
            <img src={Muntakim_Insignia} alt="Muntakim Insignia" id="insignia" />
            <img src={Muntakim_Cursive} className="sub-logo" alt="Muntakim Subtitle" id="signature" />
        </Link>
        <div className="content-container">
            <nav className="nav-links">
                <NavLink exact="true" activeclassname="active" to="/">
                    <FontAwesomeIcon icon={faHome} color="#4D4D4E" />
                </NavLink>
                <NavLink exact="true" activeclassname="active" className="experiences-link" to="/experiences">
                    <FontAwesomeIcon icon={faBriefcase} color="#4D4D4E" />
                </NavLink>
                <NavLink exact="true" activeclassname="active" className="projects-link" to="/projects">
                    <FontAwesomeIcon icon={faCode} color="#4D4D4E" />
                </NavLink>
                <NavLink exact="true" activeclassname="active" className="interests-link" to="/interests">
                    <FontAwesomeIcon icon={faGamepad} color="#4D4D4E" />
                </NavLink>
            </nav>
            <ul className="social-links">
                <li>
                    <a target="_blank" rel="noreferrer" href="https://github.com/Dipto9999" className="social-icons">
                        <FontAwesomeIcon icon={faGithub} color="#FAFAFA" />
                    </a>
                </li>
                <li>
                    <a target="_blank" rel="noreferrer" href="https://www.linkedin.com/in/muntakim-rahman/" className="social-icons">
                        <FontAwesomeIcon icon={faLinkedin} color="#0077B5" />
                    </a>
                </li>
                <li>
                    <a target="_blank" rel="noreferrer" href="https://x.com/Dipto9999" className="social-icons">
                        <FontAwesomeIcon icon={faTwitter} color="#1DA1F2" />
                    </a>
                </li>
                <li>
                    <a target="_blank" rel="noreferrer" href="https://www.youtube.com/channel/UCNF7p6gRuxE0dFYeDnzxoHw" className="social-icons">
                        <FontAwesomeIcon icon={faYoutube} color="#CC181E" />
                    </a>
                </li>
                <li>
                    <a target="_blank" rel="noreferrer" href="mailto:dipto100@alum.ubc.ca" className="social-icons">
                        <FontAwesomeIcon icon={faEnvelope} color="#EDEDED" />
                    </a>
                </li>
                <li>
                    <a target="_blank" rel="noreferrer" href="https://calendly.com/muntakim-rahman" className="social-icons">
                        <FontAwesomeIcon icon={faCalendar} color="#00A2FF" />
                    </a>
                </li>
                <li>
                    <span id="icon-padding"><br/></span>
                </li>
            </ul>
        </div>
    </div>
);

export default Navbar;
