import { useState } from 'react';

const Resume = () => {
    const [input, setPassword] = useState('');

    const password = 'Raccoons'; // Ignore Please

    const handleChange = (e) => {
        const current = e.target.value;

        setPassword(current);
        if (current === password) {
            // Download Resume
            window.location.href = 'https://drive.usercontent.google.com/uc?id=1yRhiuFHrN6sypAu8CX8y7U4O1krd0JJ2&export=download';
        }
    };

    return (
        <>
            <label htmlFor="password">Resume </label>
            <input
                type="password"
                id="password"
                value={input}
                onChange={handleChange}
                placeholder="Enter Password"
                style={{ marginRight: '5px' }}
                required
            />
            <br />
        </>
    );
}

export default Resume;
