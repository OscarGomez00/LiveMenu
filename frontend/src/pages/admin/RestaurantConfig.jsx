import { useState, useEffect } from 'react';
import { restaurantService } from '../../services/api';

export default function RestaurantConfig() {
  const [restaurant, setRestaurant] = useState({
    nombre: '',
    slug: '',
    descripcion: '',
    logo_url: '',
    telefono: '',
    direccion: '',
    horarios: '',
  });
  const [isNew, setIsNew] = useState(true);
  const [loading, setLoading] = useState(true);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchRestaurant = async () => {
      try {
        const res = await restaurantService.get();
        setRestaurant({
          nombre: res.data.nombre || '',
          slug: res.data.slug || '',
          descripcion: res.data.descripcion || '',
          logo_url: res.data.logo_url || '',
          telefono: res.data.telefono || '',
          direccion: res.data.direccion || '',
          horarios: typeof res.data.horarios === 'object' ? JSON.stringify(res.data.horarios || '') : (res.data.horarios || ''),
        });
        setIsNew(false);
      } catch (err) {
        if (err.response?.status === 404) {
          setIsNew(true);
        }
      } finally {
        setLoading(false);
      }
    };
    fetchRestaurant();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      const payload = {
        nombre: restaurant.nombre,
        descripcion: restaurant.descripcion || null,
        logo_url: restaurant.logo_url || null,
        telefono: restaurant.telefono || null,
        direccion: restaurant.direccion || null,
        horarios: restaurant.horarios || null,
      };

      if (isNew) {
        const res = await restaurantService.create(payload);
        setRestaurant(prev => ({ ...prev, slug: res.data.slug }));
        setIsNew(false);
        setSuccess('Restaurante creado correctamente.');
      } else {
        await restaurantService.update(payload);
        setSuccess('Configuración guardada correctamente.');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al guardar la configuración.');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20 text-gray-400">
        <div className="w-6 h-6 border-2 border-orange-500 border-t-transparent rounded-full animate-spin mr-3" />
        Cargando configuración...
      </div>
    );
  }

  return (
    <div className="p-8 max-w-4xl mx-auto bg-white shadow-lg rounded-2xl border border-gray-100">
      <h2 className="text-3xl font-extrabold mb-8 text-gray-800 border-b pb-4">Perfil del Restaurante</h2>

      {success && (
        <div className="mb-4 bg-green-50 text-green-700 border border-green-200 px-4 py-3 rounded-lg text-sm">
          {success}
        </div>
      )}
      {error && (
        <div className="mb-4 bg-red-50 text-red-700 border border-red-200 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Nombre y Slug */}
        <div className="space-y-2">
          <label className="block text-sm font-bold text-gray-700">Nombre del Negocio *</label>
          <input 
            type="text" value={restaurant.nombre} maxLength={100} required
            onChange={(e) => setRestaurant({...restaurant, nombre: e.target.value})}
            className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-orange-400 outline-none"
          />
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-bold text-gray-400">Slug (generado automáticamente)</label>
          <input 
            type="text" value={restaurant.slug} disabled
            className="w-full p-3 border rounded-lg bg-gray-50 cursor-not-allowed"
            placeholder="se-genera-automatico"
          />
        </div>

        {/* Descripción */}
        <div className="md:col-span-2 space-y-2">
          <label className="block text-sm font-bold text-gray-700">Descripción (Máx 500)</label>
          <textarea 
            value={restaurant.descripcion} maxLength={500} rows="3"
            onChange={(e) => setRestaurant({...restaurant, descripcion: e.target.value})}
            className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-orange-400 outline-none"
          />
        </div>

        {/* Logo URL */}
        <div className="md:col-span-2 space-y-2">
          <label className="block text-sm font-bold text-gray-700">URL del Logo</label>
          <input 
            type="text" value={restaurant.logo_url}
            onChange={(e) => setRestaurant({...restaurant, logo_url: e.target.value})}
            className="w-full p-3 border rounded-lg"
            placeholder="https://link-a-mi-logo.png"
          />
        </div>

        {/* Teléfono y Dirección */}
        <div className="space-y-2">
          <label className="block text-sm font-bold text-gray-700">Teléfono</label>
          <input 
            type="text" value={restaurant.telefono}
            onChange={(e) => setRestaurant({...restaurant, telefono: e.target.value})}
            className="w-full p-3 border rounded-lg"
            placeholder="Ej: +57 300 123 4567"
          />
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-bold text-gray-700">Dirección</label>
          <input 
            type="text" value={restaurant.direccion}
            onChange={(e) => setRestaurant({...restaurant, direccion: e.target.value})}
            className="w-full p-3 border rounded-lg"
            placeholder="Ej: Calle 123 #45-67"
          />
        </div>

        {/* Horarios */}
        <div className="md:col-span-2 space-y-2">
          <label className="block text-sm font-bold text-gray-700">Horarios</label>
          <input 
            type="text" value={restaurant.horarios}
            onChange={(e) => setRestaurant({...restaurant, horarios: e.target.value})}
            className="w-full p-3 border rounded-lg"
            placeholder="Ej: Lun-Vie 11:00-22:00, Sab-Dom 12:00-23:00"
          />
        </div>

        <div className="md:col-span-2 pt-4">
          <button type="submit" className="w-full bg-orange-600 text-white font-black py-4 rounded-xl hover:bg-orange-700 shadow-lg transform hover:-translate-y-1 transition-all">
            {isNew ? 'CREAR RESTAURANTE' : 'GUARDAR CONFIGURACIÓN'}
          </button>
        </div>
      </form>
    </div>
  );
}