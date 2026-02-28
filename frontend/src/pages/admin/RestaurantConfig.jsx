import { useState, useEffect } from "react";
import { restaurantService } from "../../services/api"; 
import QrGenerator from "../../components/QrGenerator"; 
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export default function RestaurantConfig() {
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");

  useEffect(() => {
    restaurantService.get().then(res => {
      setName(res.data.name);
      setSlug(res.data.slug);
    });
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    await restaurantService.update({ name });
    alert("Guardado!");
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <Card>
        <CardHeader><CardTitle>Datos del Restaurante (CU-02)</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={handleSave} className="space-y-4">
            <div className="space-y-1.5">
              <Label>Nombre del Local</Label>
              <Input value={name} onChange={(e) => setName(e.target.value)} maxLength={100} required />
            </div>
            <Button type="submit">Guardar Cambios</Button>
          </form>
        </CardContent>
      </Card>

      <Card className="p-6 flex flex-col items-center">
        <CardTitle className="mb-4">Tu Código QR</CardTitle>
        <QrGenerator value={`${window.location.origin}/m/${slug}`} />
      </Card>
    </div>
  );
}