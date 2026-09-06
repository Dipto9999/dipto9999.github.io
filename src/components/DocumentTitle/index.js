import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

const TITLES = {
    '/': 'Muntakim Rahman — Home',
    '/experiences': 'Muntakim Rahman — Work',
    '/projects': 'Muntakim Rahman — Projects',
    '/interests': 'Muntakim Rahman — Interests',
};

/** Sets document.title from the Current Route */
const DocumentTitle = () => {
    const { pathname } = useLocation();

    useEffect(() => {
        document.title = TITLES[pathname] || 'Muntakim Rahman';
    }, [pathname]);

    return null;
};

export default DocumentTitle;
