import { useEffect, useState } from "react";

export default function ParkList({ url }) {
  const [parks, setParks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  
  useEffect(() => {
    let ignore = false;
    setLoading(true);

    async function fetchParks() {
      try {
        const res = await fetch(url + '/parks');
        if (!ignore) setParks(await res.json());
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

  const parkList = parks.map(p => <li key={p.id} className={'clickable margin-bottom'}>{`${p.name} - ${p.state}`}</li>);
  
  return (
    <>
      {loading && <h2>Loading...</h2>}
      {errorMsg && <p className={'error-text'}>{errorMsg}</p>}
      <ul>
        {parkList}
      </ul>
    </>
  );
}