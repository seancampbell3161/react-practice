import express from 'express';
import cors from 'cors';
import { parksRouter } from './routes/parks';

export const app = express();

app.use(cors());
app.use(express.json());
app.use('/api/parks', parksRouter);
