const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Analysis = sequelize.define('Analysis', {
  id: {
    type: DataTypes.INTEGER,
    autoIncrement: true, // Use auto-incrementing integer as primary key
    primaryKey: true,
  },
  imageUrl: {
    type: DataTypes.STRING,
    allowNull: false,
  },
  status: {
    type: DataTypes.ENUM('PENDING', 'COMPLETED', 'FAILED'),
    defaultValue: 'PENDING',
  },
  totalGrains: {
    type: DataTypes.INTEGER,
    allowNull: true,
  },
  goodGrains: {
    type: DataTypes.INTEGER,
    allowNull: true,
  },
  brokenGrains: {
    type: DataTypes.INTEGER,
    allowNull: true,
  },
  qualityScore: {
    type: DataTypes.FLOAT, // Percentage of good grains
    allowNull: true,
  },
  rawResult: {
    type: DataTypes.JSONB, // Store the full JSON from Python
    allowNull: true,
  },
}, {
  timestamps: true,
});

module.exports = Analysis;
