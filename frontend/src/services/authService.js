/**
 * Servicio de autenticación.
 * Maneja registro, login, logout y obtención de perfil.
 */
import api from "./api";

const authService = {
  /**
   * Registrar un nuevo usuario.
   * @param {string} email
   * @param {string} password
   * @returns {Promise<{access_token: string, token_type: string}>}
   */
  async register(email, password) {
    const response = await api.post("/auth/register", { email, password });
    const { access_token } = response.data;
    localStorage.setItem("access_token", access_token);
    return response.data;
  },

  /**
   * Iniciar sesión.
   * @param {string} email
   * @param {string} password
   * @returns {Promise<{access_token: string, token_type: string}>}
   */
  async login(email, password) {
    const response = await api.post("/auth/login", { email, password });
    const { access_token } = response.data;
    localStorage.setItem("access_token", access_token);
    return response.data;
  },

  /**
   * Cerrar sesión (notifica al backend y elimina token local).
   */
  async logout() {
    try {
      await api.post("/auth/logout");
    } catch {
      // Si falla el backend, igual limpiamos el token local
    }
    localStorage.removeItem("access_token");
  },

  /**
   * Obtener perfil del usuario autenticado.
   * @returns {Promise<{id: string, email: string}>}
   */
  async getMe() {
    const response = await api.get("/auth/me");
    return response.data;
  },

  /**
   * Verificar si hay un token guardado.
   * @returns {boolean}
   */
  isAuthenticated() {
    return !!localStorage.getItem("access_token");
  },

  /**
   * Obtener el token guardado.
   * @returns {string|null}
   */
  getToken() {
    return localStorage.getItem("access_token");
  },
};

export default authService;
