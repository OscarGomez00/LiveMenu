import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import api from "@/services/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";

function formatPrice(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "";
  const num = Number(value);

  try {
    return new Intl.NumberFormat("es-CO", {
      style: "currency",
      currency: "COP",
      maximumFractionDigits: 0,
    }).format(num);
  } catch {
    return num.toLocaleString("es-CO");
  }
}

function SourceBadge({ source }) {
  const isCache = source === "cache";
  return (
    <span
      className={[
        "inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold border",
        isCache ? "bg-slate-50 text-slate-700 border-slate-200" : "bg-indigo-50 text-indigo-700 border-indigo-200",
      ].join(" ")}
      title={isCache ? "Respuesta desde caché en memoria" : "Respuesta desde la base de datos"}
    >
      {isCache ? "cache" : "db"}
    </span>
  );
}

export default function MenuPage() {
  const { slug } = useParams();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [status, setStatus] = useState(null);
  const [menu, setMenu] = useState(null);

  const restaurantName = menu?.data?.restaurant?.name || slug;

  const ttl = menu?.data?.cache?.ttl_seconds;
  const source = menu?.source;

  const hasCategories = (menu?.data?.categories || []).length > 0;

  const sortedCategories = useMemo(() => {
    const cats = menu?.data?.categories || [];

    return cats;
  }, [menu]);

  const fetchMenu = async () => {
    setLoading(true);
    setError("");
    setStatus(null);

    try {
      const res = await api.get(`/menu/${slug}`);
      setMenu(res.data);
    } catch (err) {
      const code = err?.response?.status ?? null;
      setStatus(code);

      if (code === 404) {
        setError("No encontramos ese restaurante. Revisa que el QR/slug sea correcto.");
      } else {
        const detail =
          err?.response?.data?.detail ||
          err?.message ||
          "Ocurrió un error cargando el menú.";
        setError(String(detail));
      }

      setMenu(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!slug) return;
    fetchMenu();

  }, [slug]);

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="h-8 w-56 bg-slate-200 rounded animate-pulse mb-2" />
            <div className="h-4 w-72 bg-slate-200 rounded animate-pulse" />
          </div>
          <div className="h-7 w-16 bg-slate-200 rounded-full animate-pulse" />
        </div>

        <div className="grid gap-4">
          <div className="h-28 bg-slate-100 rounded-xl animate-pulse" />
          <div className="h-28 bg-slate-100 rounded-xl animate-pulse" />
          <div className="h-28 bg-slate-100 rounded-xl animate-pulse" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Menú</h1>
            <p className="text-gray-500 mt-1">
              Restaurante: <strong>{slug}</strong>
            </p>
          </div>
          <Button variant="outline" onClick={fetchMenu}>
            Reintentar
          </Button>
        </div>

        <Alert variant="destructive">
          <AlertDescription>
            {error}
            {status ? <span className="ml-2 text-xs opacity-80">(HTTP {status})</span> : null}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  // Caso raro: no error pero tampoco menú
  if (!menu?.data) {
    return (
      <div className="space-y-4">
        <h1 className="text-3xl font-bold text-slate-900">Menú</h1>
        <Alert variant="destructive">
          <AlertDescription>No se pudo cargar el menú.</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <h1 className="text-3xl font-bold text-slate-900 truncate">{restaurantName}</h1>
          <div className="mt-1 flex flex-wrap items-center gap-2 text-sm text-gray-500">
            <span className="truncate">
              Slug: <strong className="text-slate-700">{slug}</strong>
            </span>
            {typeof ttl === "number" ? (
              <span className="text-xs text-gray-400">TTL: {ttl}s</span>
            ) : null}
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <SourceBadge source={source} />
          <Button variant="outline" onClick={fetchMenu} title="Volver a consultar el endpoint">
            Actualizar
          </Button>
        </div>
      </div>

      {/* Content */}
      {!hasCategories ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">Menú vacío</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-500">
              Este restaurante todavía no tiene categorías o platos publicados.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {sortedCategories.map((cat) => (
            <Card key={cat.id}>
              <CardHeader className="pb-3">
                <CardTitle className="text-xl">{cat.name}</CardTitle>
              </CardHeader>

              <CardContent className="pt-0">
                {(!cat.dishes || cat.dishes.length === 0) ? (
                  <p className="text-gray-500 text-sm">Sin platos por ahora.</p>
                ) : (
                  <ul className="divide-y divide-slate-100">
                    {cat.dishes.map((dish) => (
                      <li key={dish.id} className="py-3 flex items-start justify-between gap-4">
                        <div className="min-w-0">
                          <p className="font-semibold text-slate-900 truncate">{dish.name}</p>
                        </div>
                        <div className="text-right shrink-0">
                          <p className="font-bold text-slate-900">{formatPrice(dish.price)}</p>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

    </div>
  );
}