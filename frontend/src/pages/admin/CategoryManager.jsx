import { useState, useEffect } from 'react';
import { categoryService } from '../../services/api';

export default function CategoryManager() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({ 
    nombre: '', 
    descripcion: '', 
    activa: true 
  });

  const [noRestaurant, setNoRestaurant] = useState(false);

  const loadCategories = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await categoryService.getAll();
      setCategories(res.data);
      setNoRestaurant(false);
    } catch (err) {
      if (err.response?.status === 404) {
        setNoRestaurant(true);
      } else {
        setError('Error al cargar las categorías.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadCategories(); }, []);

  const showSuccess = (msg) => {
    setSuccess(msg);
    setTimeout(() => setSuccess(''), 3000);
  };

  const resetForm = () => {
    setFormData({ nombre: '', descripcion: '', activa: true });
    setEditingId(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      if (editingId) {
        await categoryService.update(editingId, formData);
        showSuccess('Categoría actualizada correctamente.');
      } else {
        await categoryService.create(formData);
        showSuccess('Categoría creada correctamente.');
      }
      resetForm();
      loadCategories();
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al guardar la categoría.');
    }
  };

  const handleEdit = (cat) => {
    setEditingId(cat.id);
    setFormData({
      nombre: cat.nombre,
      descripcion: cat.descripcion || '',
      activa: cat.activa,
    });
  };

  const handleDelete = async (id) => {
    setError('');
    try {
      await categoryService.delete(id);
      showSuccess('Categoría eliminada correctamente.');
      loadCategories();
    } catch (err) {
      setError(err.response?.data?.detail || 'No se puede borrar: existen platos en esta categoría.');
    }
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h2 className="text-2xl font-black mb-8 text-blue-900">Categorías del Menú</h2>

      {noRestaurant && (
        <div className="bg-amber-50 text-amber-800 border border-amber-200 px-6 py-8 rounded-xl text-center mb-8">
          <p className="font-semibold text-lg mb-2">No tienes un restaurante registrado</p>
          <p className="text-sm text-amber-600 mb-4">Primero debes crear tu restaurante para poder gestionar categorías.</p>
          <a href="/admin/restaurante" className="inline-block bg-amber-600 text-white px-6 py-2 rounded-lg font-bold hover:bg-amber-700 transition-colors no-underline">Crear Restaurante</a>
        </div>
      )}

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
      
      {/* Formulario crear / editar */}
      {!noRestaurant && (
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-2xl shadow-sm border mb-10 space-y-4">
        <h3 className="text-sm font-bold text-gray-500 uppercase">
          {editingId ? 'Editar Categoría' : 'Nueva Categoría'}
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <label className="text-xs font-bold uppercase text-gray-400">Nombre de Categoría</label>
            <input 
              type="text" placeholder="Ej: Hamburguesas" value={formData.nombre} maxLength={50} required
              onChange={(e) => setFormData({...formData, nombre: e.target.value})}
              className="w-full p-2 border-b-2 focus:border-blue-500 outline-none text-lg"
            />
          </div>
          <div className="flex items-end gap-2 pb-1">
            <input 
              type="checkbox" checked={formData.activa} id="activa-check"
              onChange={(e) => setFormData({...formData, activa: e.target.checked})}
            />
            <label htmlFor="activa-check" className="text-sm font-bold">Activa</label>
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
          <div className="flex gap-2">
            {editingId && (
              <button type="button" onClick={resetForm}
                className="bg-gray-200 text-gray-700 px-6 py-3 rounded-xl font-bold hover:bg-gray-300">
                CANCELAR
              </button>
            )}
            <button type="submit" className="bg-blue-600 text-white px-8 py-3 rounded-xl font-bold hover:bg-blue-700">
              {editingId ? 'GUARDAR CAMBIOS' : 'CREAR CATEGORÍA'}
            </button>
          </div>
        </div>
      </form>
      )}

      {/* Tabla de Listado */}
      {!noRestaurant && loading ? (
        <div className="flex items-center justify-center py-12 text-gray-400">
          <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mr-3" />
          Cargando categorías...
        </div>
      ) : categories.length === 0 ? (
        <div className="bg-gray-50 p-12 rounded-xl text-center text-gray-500">
          <p className="font-medium">No hay categorías registradas aún.</p>
          <p className="text-sm text-gray-400 mt-1">Crea una categoría para empezar a organizar tu menú.</p>
        </div>
      ) : (
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
                  <td className="p-4 flex gap-3">
                    <button onClick={() => handleEdit(cat)} className="text-blue-500 hover:text-blue-700 underline text-sm">Editar</button>
                    <button onClick={() => handleDelete(cat.id)} className="text-red-400 hover:text-red-600 underline text-sm">Eliminar</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}