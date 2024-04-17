import { useEffect, useState } from 'react';
import axios from 'axios';
import { Container, Table, Button, Form, Alert, Row, Col } from 'react-bootstrap';

function Dashboard() {
    const [units, setUnits] = useState([]);
    const [selectedUnitId, setSelectedUnitId] = useState('');
    const [selectedUnitName, setSelectedUnitName] = useState('');
    const [equipment, setEquipment] = useState([]);
    const [error, setError] = useState('');

    useEffect(() => {
        axios.get('http://localhost:8000/api/unit/all/')
            .then(response => {
                setUnits(response.data);
            })
            .catch(error => {
                setError('Failed to fetch units');
            });
    }, []);

    const fetchEquipment = () => {
        if (!selectedUnitId && !selectedUnitName) {
            setError('Please select a unit');
            return;
        }
        axios.get(`http://localhost:8000/api/equipment-summary/`, {
            params: { unit_id: selectedUnitId, unit_name: selectedUnitName }
        })
        .then(response => {
            setEquipment(response.data.equipment_summary);
            setError('');
        })
        .catch(error => {
            setError('Failed to fetch equipment');
        });
    };

    const handleCheckout = (equipmentId) => {
        const token = localStorage.getItem('token');
        axios.post('http://localhost:8000/api/add-to-cart/', {
            equipment_id: equipmentId,
            quantity: 1 
        }, {
            headers: {
                'Authorization': `Token ${token}`
            }
        })
        .then(response => {
            alert('Equipment checked out successfully');
            // Optionally refresh the list or update UI to reflect the checkout
            fetchEquipment();  // Refresh equipment list after checkout
        })
        .catch(error => setError('Failed to check out equipment'));
    };

    return (
        <Container className="mt-4">
            <h2>Equipment Dashboard</h2>
            {error && <Alert variant="danger">{error}</Alert>}
            <Form.Select aria-label="Select Unit" onChange={e => setSelectedUnitId(e.target.value)} value={selectedUnitId}>
                <option value="">Select Unit</option>
                {units.map(unit => (
                    <option key={unit.id} value={unit.id}>{unit.name}</option>
                ))}
            </Form.Select>
            <Button onClick={fetchEquipment} className="mt-2">Fetch Equipment</Button>
            <Table striped bordered hover className="mt-3">
                <thead>
                    <tr key ='key'>
                        <th>Name</th>
                        <th>NSN</th>
                        <th>Status</th>
                        <th>Quantity</th>
                        <th>Action</th>
                        
                    </tr>
                </thead>
                <tbody>
                    {equipment.map(item => (
                        <tr key={item.id}>
                            <td>{item.name}</td>
                            <td>{item.nsn}</td>
                            <td>{item.status}</td>
                            <td>{item.quantity}</td>
                            <td>
                                <Button variant="primary" onClick={() => handleCheckout(item.id)}>
                                    Check Out
                                </Button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </Table>
        </Container>
    );
}

export default Dashboard;