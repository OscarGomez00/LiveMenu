import { useState, useEffect } from 'react';

export default function RestaurantConfig() {
  const [restaurant, setRestaurant] = useState({
    nombre: '',
    slug: '',
    descripcion: '',
    logo_url: '',
    banner_url: '',
    color_tema: '#ef4444', // Color por defecto (naranja/rojo)
    activo: true
  });

  useEffect(() => {
    const fetchRestaurant = async () => {
      const res = await fetch('/api/v1/restaurant', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (res.ok) {
        const data = await res.json();
        setRestaurant(data);
      }
    };
    fetchRestaurant();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    await fetch('/api/v1/restaurant', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(restaurant)
    });
    alert("Configuración total guardada.");
  };

  return (
    <div className="p-8 max-w-4xl mx-auto bg-white shadow-lg rounded-2xl border border-gray-100">
      <h2 className="text-3xl font-extrabold mb-8 text-gray-800 border-b pb-4">Perfil del Restaurante</h2>
      
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
          <label className="block text-sm font-bold text-gray-700 text-gray-400">Slug (Identificador único)</label>
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

        {/* URLs de Imágenes */}
        <div className="space-y-2">
          <label className="block text-sm font-bold text-gray-700">URL del Logo</label>
          <input 
            type="text" value={restaurant.logo_url}
            onChange={(e) => setRestaurant({...restaurant, logo_url: e.target.value})}
            className="w-full p-3 border rounded-lg"
            placeholder="https://link-a-mi-logo.png"
          />
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-bold text-gray-700">URL del Banner</label>
          <input 
            type="text" value={restaurant.banner_url}
            onChange={(e) => setRestaurant({...restaurant, banner_url: e.target.value})}
            className="w-full p-3 border rounded-lg"
            placeholder="https://link-al-banner.png"
          />
        </div>

        {/* Personalización y Estado */}
        <div className="flex items-center gap-6 p-4 bg-orange-50 rounded-lg">
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-1">Color del Tema</label>
            <input 
              type="color" value={restaurant.color_tema}
              onChange={(e) => setRestaurant({...restaurant, color_tema: e.target.value})}
              className="h-10 w-20 cursor-pointer rounded"
            />
          </div>
          <div className="flex items-center gap-2 mt-4">
            <input 
              type="checkbox" checked={restaurant.activo}
              onChange={(e) => setRestaurant({...restaurant, activo: e.target.checked})}
              className="w-5 h-5 accent-orange-500"
            />
            <span className="font-bold text-gray-700">Restaurante Activo</span>
          </div>
        </div>

        <div className="md:col-span-2 pt-4">
          <button type="submit" className="w-full bg-orange-600 text-white font-black py-4 rounded-xl hover:bg-orange-700 shadow-lg transform hover:-translate-y-1 transition-all">
            GUARDAR CONFIGURACIÓN COMPLETA
          </button>
        </div>
      </form>
    </div>
  );
}