import './index.scss';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEnvelope, faCalendar } from '@fortawesome/free-solid-svg-icons';
import { faGithub, faLinkedin, faTwitter, faYoutube } from '@fortawesome/free-brands-svg-icons';

const Iconbar = () => (
    <span className="iconbar">
        <ul className="social-links">
            <li>
                <a target="_blank" rel="noreferrer" href="https://github.com/Dipto9999">
                    <FontAwesomeIcon icon={faGithub} color="#181717" className="social-icon"/>
                </a>
            </li>
            <li>
                <a target="_blank" rel="noreferrer" href="https://www.linkedin.com/in/muntakim-rahman/">
                    <FontAwesomeIcon icon={faLinkedin} color="#0077B5" className="social-icon" />
                </a>
            </li>
            <li>
                <a target="_blank" rel="noreferrer" href="https://x.com/Dipto9999">
                    <FontAwesomeIcon icon={faTwitter} color="#1DA1F2" className="social-icon" />
                </a>
            </li>
            <li>
                <a target="_blank" rel="noreferrer" href="https://www.youtube.com/channel/UCNF7p6gRuxE0dFYeDnzxoHw">
                    <FontAwesomeIcon icon={faYoutube} color="#FF0000" className="social-icon" />
                </a>
            </li>
            <li>
                <a target="_blank" rel="noreferrer" href="mailto:dipto100@alum.ubc.ca">
                    <FontAwesomeIcon icon={faEnvelope} color="#181717" className="social-icon" />
                </a>
            </li>
            <li>
                <a target="_blank" rel="noreferrer" href="https://calendly.com/muntakim-rahman">
                    <FontAwesomeIcon icon={faCalendar} color="#00A2FF" className="social-icon" />
                </a>
            </li>
        </ul>
    </span>
);

export default Iconbar;
