const express = require('express');
const sequelize = require('./config/database');
const app = express();
const port = process.env.PORT || 3000;

app.get('/', (req, res) => {
    res.send('Rice Quality System Backend is Running!');
});

async function startServer() {
    try {
        await sequelize.authenticate();
        console.log('Database connection has been established successfully.');

        app.listen(port, () => {
            console.log(`Server listening on port ${port}`);
        });
    } catch (error) {
        console.error('Unable to connect to the database:', error);
    }
}

startServer();
