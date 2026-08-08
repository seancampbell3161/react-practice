export interface ParkSummary {
  id: string;
  name: string;
  state: string;
  tagline: string;
}

export interface ParkDetail extends ParkSummary {
  description: string;
  established: string;
  sizeAcres: number;
  activities: string[];
}