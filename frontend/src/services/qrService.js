/**
 * Servicio para generación de QR.
 * Soporta tamaños (s, m, l, xl), formatos (png, svg) y colores personalizados.
 */
import api from "./api";

const qrService = {
  /**
   * Construir URL del endpoint QR con parámetros.
   * @param {Object} options
   * @param {string} [options.size="m"] - Tamaño: s, m, l, xl
   * @param {string} [options.format="png"] - Formato: png, svg
   * @param {string} [options.color="000000"] - Color HEX sin #
   * @param {string} [options.bgColor="FFFFFF"] - Color de fondo HEX sin #
   * @returns {string} URL con query params
   */
  getQrUrl({ size = "m", format = "png", color = "000000", bgColor = "FFFFFF" } = {}) {
    const baseURL = api.defaults.baseURL;
    const params = new URLSearchParams({ size, format, color, bg_color: bgColor });
    return `${baseURL}/admin/qr?${params.toString()}`;
  },

  /**
   * Descargar la imagen QR como blob.
   * @param {Object} options
   * @param {string} [options.size="m"]
   * @param {string} [options.format="png"]
   * @param {string} [options.color="000000"]
   * @param {string} [options.bgColor="FFFFFF"]
   * @returns {Promise<Blob>}
   */
  async downloadQr({ size = "m", format = "png", color = "000000", bgColor = "FFFFFF" } = {}) {
    const params = { size, format, color, bg_color: bgColor };
    const response = await api.get("/admin/qr", {
      params,
      responseType: "blob",
    });
    return response.data;
  },
};

export default qrService;
