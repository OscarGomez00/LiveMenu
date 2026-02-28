/**
 * Modal para crear o editar un plato.
 * Integra la carga de imagen (CU-05) con el formulario de plato (CU-04).
 */
import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import dishService from "../services/dishService";
import { X, Upload, ImagePlus } from "lucide-react";

export default function DishFormModal({ dish, onClose, onSaved }) {
    const isEditing = !!dish;

    const [form, setForm] = useState({
        nombre: "",
        descripcion: "",
        precio: "",
        precio_oferta: "",
        category_id: "",
        disponible: true,
        destacado: false,
        imagen_url: "",
    });

    const [imagePreview, setImagePreview] = useState(null);
    const [uploadingImage, setUploadingImage] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const fileInputRef = useRef(null);

    useEffect(() => {
        if (dish) {
            setForm({
                nombre: dish.nombre || "",
                descripcion: dish.descripcion || "",
                precio: dish.precio?.toString() || "",
                precio_oferta: dish.precio_oferta?.toString() || "",
                category_id: dish.category_id ? String(dish.category_id) : "",
                disponible: dish.disponible ?? true,
                destacado: dish.destacado ?? false,
                imagen_url: dish.imagen_url || "",
            });
            if (dish.imagen_url) setImagePreview(dish.imagen_url);
        }
    }, [dish]);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setForm((prev) => ({
            ...prev,
            [name]: type === "checkbox" ? checked : value,
        }));
    };

    // CU-05: subir imagen
    const handleImageSelect = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        setImagePreview(URL.createObjectURL(file));
        setError("");
        setUploadingImage(true);
        try {
            const url = await dishService.uploadDishImage(file);
            setForm((prev) => ({ ...prev, imagen_url: url }));
        } catch (err) {
            setError(err.response?.data?.detail || "Error al subir la imagen. Verifica formato/tamaño.");
            setImagePreview(dish?.imagen_url || null);
        } finally {
            setUploadingImage(false);
        }
    };

    // CU-04: guardar plato
    const handleSubmit = async (e) => {
        e.preventDefault();
        if (uploadingImage) return;

        if (!form.category_id.trim()) {
            setError("El ID de categoría es requerido.");
            return;
        }

        setError("");
        setLoading(true);

        try {
            const payload = {
                nombre: form.nombre.trim(),
                category_id: form.category_id.trim(),
                disponible: form.disponible,
                destacado: form.destacado,
            };
            if (form.descripcion) payload.descripcion = form.descripcion.trim();
            if (form.precio) payload.precio = parseFloat(form.precio);
            if (form.precio_oferta) payload.precio_oferta = parseFloat(form.precio_oferta);
            if (form.imagen_url) payload.imagen_url = form.imagen_url;

            let saved;
            if (isEditing) {
                saved = await dishService.updateDish(dish.id, payload);
            } else {
                if (!form.precio) {
                    setError("El precio es requerido.");
                    setLoading(false);
                    return;
                }
                saved = await dishService.createDish(payload);
            }

            onSaved(saved);
            onClose();
        } catch (err) {
            const detail = err.response?.data?.detail || "Error al guardar el plato.";
            setError(typeof detail === "string" ? detail : JSON.stringify(detail));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={(e) => e.target === e.currentTarget && onClose()}
        >
            <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
                {/* Header */}
                <div className="flex items-center justify-between p-6 pb-4 border-b border-gray-100">
                    <h2 className="text-lg font-semibold text-slate-900">
                        {isEditing ? "Editar Plato" : "Nuevo Plato"}
                    </h2>
                    <button
                        onClick={onClose}
                        className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
                    >
                        <X size={18} />
                    </button>
                </div>

                {/* Body */}
                <form onSubmit={handleSubmit} className="p-6 space-y-5">
                    {error && (
                        <Alert variant="destructive">
                            <AlertDescription>{error}</AlertDescription>
                        </Alert>
                    )}

                    {/* Imagen (CU-05) */}
                    <div className="space-y-2">
                        <Label>Imagen del plato</Label>
                        <div
                            onClick={() => !uploadingImage && fileInputRef.current?.click()}
                            className={`relative border-2 border-dashed rounded-xl flex flex-col items-center justify-center cursor-pointer transition-colors h-40 overflow-hidden
                ${uploadingImage ? "opacity-60 cursor-wait" : "hover:border-indigo-400 hover:bg-indigo-50/30 border-gray-200"}`}
                        >
                            {imagePreview ? (
                                <>
                                    <img src={imagePreview} alt="Vista previa" className="w-full h-full object-cover" />
                                    <div className="absolute inset-0 bg-black/30 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                                        <span className="text-white text-sm font-medium flex items-center gap-1">
                                            <Upload size={16} /> Cambiar imagen
                                        </span>
                                    </div>
                                </>
                            ) : (
                                <div className="flex flex-col items-center gap-2 text-gray-400">
                                    <ImagePlus size={32} />
                                    <span className="text-sm">Clic para subir imagen</span>
                                    <span className="text-xs">JPG, PNG o WebP · Máx. 2MB</span>
                                </div>
                            )}
                            {uploadingImage && (
                                <div className="absolute inset-0 flex items-center justify-center bg-white/70">
                                    <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
                                </div>
                            )}
                        </div>
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept="image/jpeg,image/png,image/webp"
                            className="hidden"
                            onChange={handleImageSelect}
                        />
                    </div>

                    {/* Nombre */}
                    <div className="space-y-1.5">
                        <Label htmlFor="nombre">
                            Nombre <span className="text-red-500">*</span>
                        </Label>
                        <Input
                            id="nombre"
                            name="nombre"
                            value={form.nombre}
                            onChange={handleChange}
                            placeholder="Ej: Bandeja Paisa"
                            required
                            autoFocus
                        />
                    </div>

                    {/* Descripción */}
                    <div className="space-y-1.5">
                        <Label htmlFor="descripcion">Descripción</Label>
                        <textarea
                            id="descripcion"
                            name="descripcion"
                            value={form.descripcion}
                            onChange={handleChange}
                            placeholder="Descripción breve del plato..."
                            maxLength={300}
                            rows={2}
                            className="w-full rounded-md border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                        />
                        <p className="text-xs text-gray-400 text-right">{form.descripcion.length}/300</p>
                    </div>

                    {/* Precios */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1.5">
                            <Label htmlFor="precio">
                                Precio <span className="text-red-500">*</span>
                            </Label>
                            <Input
                                id="precio"
                                name="precio"
                                type="number"
                                min="0"
                                step="0.01"
                                value={form.precio}
                                onChange={handleChange}
                                placeholder="0.00"
                                required={!isEditing}
                            />
                        </div>
                        <div className="space-y-1.5">
                            <Label htmlFor="precio_oferta">Precio oferta</Label>
                            <Input
                                id="precio_oferta"
                                name="precio_oferta"
                                type="number"
                                min="0"
                                step="0.01"
                                value={form.precio_oferta}
                                onChange={handleChange}
                                placeholder="0.00"
                            />
                        </div>
                    </div>

                    {/* Categoría */}
                    <div className="space-y-1.5">
                        <Label htmlFor="category_id">
                            ID de Categoría <span className="text-red-500">*</span>
                        </Label>
                        <Input
                            id="category_id"
                            name="category_id"
                            value={form.category_id}
                            onChange={handleChange}
                            placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                            required
                        />
                    </div>

                    {/* Toggles */}
                    <div className="flex gap-6">
                        <label className="flex items-center gap-2 cursor-pointer select-none">
                            <input
                                type="checkbox"
                                name="disponible"
                                checked={form.disponible}
                                onChange={handleChange}
                                className="w-4 h-4 rounded accent-indigo-600"
                            />
                            <span className="text-sm text-slate-700">Disponible</span>
                        </label>
                        <label className="flex items-center gap-2 cursor-pointer select-none">
                            <input
                                type="checkbox"
                                name="destacado"
                                checked={form.destacado}
                                onChange={handleChange}
                                className="w-4 h-4 rounded accent-indigo-600"
                            />
                            <span className="text-sm text-slate-700">Destacado</span>
                        </label>
                    </div>

                    {/* Acciones */}
                    <div className="flex justify-end gap-3 pt-2">
                        <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
                            Cancelar
                        </Button>
                        <Button type="submit" disabled={loading || uploadingImage}>
                            {loading ? "Guardando..." : isEditing ? "Guardar cambios" : "Crear plato"}
                        </Button>
                    </div>
                </form>
            </div>
        </div>
    );
}
