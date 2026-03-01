/**
 * Configuración base de Axios para comunicación con el backend.
 */
import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor: adjuntar token JWT a cada request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor: manejar errores 401 (token expirado)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

/**
 * Servicios para el CU-02: Gestión de Restaurante
 */
export const restaurantService = {
  // Obtener datos del restaurante del usuario autenticado
  get: () => api.get("/admin/restaurant"),
  // Crear restaurante
  create: (data) => api.post("/admin/restaurant", data),
  // Actualizar restaurante
  update: (data) => api.put("/admin/restaurant", data),
  // Eliminar restaurante
  delete: () => api.delete("/admin/restaurant"),
};

/**
 * Servicios para el CU-03: Gestión de Categorías
 */
export const categoryService = {
  // Listar todas las categorías (Requisito 2 del flujo principal)
  getAll: () => api.get("/admin/categories"),
  // Crear nueva categoría (Requisito 3.1)
  create: (data) => api.post("/admin/categories", data),
  // Editar categoría (Requisito 3.2)
  update: (id, data) => api.put(`/admin/categories/${id}`, data),
  // Eliminar categoría (Requisito 3.3)
  delete: (id) => api.delete(`/admin/categories/${id}`),
  // Reordenar categorías
  reorder: (orderedIds) => api.patch("/admin/categories/reorder", { ordered_ids: orderedIds }),
};

export default api;
