// src/components/Layout/index.js

import './index.scss';
import Sidebar from '../Sidebar';
import { Outlet } from 'react-router-dom';

const Layout = () => {
    return (
        <div className="App">
            <Sidebar />
            <div className="main-content">
                <Outlet />
            </div>
        </div>
    );
}

export default Layout;
