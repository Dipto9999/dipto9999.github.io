import Navbar from '../Navbar';
import Iconbar from '../Iconbar';
import { Outlet } from 'react-router-dom';
import './index.scss';

const Layout = () => {
    return (
        <div className="App">
            <Navbar />

            <div className="main-content">
                <Outlet />
            </div>

            <Iconbar />
        </div>
    );
}

export default Layout;
