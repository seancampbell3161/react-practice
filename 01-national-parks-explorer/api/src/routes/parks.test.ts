import { describe, it, expect } from 'vitest';
import request from 'supertest';
import { app } from '../app';

describe('GET /api/parks', () => {
  it('returns a list of park summaries', async () => {
    const res = await request(app).get('/api/parks');

    expect(res.status).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
    expect(res.body.length).toBeGreaterThanOrEqual(10);
    expect(res.body[0]).toMatchObject({
      id: expect.any(String),
      name: expect.any(String),
      state: expect.any(String),
      tagline: expect.any(String),
    });
    expect(res.body[0]).not.toHaveProperty('description');
  });
});

describe('GET /api/parks/:id', () => {
  it('returns full detail for a known park', async () => {
    const res = await request(app).get('/api/parks/yellowstone');

    expect(res.status).toBe(200);
    expect(res.body).toMatchObject({
      id: 'yellowstone',
      name: expect.any(String),
      description: expect.any(String),
      activities: expect.any(Array),
    });
  });

  it('returns 404 for an unknown park', async () => {
    const res = await request(app).get('/api/parks/not-a-real-park');

    expect(res.status).toBe(404);
    expect(res.body).toMatchObject({ error: expect.any(String) });
  });
});
