import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { Home } from './pages/Home';
import { Datasets } from './pages/Datasets';
import { Methods } from './pages/Methods';
import { StateOfTheArt } from './pages/StateOfTheArt';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="datasets" element={<Datasets />} />
          <Route path="methods" element={<Methods />} />
          <Route path="sota" element={<StateOfTheArt />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App
