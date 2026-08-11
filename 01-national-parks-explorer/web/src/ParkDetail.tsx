import { useEffect, useState } from "react";
import type { ParkDetailModel } from "./models";

export default function ParkDetail({ url, id, handleBack }) {
  const [park, setPark] = useState<ParkDetailModel | undefined>(undefined);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let ignore = false;
    setLoading(true);

    async function getPark() {
      try {
        const res = await fetch(`${url}/parks/${id}`);
        if (!ignore) setPark(await res.json());
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    }
    
    getPark();

    return () => {
      ignore = true;
    }
  }, []);

  const activities = park?.activities.map((act, i) => <li key={i}>{act}</li>)

  function Park() {
    return (
      <>
        <h1>{park?.name}</h1>
        <p>{park?.tagline}</p>
        <p>Established: {park?.established}</p>
        <p>Acres: {park?.sizeAcres}</p>
        <p>{park?.description}</p>
        <ul>
          {activities}
        </ul>
      </>
    );
  }

  return (
    <>
      {loading && <h2>Loading...</h2>}
      {park && <Park />}
      <button type="button" onClick={handleBack}>Go Back</button>
    </>
  );
}