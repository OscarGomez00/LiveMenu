/**
 * Pagina publica del menu de un restaurante (accesible via QR).
 * Sera completada por el Desarrollador 4.
 */
import { useParams } from "react-router-dom";

export default function MenuPage() {
  const { slug } = useParams();

  return (
    <div className="text-center py-8">
      <h1 className="text-3xl font-bold text-slate-900 mb-2">Menu</h1>
      <p className="text-gray-500 mb-6">
        Restaurante: <strong>{slug}</strong>
      </p>
      <div className="bg-gray-50 p-8 rounded-xl text-center text-gray-500">
        <p>El menu publico sera implementado por el Desarrollador 4.</p>
        <p className="mt-2">
          Endpoint:{" "}
          <code className="bg-gray-200 px-2 py-1 rounded text-sm">
            GET /api/v1/menu/{"{"}slug{"}"}  
          </code>
        </p>
      </div>
    </div>
  );
}
