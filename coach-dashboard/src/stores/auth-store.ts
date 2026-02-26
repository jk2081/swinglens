import { create } from 'zustand';

interface AuthStore {
  token: string | null;
  setToken: (token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  token: localStorage.getItem('swinglens_token'),
  setToken: (token) => {
    localStorage.setItem('swinglens_token', token);
    set({ token });
  },
  logout: () => {
    localStorage.removeItem('swinglens_token');
    set({ token: null });
  },
}));
