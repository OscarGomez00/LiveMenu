/**
 * Dashboard del administrador.
 * Muestra restaurantes y permite generar QR.
 * Incluye acceso rápido a gestión de platos (CU-04).
 */
import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import api from "../../services/api";
import QrGenerator from "../../components/QrGenerator";
import { UtensilsCrossed, LayoutList } from "lucide-react";

export default function DashboardPage() {
  const { user } = useAuth();
  const [restaurants, setRestaurants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchRestaurants = async () => {
      try {
        const response = await api.get("/admin/restaurant");
        // Backend returns a single restaurant object; wrap in array for the UI
        setRestaurants(response.data ? [response.data] : []);
      } catch (err) {
        if (err.response?.status === 404 || err.response?.status === 405) {
          setRestaurants([]);
        } else {
          setError("Error al cargar restaurantes");
        }
      } finally {
        setLoading(false);
      }
    };
    fetchRestaurants();
  }, []);

  return (
    <div className="py-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-1">Dashboard</h1>
        <p className="text-gray-500">
          Bienvenido, <strong>{user?.email}</strong>
        </p>
      </div>

      {/* Acciones rápidas */}
      <section className="mb-8">
        <h2 className="text-xl font-semibold text-slate-900 mb-4">Acciones rápidas</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <Link
            to="/admin/dishes"
            className="flex items-center gap-4 bg-white border border-gray-100 rounded-xl p-5 shadow-sm hover:shadow-md hover:border-indigo-200 transition-all no-underline group"
          >
            <div className="bg-indigo-50 p-3 rounded-lg group-hover:bg-indigo-100 transition-colors">
              <UtensilsCrossed size={22} className="text-indigo-600" />
            </div>
            <div>
              <p className="font-semibold text-slate-900 text-sm">Gestionar Platos</p>
              <p className="text-gray-400 text-xs">Crea, edita y administra el menú</p>
            </div>
          </Link>

          <Link
            to="/admin/categorias"
            className="flex items-center gap-4 bg-white border border-gray-100 rounded-xl p-5 shadow-sm hover:shadow-md hover:border-emerald-200 transition-all no-underline group"
          >
            <div className="bg-emerald-50 p-3 rounded-lg group-hover:bg-emerald-100 transition-colors">
              <LayoutList size={22} className="text-emerald-600" />
            </div>
            <div>
              <p className="font-semibold text-slate-900 text-sm">Gestionar Categorías</p>
              <p className="text-gray-400 text-xs">Organiza las secciones del menú</p>
            </div>
          </Link>
        </div>
      </section>

      {error && (
        <div className="bg-red-50 text-red-700 border border-red-200 px-4 py-3 rounded-lg mb-4 text-sm">
          {error}
        </div>
      )}

      <section>
        <h2 className="text-xl font-semibold text-slate-900 mb-4">
          Mis Restaurantes
        </h2>

        {loading ? (
          <p className="text-gray-500">Cargando restaurantes...</p>
        ) : restaurants.length === 0 ? (
          <div className="bg-gray-50 p-8 rounded-xl text-center text-gray-500">
            <p className="font-medium">No tienes un restaurante registrado aún.</p>
            <p className="text-sm text-gray-400 mt-2 mb-4">
              Crea tu restaurante para empezar a gestionar tu menú digital.
            </p>
            <Link
              to="/admin/restaurante"
              className="inline-block bg-indigo-600 text-white px-6 py-2 rounded-lg font-semibold text-sm no-underline hover:bg-indigo-700 transition-colors"
            >
              Crear Restaurante
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {restaurants.map((restaurant) => (
              <div
                key={restaurant.id}
                className="bg-white p-6 rounded-xl shadow-sm"
              >
                <h3 className="text-lg font-semibold text-slate-900 mb-1">
                  {restaurant.nombre}
                </h3>
                <p className="text-gray-400 text-sm mb-4">
                  /{restaurant.slug}
                </p>
                <a
                  href={`/menu/${restaurant.slug}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block mb-4 bg-emerald-600 text-white px-4 py-2 rounded-lg font-semibold text-sm no-underline hover:bg-emerald-700 transition-colors"
                >
                  Ver Menú Público
                </a>
                <QrGenerator
                  restaurantId={restaurant.id}
                  restaurantSlug={restaurant.slug}
                />
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
