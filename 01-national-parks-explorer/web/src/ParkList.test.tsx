import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import ParkList from "./ParkList";

const mockParks = [
  { id: "yellowstone", name: "Yellowstone", state: "WY, MT, ID", tagline: "America's first national park" },
  { id: "yosemite", name: "Yosemite", state: "CA", tagline: "Granite cliffs and waterfalls" },
];

beforeEach(() => {
  // Replace the real fetch with a mock so the test never hits the network.
  // Each test below configures what it resolves to.
  globalThis.fetch = vi.fn();
});

describe("ParkList", () => {
  it("shows a loading state, then renders the fetched parks", async () => {
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: true,
      json: async () => mockParks,
    });

    render(<ParkList url="http://localhost:4001/api" />);

    // The fetch promise hasn't resolved yet on this first render, so the
    // loading indicator should already be on screen.
    expect(screen.getByText("Loading...")).toBeInTheDocument();

    // findByText is async: it retries until the text appears (or times out),
    // which happens once the mocked fetch resolves and React re-renders.
    expect(await screen.findByText("Yellowstone - WY, MT, ID")).toBeInTheDocument();
    expect(screen.getByText("Yosemite - CA")).toBeInTheDocument();

    // And now that loading is done, the indicator should be gone.
    expect(screen.queryByText("Loading...")).not.toBeInTheDocument();
  });

  it("shows an error message when the fetch fails", async () => {
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: false,
      json: async () => ({ error: "Something went wrong" }),
    });

    render(<ParkList url="http://localhost:4001/api" />);

    expect(await screen.findByText(/failed to load parks/i)).toBeInTheDocument();
  });
});
