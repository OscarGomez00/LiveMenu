/**
 * Servicio para gestión de platos (CU-04), carga de imágenes (CU-05) y categorías.
 */
import api from "./api";

const dishService = {
  // ── Categorías ───────────────────────────────────────────────────────────

  /** Listar todas las categorías */
  async getCategories() {
    const response = await api.get("/admin/categories");
    return response.data;
  },

  /** Crear una nueva categoría */
  async createCategory(nombre) {
    const response = await api.post("/admin/categories", { nombre });
    return response.data;
  },

  // ── Platos ───────────────────────────────────────────────────────────────

  /**
   * Listar platos con filtros opcionales.
   * @param {Object} filters - { category_id, disponible, destacado, skip, limit }
   */
  async getDishes(filters = {}) {
    const params = {};
    if (filters.category_id) params.category_id = filters.category_id;
    if (filters.disponible !== undefined) params.disponible = filters.disponible;
    if (filters.destacado !== undefined) params.destacado = filters.destacado;
    if (filters.skip !== undefined) params.skip = filters.skip;
    if (filters.limit !== undefined) params.limit = filters.limit;

    const response = await api.get("/admin/dishes", { params });
    return response.data;
  },

  /**
   * Obtener un plato por ID.
   * @param {string} id - UUID del plato
   */
  async getDish(id) {
    const response = await api.get(`/admin/dishes/${id}`);
    return response.data;
  },

  /**
   * Crear un nuevo plato.
   * @param {Object} dishData - { nombre, precio, category_id, descripcion?, precio_oferta?, imagen_url?, disponible?, destacado?, etiquetas?, posicion? }
   */
  async createDish(dishData) {
    const response = await api.post("/admin/dishes", dishData);
    return response.data;
  },

  /**
   * Actualizar un plato existente.
   * @param {string} id - UUID del plato
   * @param {Object} dishData - Campos a actualizar
   */
  async updateDish(id, dishData) {
    const response = await api.put(`/admin/dishes/${id}`, dishData);
    return response.data;
  },

  /**
   * Eliminar un plato (soft delete).
   * @param {string} id - UUID del plato
   */
  async deleteDish(id) {
    const response = await api.delete(`/admin/dishes/${id}`);
    return response.data;
  },

  /**
   * Alternar disponibilidad de un plato.
   * @param {string} id - UUID del plato
   */
  async toggleAvailability(id) {
    const response = await api.patch(`/admin/dishes/${id}/availability`);
    return response.data;
  },

  /**
   * Subir imagen de un plato (CU-05).
   * @param {File} file - Archivo de imagen (jpg, png, webp)
   * @returns {string} URL relativa de la imagen guardada
   */
  async uploadDishImage(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post("/upload/dish", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data.url;
  },
};

export default dishService;
