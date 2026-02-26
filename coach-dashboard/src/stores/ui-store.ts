import { create } from 'zustand';

type ViewMode = 'raw' | 'overlay' | 'skeleton';

interface UIStore {
  viewMode: ViewMode;
  setViewMode: (mode: ViewMode) => void;
  selectedPhase: number;
  setSelectedPhase: (phase: number) => void;
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
}

export const useUIStore = create<UIStore>((set) => ({
  viewMode: 'raw',
  setViewMode: (mode) => set({ viewMode: mode }),
  selectedPhase: 0,
  setSelectedPhase: (phase) => set({ selectedPhase: phase }),
  sidebarOpen: true,
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
}));
