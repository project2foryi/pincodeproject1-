import express from 'express';
import handler from './api/bot.js';

const app = express();
app.use(express.json());

app.all('/api/bot', (req, res) => handler(req, res));
app.get('/', (req, res) => res.status(200).send('Bot is active'));

const port = process.env.PORT || 3000;
app.listen(port, '0.0.0.0', () => {
  console.log(`Server listening on port ${port}`);
});
