import { useState, useEffect } from 'react';

export default function CategoryManager() {
  const [categories, setCategories] = useState([]);
  const [formData, setFormData] = useState({ 
    nombre: '', 
    descripcion: '', 
    posicion: 1, 
    activa: true 
  });

  const loadCategories = async () => {
    const res = await fetch('/api/v1/categories', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    const data = await res.json();
    setCategories(data);
  };

  useEffect(() => { loadCategories(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    const res = await fetch('/api/v1/categories', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(formData)
    });
    if (res.ok) {
      setFormData({ nombre: '', descripcion: '', posicion: categories.length + 1, activa: true });
      loadCategories();
    }
  };

  const handleDelete = async (id) => {
    const res = await fetch(`/api/v1/categories/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    if (!res.ok) alert("No se puede borrar: Existen platos en esta categoría.");
    else loadCategories();
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h2 className="text-2xl font-black mb-8 text-blue-900">Categorías del Menú</h2>
      
      {/* Formulario con todos los campos del esquema */}
      <form onSubmit={handleCreate} className="bg-white p-6 rounded-2xl shadow-sm border mb-10 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <label className="text-xs font-bold uppercase text-gray-400">Nombre de Categoría</label>
            <input 
              type="text" placeholder="Ej: Hamburguesas" value={formData.nombre} maxLength={50} required
              onChange={(e) => setFormData({...formData, nombre: e.target.value})}
              className="w-full p-2 border-b-2 focus:border-blue-500 outline-none text-lg"
            />
          </div>
          <div>
            <label className="text-xs font-bold uppercase text-gray-400">Posición</label>
            <input 
              type="number" value={formData.posicion}
              onChange={(e) => setFormData({...formData, posicion: parseInt(e.target.value)})}
              className="w-full p-2 border-b-2 outline-none text-lg"
            />
          </div>
        </div>
        
        <div className="flex flex-col md:flex-row gap-4 items-end">
          <div className="flex-1 w-full">
            <label className="text-xs font-bold uppercase text-gray-400">Descripción Breve</label>
            <input 
              type="text" value={formData.descripcion}
              onChange={(e) => setFormData({...formData, descripcion: e.target.value})}
              className="w-full p-2 border-b-2 outline-none"
            />
          </div>
          <div className="flex items-center gap-2 mb-2">
            <input 
              type="checkbox" checked={formData.activa}
              onChange={(e) => setFormData({...formData, activa: e.target.checked})}
            />
            <span className="text-sm font-bold">Activa</span>
          </div>
          <button className="bg-blue-600 text-white px-8 py-3 rounded-xl font-bold hover:bg-blue-700">
            CREAR CATEGORÍA
          </button>
        </div>
      </form>

      {/* Tabla de Listado */}
      <div className="bg-white rounded-xl shadow overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="p-4 text-xs font-bold uppercase text-gray-500">Pos</th>
              <th className="p-4 text-xs font-bold uppercase text-gray-500">Categoría</th>
              <th className="p-4 text-xs font-bold uppercase text-gray-500">Estado</th>
              <th className="p-4 text-xs font-bold uppercase text-gray-500">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {categories.map((cat) => (
              <tr key={cat.id} className="border-b hover:bg-gray-50 transition">
                <td className="p-4 font-mono text-blue-600">#{cat.posicion}</td>
                <td className="p-4">
                  <div className="font-bold">{cat.nombre}</div>
                  <div className="text-xs text-gray-400">{cat.descripcion}</div>
                </td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-bold ${cat.activa ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                    {cat.activa ? 'ACTIVA' : 'INACTIVA'}
                  </span>
                </td>
                <td className="p-4">
                  <button onClick={() => handleDelete(cat.id)} className="text-red-400 hover:text-red-600 underline text-sm">Eliminar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}