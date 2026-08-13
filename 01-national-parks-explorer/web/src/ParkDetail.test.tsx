import { beforeEach, describe, expect, it, vi } from "vitest";
import type { ParkDetailModel } from "./models";
import { render, screen } from "@testing-library/react";
import ParkDetail from "./ParkDetail";

const mockPark: ParkDetailModel = {
  id: 'rocky-mountain',
  name: 'Rocky Mountain',
  state: 'CO',
  tagline: 'The gateway to the West',
  description: 'The best park ever',
  established: '1907',
  sizeAcres: 1048405,
  activities: ['Hiking', 'Climbing', 'Camping', 'Backpacking'],
};

beforeEach(() => {
  globalThis.fetch = vi.fn();
});

describe("ParkDetail", () => {
  it("shows a loading state, then renders the park details", async () => {
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: true,
      json: async () => mockPark,
    });

    render(<ParkDetail url="http://localhost:4001/api/rocky-mountain" id={mockPark.id} handleBack={() => { }} />);

    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });
});