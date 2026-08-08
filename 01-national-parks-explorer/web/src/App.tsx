import ParkList from "./ParkList";

function App() {
  const url = 'http://localhost:4001/api';
  
  return (
    <main>
      <h1>National Parks Explorer</h1>
      <ParkList url={url} />
    </main>
  );
}

export default App;
