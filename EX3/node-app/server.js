const express = require("express");
const app = express();

// Route racine
app.get("/", (req, res) => {
  res.send("<h1>Bienvenue sur Node-App Dockerisée</h1>");
});

// Route health
app.get("/api/health", (req, res) => {
  res.json({ status: "UP" });
});

// Route info
app.get("/api/info", (req, res) => {
  res.json({
    node_version: process.version,
    platform: process.platform,
    memory: process.memoryUsage(),
  });
});

// Route time
app.get("/api/time", (req, res) => {
  res.json({ time: new Date().toISOString() });
});

// Port d'écoute
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
