import { defineStore } from "pinia";
import { login as apiLogin, register as apiRegister } from "../api/auth";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem("token") || null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    setToken(token) {
      this.token = token;
      localStorage.setItem("token", token);
    },
    async login(email, password) {
      const { data } = await apiLogin(email, password);
      this.setToken(data.access_token);
    },
    async register(email, password) {
      const { data } = await apiRegister(email, password);
      this.setToken(data.access_token);
    },
    logout() {
      this.token = null;
      localStorage.removeItem("token");
    },
  },
});
