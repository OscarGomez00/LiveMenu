import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import api from "@/services/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";

const BACKEND_URL = import.meta.env.VITE_API_URL?.replace("/api/v1", "") || "";

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

function imgSrc(url) {
  if (!url) return null;
  if (url.startsWith("http")) return url;
  return `${BACKEND_URL}${url.startsWith("/") ? "" : "/"}${url}`;
}

/* ---------- sub-components ---------- */

function SourceBadge({ source }) {
  const isCache = source === "cache";
  return (
    <span
      className={[
        "inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold border",
        isCache
          ? "bg-slate-50 text-slate-700 border-slate-200"
          : "bg-indigo-50 text-indigo-700 border-indigo-200",
      ].join(" ")}
      title={isCache ? "Respuesta desde caché" : "Respuesta desde la base de datos"}
    >
      {isCache ? "cache" : "db"}
    </span>
  );
}

function FeaturedBadge() {
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-amber-50 text-amber-700 border border-amber-200 px-2 py-0.5 text-xs font-semibold">
      ★ Destacado
    </span>
  );
}

function TagList({ tags }) {
  if (!tags || tags.length === 0) return null;
  return (
    <div className="flex flex-wrap gap-1.5 mt-1.5">
      {tags.map((tag) => (
        <span
          key={tag}
          className="inline-block rounded-full bg-slate-100 text-slate-600 px-2.5 py-0.5 text-xs font-medium"
        >
          {tag}
        </span>
      ))}
    </div>
  );
}

function DishPrice({ price, offerPrice }) {
  if (offerPrice != null && offerPrice < price) {
    return (
      <div className="text-right">
        <p className="text-sm text-gray-400 line-through">{formatPrice(price)}</p>
        <p className="font-bold text-emerald-600 text-lg">{formatPrice(offerPrice)}</p>
      </div>
    );
  }
  return (
    <div className="text-right">
      <p className="font-bold text-slate-900 text-lg">{formatPrice(price)}</p>
    </div>
  );
}

function DishCard({ dish }) {
  const src = imgSrc(dish.image_url);

  return (
    <li className="py-4 flex gap-4">
      {/* Image */}
      {src && (
        <div className="shrink-0 w-24 h-24 rounded-lg overflow-hidden bg-slate-100">
          <img
            src={src}
            alt={dish.name}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        </div>
      )}

      {/* Info */}
      <div className="flex-1 min-w-0 flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <p className="font-semibold text-slate-900">{dish.name}</p>
            {dish.featured && <FeaturedBadge />}
          </div>
          {dish.description && (
            <p className="text-gray-500 text-sm mt-0.5 line-clamp-2">{dish.description}</p>
          )}
          <TagList tags={dish.tags} />
        </div>
      </div>

      {/* Price */}
      <div className="shrink-0 flex items-start pt-0.5">
        <DishPrice price={dish.price} offerPrice={dish.offer_price} />
      </div>
    </li>
  );
}

/* ---------- main page ---------- */

export default function MenuPage() {
  const { slug } = useParams();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [status, setStatus] = useState(null);
  const [menu, setMenu] = useState(null);

  const restaurant = menu?.data?.restaurant;
  const restaurantName = restaurant?.name || slug;
  const source = menu?.source;

  const hasCategories = (menu?.data?.categories || []).length > 0;

  const sortedCategories = useMemo(() => {
    return menu?.data?.categories || [];
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

  /* --- Loading skeleton --- */
  if (loading) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">
        <div className="flex items-center gap-4">
          <div className="h-16 w-16 bg-slate-200 rounded-full animate-pulse" />
          <div>
            <div className="h-7 w-48 bg-slate-200 rounded animate-pulse mb-2" />
            <div className="h-4 w-64 bg-slate-200 rounded animate-pulse" />
          </div>
        </div>
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-32 bg-slate-100 rounded-xl animate-pulse" />
        ))}
      </div>
    );
  }

  /* --- Error state --- */
  if (error) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8 space-y-4">
        <h1 className="text-3xl font-bold text-slate-900">Menú</h1>
        <p className="text-gray-500">
          Restaurante: <strong>{slug}</strong>
        </p>
        <Alert variant="destructive">
          <AlertDescription>
            {error}
            {status ? <span className="ml-2 text-xs opacity-80">(HTTP {status})</span> : null}
          </AlertDescription>
        </Alert>
        <Button variant="outline" onClick={fetchMenu}>
          Reintentar
        </Button>
      </div>
    );
  }

  /* --- No data fallback --- */
  if (!menu?.data) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8 space-y-4">
        <h1 className="text-3xl font-bold text-slate-900">Menú</h1>
        <Alert variant="destructive">
          <AlertDescription>No se pudo cargar el menú.</AlertDescription>
        </Alert>
      </div>
    );
  }

  /* --- Main render --- */
  const logoSrc = imgSrc(restaurant?.logo_url);

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-8">
      {/* Restaurant Header */}
      <header className="flex items-start gap-4">
        {logoSrc && (
          <img
            src={logoSrc}
            alt={restaurantName}
            className="w-16 h-16 rounded-full object-cover border border-slate-200 shrink-0"
          />
        )}
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-3xl font-bold text-slate-900 truncate">{restaurantName}</h1>
            <SourceBadge source={source} />
          </div>
          {restaurant?.description && (
            <p className="text-gray-500 mt-1 leading-relaxed">{restaurant.description}</p>
          )}
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={fetchMenu}
          className="shrink-0"
          title="Actualizar menú"
        >
          ↻
        </Button>
      </header>

      {/* Categories + Dishes */}
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
        <div className="space-y-6">
          {sortedCategories.map((cat) => (
            <Card key={cat.id} className="overflow-hidden">
              <CardHeader className="pb-2 bg-slate-50/60">
                <CardTitle className="text-xl">{cat.name}</CardTitle>
                {cat.description && (
                  <p className="text-sm text-gray-500 mt-0.5">{cat.description}</p>
                )}
              </CardHeader>

              <CardContent className="pt-0 px-4 sm:px-6">
                {(!cat.dishes || cat.dishes.length === 0) ? (
                  <p className="text-gray-500 text-sm py-4">Sin platos por ahora.</p>
                ) : (
                  <ul className="divide-y divide-slate-100">
                    {cat.dishes.map((dish) => (
                      <DishCard key={dish.id} dish={dish} />
                    ))}
                  </ul>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Footer */}
      <footer className="text-center text-xs text-gray-400 pt-4 border-t border-slate-100">
        Menú digital por <strong>LiveMenu</strong>
      </footer>
    </div>
  );
}