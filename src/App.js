import './App.scss';
import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Footer from './components/Footer';
import Home from './components/Home';
import Experiences from './components/Experiences';
import Projects from './components/Projects';
import Interests from './components/Interests';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Home />} />
            <Route path="experiences" element={<Experiences />} />
            <Route path="projects" element={<Projects />} />
            <Route path="interests" element={<Interests />} />
          </Route>
        </Routes>

        <Footer />
      </div>
    </Router>
  );
}

export default App;
