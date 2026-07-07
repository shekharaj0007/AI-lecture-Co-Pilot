import { create } from "zustand";

type PlayerState = {
  seekTo: number | null;
  currentTime: number;
  requestSeek: (seconds: number) => void;
  clearSeek: () => void;
  setCurrentTime: (seconds: number) => void;
};

export const usePlayerStore = create<PlayerState>((set) => ({
  seekTo: null,
  currentTime: 0,
  requestSeek: (seconds) => set({ seekTo: seconds }),
  clearSeek: () => set({ seekTo: null }),
  setCurrentTime: (seconds) => set({ currentTime: seconds }),
}));
