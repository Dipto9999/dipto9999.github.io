import './App.scss';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Footer from './components/Footer';
import Home from './components/Home';
import Experiences from './components/Experiences';
import Projects from './components/Projects';

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="experiences" element={<Experiences />} />
          <Route path="projects" element={<Projects />} />
        </Route>
      </Routes>
      <Footer />
    </>
  )
}

export default App;
