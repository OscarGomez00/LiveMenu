import { useState, useEffect } from "react";
import api from "../../services/api"; 
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export default function CategoryManager() {
  const [categories, setCategories] = useState([]);
  const [name, setName] = useState("");
  const [position, setPosition] = useState(0);

  useEffect(() => { fetchCategories(); }, []);

  const fetchCategories = async () => {
    try {
      const res = await api.get("/categories/");
      setCategories(res.data.sort((a, b) => a.position - b.position));
    } catch (err) { console.error("Error al cargar"); }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (name.length > 50) return alert("Máximo 50 caracteres");
    await api.post("/categories/", { name, position: parseInt(position), is_active: true });
    setName(""); setPosition(0); fetchCategories();
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader><CardTitle>Nueva Categoría (CU-03)</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="flex gap-4 items-end">
            <div className="flex-1 space-y-1.5">
              <Label>Nombre</Label>
              <Input value={name} onChange={(e) => setName(e.target.value)} maxLength={50} required />
            </div>
            <div className="w-24 space-y-1.5">
              <Label>Posición</Label>
              <Input type="number" value={position} onChange={(e) => setPosition(e.target.value)} />
            </div>
            <Button type="submit">Agregar</Button>
          </form>
        </CardContent>
      </Card>

      <div className="bg-white rounded-lg border">
        <div className="p-4 border-b font-bold grid grid-cols-3">
          <span>Posición</span><span>Nombre</span><span className="text-right">Acción</span>
        </div>
        {categories.map((cat) => (
          <div key={cat.id} className="p-4 border-b grid grid-cols-3 items-center">
            <span>{cat.position}</span>
            <span className="font-medium">{cat.name}</span>
            <div className="text-right">
              <Button variant="destructive" size="sm" onClick={async () => {
                await api.delete(`/categories/${cat.id}`);
                fetchCategories();
              }}>Eliminar</Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}