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

parksRouter.get('/:id', (req, res) => {
  const park = PARKS.find((p) => p.id === req.params.id);

  if (!park) {
    res.status(404).json({ error: 'Park not found' });
    return;
  }

  res.json(park);
});
