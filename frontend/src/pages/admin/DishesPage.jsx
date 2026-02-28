/**
 * Página de gestión de platos del administrador (CU-04 y CU-05).
 * CRUD completo: listar, crear, editar, eliminar y toggle de disponibilidad.
 */
import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import dishService from "../../services/dishService";
import DishFormModal from "../../components/DishFormModal";
import { Plus, Pencil, Trash2, ToggleLeft, ToggleRight, Star, ImagePlus } from "lucide-react";

export default function DishesPage() {
    const [dishes, setDishes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    // Modal state
    const [modalOpen, setModalOpen] = useState(false);
    const [editingDish, setEditingDish] = useState(null);

    // Confirmación de borrado
    const [deletingId, setDeletingId] = useState(null);

    const fetchDishes = useCallback(async () => {
        setLoading(true);
        setError("");
        try {
            const data = await dishService.getDishes();
            setDishes(data.dishes ?? data);
        } catch {
            setError("Error al cargar los platos. Verifica que el backend esté funcionando.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchDishes();
    }, [fetchDishes]);

    const showSuccess = (msg) => {
        setSuccess(msg);
        setTimeout(() => setSuccess(""), 3000);
    };

    const handleOpenCreate = () => {
        setEditingDish(null);
        setModalOpen(true);
    };

    const handleOpenEdit = (dish) => {
        setEditingDish(dish);
        setModalOpen(true);
    };

    const handleSaved = (savedDish) => {
        setDishes((prev) => {
            const exists = prev.find((d) => d.id === savedDish.id);
            if (exists) return prev.map((d) => (d.id === savedDish.id ? savedDish : d));
            return [savedDish, ...prev];
        });
        showSuccess(editingDish ? "Plato actualizado correctamente." : "Plato creado correctamente.");
    };

    const handleToggle = async (dish) => {
        try {
            const updated = await dishService.toggleAvailability(dish.id);
            setDishes((prev) => prev.map((d) => (d.id === updated.id ? updated : d)));
        } catch {
            setError("No se pudo cambiar la disponibilidad del plato.");
        }
    };

    const handleDeleteConfirm = async (id) => {
        try {
            await dishService.deleteDish(id);
            setDishes((prev) => prev.filter((d) => d.id !== id));
            showSuccess("Plato eliminado correctamente.");
        } catch {
            setError("No se pudo eliminar el plato.");
        } finally {
            setDeletingId(null);
        }
    };

    return (
        <div className="py-4">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 mb-1">Gestión de Platos</h1>
                    <p className="text-gray-500">Crea, edita y administra los platos del menú.</p>
                </div>
                <Button onClick={handleOpenCreate} className="flex items-center gap-2">
                    <Plus size={18} />
                    Nuevo Plato
                </Button>
            </div>

            {/* Alertas */}
            {error && (
                <Alert variant="destructive" className="mb-4">
                    <AlertDescription>{error}</AlertDescription>
                </Alert>
            )}
            {success && (
                <div className="mb-4 bg-green-50 text-green-700 border border-green-200 px-4 py-3 rounded-lg text-sm">
                    {success}
                </div>
            )}

            {/* Contenido */}
            {loading ? (
                <div className="flex items-center justify-center py-20 text-gray-400">
                    <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mr-3" />
                    Cargando platos...
                </div>
            ) : dishes.length === 0 ? (
                <div className="bg-gray-50 p-12 rounded-xl text-center text-gray-500">
                    <ImagePlus size={40} className="mx-auto mb-3 text-gray-300" />
                    <p className="font-medium">No hay platos registrados aún.</p>
                    <p className="text-sm text-gray-400 mt-1">Haz clic en "Nuevo Plato" para comenzar.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                    {dishes.map((dish) => (
                        <div
                            key={dish.id}
                            className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden flex flex-col"
                        >
                            {/* Imagen */}
                            {dish.imagen_url ? (
                                <img
                                    src={dish.imagen_url}
                                    alt={dish.nombre}
                                    className="w-full h-40 object-cover"
                                />
                            ) : (
                                <div className="w-full h-40 bg-gray-100 flex items-center justify-center text-gray-300">
                                    <ImagePlus size={36} />
                                </div>
                            )}

                            {/* Info */}
                            <div className="p-4 flex flex-col flex-1">
                                <div className="flex items-start justify-between gap-2 mb-1">
                                    <h3 className="font-semibold text-slate-900 leading-tight">{dish.nombre}</h3>
                                    {dish.destacado && (
                                        <Star size={15} className="text-yellow-400 fill-yellow-400 shrink-0 mt-0.5" />
                                    )}
                                </div>

                                {dish.descripcion && (
                                    <p className="text-gray-400 text-xs mb-2 line-clamp-2">{dish.descripcion}</p>
                                )}

                                <div className="flex items-center gap-2 mt-auto">
                                    <span className="text-indigo-600 font-semibold text-sm">
                                        ${parseFloat(dish.precio).toFixed(2)}
                                    </span>
                                    {dish.precio_oferta && (
                                        <span className="text-gray-400 line-through text-xs">
                                            ${parseFloat(dish.precio_oferta).toFixed(2)}
                                        </span>
                                    )}
                                </div>

                                {/* Acciones */}
                                <div className="flex items-center gap-2 mt-4 pt-3 border-t border-gray-100">
                                    {/* Toggle disponibilidad */}
                                    <button
                                        onClick={() => handleToggle(dish)}
                                        title={dish.disponible ? "Marcar como no disponible" : "Marcar como disponible"}
                                        className={`flex items-center gap-1 text-xs px-2 py-1 rounded-md transition-colors ${dish.disponible
                                                ? "bg-green-50 text-green-700 hover:bg-green-100"
                                                : "bg-gray-100 text-gray-500 hover:bg-gray-200"
                                            }`}
                                    >
                                        {dish.disponible ? (
                                            <ToggleRight size={14} />
                                        ) : (
                                            <ToggleLeft size={14} />
                                        )}
                                        {dish.disponible ? "Disponible" : "No disponible"}
                                    </button>

                                    <div className="flex gap-1 ml-auto">
                                        {/* Editar */}
                                        <button
                                            onClick={() => handleOpenEdit(dish)}
                                            title="Editar plato"
                                            className="p-1.5 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-md transition-colors"
                                        >
                                            <Pencil size={15} />
                                        </button>

                                        {/* Eliminar */}
                                        {deletingId === dish.id ? (
                                            <div className="flex items-center gap-1">
                                                <button
                                                    onClick={() => handleDeleteConfirm(dish.id)}
                                                    className="text-xs px-2 py-1 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                                                >
                                                    Confirmar
                                                </button>
                                                <button
                                                    onClick={() => setDeletingId(null)}
                                                    className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded-md hover:bg-gray-200 transition-colors"
                                                >
                                                    Cancelar
                                                </button>
                                            </div>
                                        ) : (
                                            <button
                                                onClick={() => setDeletingId(dish.id)}
                                                title="Eliminar plato"
                                                className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors"
                                            >
                                                <Trash2 size={15} />
                                            </button>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Modal crear/editar */}
            {modalOpen && (
                <DishFormModal
                    dish={editingDish}
                    onClose={() => setModalOpen(false)}
                    onSaved={handleSaved}
                />
            )}
        </div>
    );
}
