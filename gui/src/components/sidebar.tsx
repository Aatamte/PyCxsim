import React from 'react';

const Sidebar: React.FC = () => {
    return (
        <div style={{ width: '200px', height: '100vh', backgroundColor: '#444', color: 'white', padding: '20px' }}>
            <ul style={{ listStyleType: 'none', padding: 0 }}>
                <li>Menu Item 1</li>
                <li>Menu Item 2</li>
                <li>Menu Item 3</li>
                {/* Add more menu items here */}
            </ul>
        </div>
    );
};

export default Sidebar;