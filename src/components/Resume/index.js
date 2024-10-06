import { useState } from 'react';

const Resume = () => {
    const [input, setPassword] = useState('');
    const [showCheckmark, setShowCheckmark] = useState(false);

    const password = 'Raccoons'; // Ignore Please

    const handleChange = (e) => {
        const current = e.target.value;

        setPassword(current);

        if (current === password) {
            // Show Checkmark
            setShowCheckmark(true);

            // Download Resume
            window.location.href = 'https://drive.usercontent.google.com/uc?id=1yRhiuFHrN6sypAu8CX8y7U4O1krd0JJ2&export=download';

            // Remove Checkmark After 5 s.
            setTimeout(() => {
                setShowCheckmark(false);
            }, 5000);
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
            {showCheckmark && (
                <span>✅</span>
            )}
            <br />
        </>
    );
}

export default Resume;
