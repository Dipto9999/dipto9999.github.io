import './index.scss';
import Sidebar from '../Sidebar';
import { Outlet } from 'react-router-dom';

const Layout = () => {
    return (
        <div className="App">
            <Sidebar/>
            <div className='page'>
                <span className='tags top-tags'>func main&#40;&#41; &#123;</span>
                <Outlet/>
                <span className='tags bottom-tags'>
                &#125;
                </span>
            </div>
        </div>
    )
}

export default Layout