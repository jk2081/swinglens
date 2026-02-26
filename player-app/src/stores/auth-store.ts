import * as SecureStore from 'expo-secure-store';
import { create } from 'zustand';

const TOKEN_KEY = 'swinglens_token';

interface AuthStore {
  token: string | null;
  isLoading: boolean;
  loadToken: () => Promise<void>;
  setToken: (token: string) => Promise<void>;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthStore>((set) => ({
  token: null,
  isLoading: true,
  loadToken: async () => {
    const token = await SecureStore.getItemAsync(TOKEN_KEY);
    set({ token, isLoading: false });
  },
  setToken: async (token) => {
    await SecureStore.setItemAsync(TOKEN_KEY, token);
    set({ token });
  },
  logout: async () => {
    await SecureStore.deleteItemAsync(TOKEN_KEY);
    set({ token: null });
  },
}));
