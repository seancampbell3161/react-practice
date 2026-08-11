export interface ParkSummary {
  id: string;
  name: string;
  state: string;
  tagline: string;
}

export interface ParkDetailModel extends ParkSummary {
  description: string;
  established: string;
  sizeAcres: number;
  activities: string[];
}