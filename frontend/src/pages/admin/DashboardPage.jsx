/**
 * Dashboard del administrador.
 * Muestra restaurantes y permite generar QR.
 */
import { useState, useEffect } from "react";
import { useAuth } from "../../hooks/useAuth";
import api from "../../services/api";
import QrGenerator from "../../components/QrGenerator";

export default function DashboardPage() {
  const { user } = useAuth();
  const [restaurants, setRestaurants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchRestaurants = async () => {
      try {
        const response = await api.get("/restaurants/");
        setRestaurants(response.data);
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
            <p>No tienes restaurantes registrados aun.</p>
            <p className="text-sm text-gray-400 mt-2">
              El modulo de restaurantes sera implementado por el Desarrollador 2.
            </p>
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
