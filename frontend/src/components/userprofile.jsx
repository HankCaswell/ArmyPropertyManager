import { useState, useEffect } from 'react'; 
import axios from 'axios';
import { Card, Container, ListGroup} from  'react-bootstrap'

function UserProfile() {
    const [profile, setProfile] = useState(null); 
    const [cartItems, setCartItems] = useState([]);

    useEffect(() => {
        const token = localStorage.getItem('token');
        const headers = { Authorization: `Token ${token}` };

        const fetchProfile = async () => {
            try {
                const response = await axios.get('http://localhost:8000/api/profile/', {headers});
                setProfile(response.data.profile);  // Adjust according to new response structure
                setCartItems(response.data.cart_items); // Set cart items
            } catch (error) {
                console.error('Failed to fetch profile:', error);
            }
        }; 
        fetchProfile();
    }, []);

    useEffect(() => {
        console.log('Cart items:', cartItems);
    }, [cartItems]);

    useEffect(() => {
        console.log('Profile:', profile);
    }, [profile]);


    const handleReturn = (transactionId) => {
        const token = localStorage.getItem('token');
        axios.post('http://localhost:8000/api/cart/return/', {
            transaction_id: transactionId, 
            user : profile.user.id
        }, {
            headers: {
                'Authorization': `Token ${token}`
            }
        })
        .then(response => {
            console.log('Equipment returned:', response.data);
            setCartItems(response.data.cart_items);
        })
        .catch(error => {
            console.error('Failed to return equipment:', error);
        });
    };
              
    return (
        <Container>
            {profile ? (
                <>
                    <Card>
                        <Card.Header>User Profile</Card.Header>
                        <ListGroup variant="flush">
                            <ListGroup.Item><strong>Name:</strong> {profile.user.username}</ListGroup.Item>
                            <ListGroup.Item><strong>Email:</strong> {profile.user.email}</ListGroup.Item>
                            <ListGroup.Item><strong>Rank:</strong> {profile.rank}</ListGroup.Item>
                            <ListGroup.Item><strong>Unit:</strong> {profile.unit ? profile.unit.name : 'Not Assigned'}</ListGroup.Item>
                        </ListGroup>
                    </Card>
                    <Card className="mt-3">
                        <Card.Header>Checked-Out Equipment</Card.Header>
                        <ListGroup variant="flush">
                            {cartItems.map(item => (
                                <ListGroup.Item key={item.transaction_id}>
                                    {item.name} - Status: {item.status}
                                    <button className="btn btn-danger btn-sm float-end" onClick={() => handleReturn(item.transaction_id)}>Return</button>
                                </ListGroup.Item>
                            ))}
                        </ListGroup>
                    </Card>
                </>
            ) : (
                <p>Loading...</p>
            )}
        </Container>
    );
}

export default UserProfile;