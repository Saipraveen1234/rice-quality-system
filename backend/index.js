const express = require('express');
const sequelize = require('./config/database');
const app = express();
const port = process.env.PORT || 3000;

const cors = require('cors');
const analysisRoutes = require('./routes/analysis');

app.use(cors());
app.use(express.json());
// Serve uploaded images statically so frontend can display them
app.use('/uploads', express.static('uploads'));

app.use('/api', analysisRoutes);

app.get('/', (req, res) => {
    res.send('Rice Quality System Backend is Running!');
});

async function startServer() {
    try {
        await sequelize.authenticate();
        console.log('Database connection has been established successfully.');

        // Sync models
        const Analysis = require('./models/Analysis');
        await sequelize.sync({ alter: true });
        console.log('Database models synced.');

        app.listen(port, () => {
            console.log(`Server listening on port ${port}`);
        });
    } catch (error) {
        console.error('Unable to connect to the database:', error);
    }
}

startServer();
