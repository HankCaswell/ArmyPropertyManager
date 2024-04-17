import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Login from './components/login';
import Register from './components/register';
import Dashboard from './components/dashboard';
import NavigationBar from './components/navbar';
import UserProfile from './components/userprofile';
import { Container } from 'react-bootstrap';


function App() {
  return (
    <Router>
      <NavigationBar />
      <Container style={{marginTop: '20px'}}>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/profile" element={<UserProfile />} />
      </Routes>
      </Container>
    </Router>
  );
}

export default App;