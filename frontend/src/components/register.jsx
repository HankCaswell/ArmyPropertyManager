import { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Form, Button, Container, Row, Col } from 'react-bootstrap';

function Register() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [email, setEmail] = useState('');
    const [rank, setRank] = useState('');
    const [unit, setUnit] = useState('');
    // const [unitId, setUnitId] = useState('');
    const navigate = useNavigate();

    const handleRegister = async () => {
        try {
            const payload = {
                username,
                password,
                email,
                profile: {
                    rank,
                    unit
                },
            };
            console.log(payload)
            const response = await axios.post('http://localhost:8000/api/register/', payload);
            console.log('Registration successful', response.data);
            navigate('/login');  // Redirect to login page after successful registration
        } catch (error) {
            console.error('Registration failed:', error.response?.data);
        }
    };

    return (
        <Container className="mt-5">
            <Row className="justify-content-md-center">
                <Col xs={12} md={6}>
                    <h2>Register</h2>
                    <Form>
                        <Form.Group className="mb-3">
                            <Form.Label>Username</Form.Label>
                            <Form.Control
                                type="text"
                                placeholder="Enter username"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                            />
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label>Password</Form.Label>
                            <Form.Control
                                type="password"
                                placeholder="Password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label>Email address</Form.Label>
                            <Form.Control
                                type="email"
                                placeholder="Enter email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label>Rank</Form.Label>
                            <Form.Control
                                type="text"
                                placeholder="Enter rank"
                                value={rank}
                                onChange={(e) => setRank(e.target.value)}
                            />
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label>Unit</Form.Label>
                            <Form.Control
                                type="text"
                                placeholder="Enter unit name"
                                value={unit}
                                onChange={(e) => setUnit(e.target.value)}
                            />
                       </Form.Group>
                
                        <Button variant="primary" onClick={handleRegister}>
                            Register
                        </Button>
                    </Form>
                </Col>
            </Row>
        </Container>
    );
}

export default Register;
