import express from 'express';
import cors from 'cors';
import morgan from 'morgan';
import 'express-async-errors';
import dotenv from 'dotenv';

import predictionsRouter from './routes/predictions.js';

// Future routes
// import fixturesRouter from './routes/fixtures.js';
// import playersRouter from './routes/players.js';

import errorHandler from './middleware/errorHandler.js';

dotenv.config();

const app = express();

const PORT = process.env.PORT || 5000;

// Middleware

app.use(cors({
origin:
process.env.CORS_ORIGIN
|| 'http://localhost:5173',
credentials: true
}));

app.use(morgan('combined'));

app.use(express.json());

app.use(express.urlencoded({
extended: true
}));

// Health Check

app.get(
'/api/health',
(req, res) => {


res.json({

  status: 'ok',

  timestamp:
    new Date()
    .toISOString(),

  uptime:
    process.uptime()
});


}
);

// Routes

app.use(
'/api/predictions',
predictionsRouter
);

// Future routes

// app.use(
//   '/api/fixtures',
//   fixturesRouter
// );

// app.use(
//   '/api/players',
//   playersRouter
// );

// 404

app.use((req, res) => {

res.status(404).json({


error:
  'Route not found',

path:
  req.path,

method:
  req.method


});
});

// Error Handler

app.use(errorHandler);

// Start Server

app.listen(
PORT,
() => {


console.log(
  `Backend server running on http://localhost:${PORT}`
);

console.log(
  `Environment: ${
    process.env.NODE_ENV
    || 'development'
  }`
);


}
);

export default app;
