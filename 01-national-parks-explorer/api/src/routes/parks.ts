import { Router } from 'express';
import { PARKS } from '../data';

export const parksRouter = Router();

parksRouter.get('/', (_req, res) => {
  const summaries = PARKS.map(({ id, name, state, tagline }) => ({
    id,
    name,
    state,
    tagline,
  }));
  res.json(summaries);
});
