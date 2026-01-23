const Analysis = require('../models/Analysis');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

exports.analyzeImage = async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No image file uploaded' });
        }

        const imagePath = req.file.path;
        const absolutePath = path.resolve(imagePath);

        // 1. Create Pending Record
        const analysis = await Analysis.create({
            imageUrl: imagePath,
            status: 'PENDING',
        });

        // 2. Spawn Python Process
        // Note: Assuming 'python3' is in PATH. In virtualenv, might need full path.
        // For now we use the system python or venv python if activated.
        const pythonProcess = spawn('python3', ['../ai/inference.py', absolutePath], {
            cwd: __dirname // Run from controller dir, so we need valid relative path to ai/inference.py
        });

        // Actually, let's look for the script relative to project root for reliability
        const infoScriptPath = path.resolve(__dirname, '../../ai/inference.py');
        const venvPythonPath = path.resolve(__dirname, '../../ai/venv/bin/python'); // Try venv first

        const executable = fs.existsSync(venvPythonPath) ? venvPythonPath : 'python3';

        console.log(`Spawning AI process: ${executable} ${infoScriptPath} ${absolutePath}`);

        const child = spawn(executable, [infoScriptPath, absolutePath]);

        let pythonOutput = '';
        let pythonError = '';

        child.stdout.on('data', (data) => {
            pythonOutput += data.toString();
        });

        child.stderr.on('data', (data) => {
            pythonError += data.toString();
        });

        child.on('close', async (code) => {
            if (code !== 0) {
                console.error(`Python script exited with code ${code}`);
                console.error(`Stderr: ${pythonError}`);

                analysis.status = 'FAILED';
                analysis.rawResult = { error: pythonError };
                await analysis.save();

                // If we haven't responded yet (we might want to make this async/webhook based in real prod, 
                // but for this MVP we wait)
                return res.status(500).json({ error: 'AI processing failed', details: pythonError });
            }

            try {
                // Find the JSON line in the output
                const lines = pythonOutput.split('\n');
                let result = null;

                for (const line of lines) {
                    try {
                        const trimmedLine = line.trim();
                        if (trimmedLine.startsWith('{') && trimmedLine.endsWith('}')) {
                            const parsed = JSON.parse(trimmedLine);
                            if (parsed.status) { // basic validation
                                result = parsed;
                                break;
                            }
                        }
                    } catch (e) {
                        // Continue to next line
                    }
                }

                if (!result) {
                    // Fallback: try to find JSON substring if it's mixed with other text on the same line (rare but possible)
                    const jsonMatch = pythonOutput.match(/\{.*\}/);
                    if (jsonMatch) {
                        try {
                            result = JSON.parse(jsonMatch[0]);
                        } catch (e) {
                            // still failed
                        }
                    }
                }

                if (!result) {
                    throw new Error('No valid JSON found in Python output');
                }

                // 3. Update Record
                analysis.status = 'COMPLETED';
                analysis.totalGrains = result.total_grains;
                analysis.goodGrains = result.good_grains;
                analysis.brokenGrains = result.broken_grains;
                analysis.qualityScore = result.quality_score;
                analysis.rawResult = result;
                await analysis.save();

                res.json(analysis);
            } catch (parseError) {
                console.error('Failed to parse Python output:', pythonOutput);
                analysis.status = 'FAILED';
                analysis.rawResult = { error: 'Parse Error', output: pythonOutput };
                await analysis.save();
                res.status(500).json({ error: 'Invalid AI response' });
            }
        });

    } catch (error) {
        console.error('Controller Error:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
};

exports.getAllAnalyses = async (req, res) => {
    try {
        const analyses = await Analysis.findAll({ order: [['createdAt', 'DESC']] });
        res.json(analyses);
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch history' });
    }
};
