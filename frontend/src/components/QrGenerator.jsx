/**
 * Componente para generar y descargar códigos QR de un restaurante.
 * Soporta tamaños (S, M, L, XL), formatos (PNG, SVG) y colores personalizados.
 * Usa componentes shadcn/ui.
 */
import { useState } from "react";
import qrService from "../services/qrService";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";

const SIZE_OPTIONS = [
  { value: "s", label: "S (200×200 px)" },
  { value: "m", label: "M (400×400 px)" },
  { value: "l", label: "L (800×800 px)" },
  { value: "xl", label: "XL (1200×1200 px)" },
];

const FORMAT_OPTIONS = [
  { value: "png", label: "PNG" },
  { value: "svg", label: "SVG" },
];

export default function QrGenerator({ restaurantSlug }) {
  const [qrUrl, setQrUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [size, setSize] = useState("m");
  const [format, setFormat] = useState("png");
  const [color, setColor] = useState("000000");
  const [bgColor, setBgColor] = useState("FFFFFF");

  const handleGenerate = async () => {
    setLoading(true);
    setError("");

    try {
      const blob = await qrService.downloadQr({ size, format, color, bgColor });
      const url = URL.createObjectURL(blob);
      setQrUrl(url);
    } catch (err) {
      const detail = err.response?.data?.detail || "Error al generar el QR";
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!qrUrl) return;
    const link = document.createElement("a");
    link.href = qrUrl;
    link.download = `qr-${restaurantSlug}.${format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="mt-4 space-y-4">
      {/* Opciones de personalización */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1.5">
          <Label htmlFor="qr-size">Tamaño</Label>
          <Select id="qr-size" value={size} onChange={(e) => setSize(e.target.value)}>
            {SIZE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </Select>
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="qr-format">Formato</Label>
          <Select id="qr-format" value={format} onChange={(e) => setFormat(e.target.value)}>
            {FORMAT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </Select>
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="qr-color">Color del QR</Label>
          <div className="flex items-center gap-2">
            <span className="text-gray-400 text-sm">#</span>
            <Input
              id="qr-color"
              value={color}
              onChange={(e) => setColor(e.target.value.replace(/[^0-9A-Fa-f]/g, "").slice(0, 6))}
              placeholder="000000"
              maxLength={6}
            />
            <div
              className="w-8 h-8 rounded border-2 border-gray-200 shrink-0"
              style={{ backgroundColor: `#${color}` }}
            />
          </div>
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="qr-bg">Color de fondo</Label>
          <div className="flex items-center gap-2">
            <span className="text-gray-400 text-sm">#</span>
            <Input
              id="qr-bg"
              value={bgColor}
              onChange={(e) => setBgColor(e.target.value.replace(/[^0-9A-Fa-f]/g, "").slice(0, 6))}
              placeholder="FFFFFF"
              maxLength={6}
            />
            <div
              className="w-8 h-8 rounded border-2 border-gray-200 shrink-0"
              style={{ backgroundColor: `#${bgColor}` }}
            />
          </div>
        </div>
      </div>

      <Button onClick={handleGenerate} variant="outline" disabled={loading}>
        {loading ? "Generando..." : "Generar QR"}
      </Button>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {qrUrl && (
        <div className="text-center space-y-3">
          <img
            src={qrUrl}
            alt={`QR de ${restaurantSlug}`}
            className="max-w-[200px] rounded-lg border-2 border-gray-200 mx-auto"
          />
          <Button onClick={handleDownload} variant="default" size="sm">
            Descargar QR
          </Button>
        </div>
      )}
    </div>
  );
}
