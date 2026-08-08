import { app } from './app';

const PORT = 4001;

app.listen(PORT, () => {
  console.log(`National Parks API listening on http://localhost:${PORT}`);
});
