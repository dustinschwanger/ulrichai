const express = require('express');
const path = require('path');
const app = express();

// Serve static files from the React build
app.use(express.static(path.join(__dirname, 'build')));

// Handle all requests by returning the React app
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Frontend server running on port ${PORT}`);
});