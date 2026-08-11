import { useEffect, useState } from "react";
import ParkDetail from "./ParkDetail";
import type { ParkSummary } from "./models";

export default function ParkList({ url }) {
  const [parks, setParks] = useState<ParkSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [currentPark, setCurrentPark] = useState('');
  const [favorites, setFavorites] = useState<Record<string, boolean>>({});
  const [userInput, setUserInput] = useState<string>('');
  
  useEffect(() => {
    let ignore = false;
    setLoading(true);

    async function fetchParks() {
      try {
        const res = await fetch(url + '/parks');
        if (!ignore) {
          const parks = await res.json();
          setParks(parks);
          getFavorites(parks);
        }
      } catch (error) {
        setErrorMsg(error.message)
      } finally {
        setLoading(false);
      }
    }

    fetchParks();

    return () => {
      ignore = true;
    }
  }, []);

  function getFavorites(p: ParkSummary[]): void {
    const faveMap: Record<string, boolean> = {};
    
    p.forEach(p => {
      const isFavorite = localStorage.getItem(p.id);
      if (isFavorite) {
        faveMap[p.id] = isFavorite === 'true';
      }
    });
    setFavorites(faveMap);
  }

  const filteredParks = parks.filter((p: ParkSummary) => p.name.toLowerCase().includes(userInput.toLowerCase()));

  const updateFavorite = (key: string) => {
    const value = localStorage.getItem(key) === 'true';
    const updatedValue = !value;

    localStorage.setItem(key, updatedValue.toString());
    const faves = { ...favorites }
    faves[key] = updatedValue;
    
    setFavorites(faves);
  }
  
  const resetPark = () => { setCurrentPark('') }

  const handleInput = (e) => {
    const searchString: string = e.target.value;
    
    setUserInput(searchString);
  }
  
  return (
    <>
      {loading && <h2>Loading...</h2>}
      {errorMsg && <p className={'error-text'}>{errorMsg}</p>}
      <input type="text" onChange={handleInput} value={userInput} />
      {currentPark ? <ParkDetail url={url} id={currentPark} handleBack={resetPark} /> :
        <ul>
          {filteredParks.map((p: ParkSummary) => {
            const isFavorite = favorites[p.id] ?? localStorage.getItem(p.id) === "true";
            return (
              <li key={p.id} className="margin-bottom">
                <span
                  className="clickable"
                  onClick={() => setCurrentPark(p.id)}
                >
                  {`${p.name} - ${p.state}`}
                </span>
                <input
                  id={"checkbox-" + p.id}
                  type="checkbox"
                  checked={isFavorite}
                  onChange={() => updateFavorite(p.id)}
                />
              </li>
            );
          })}
        </ul>
      }
    </>
  );
}