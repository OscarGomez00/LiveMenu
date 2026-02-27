/**
 * Pagina de inicio publica.
 */
import { Link } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

export default function HomePage() {
  const { user } = useAuth();

  return (
    <div className="text-center">
      <div className="py-12">
        <h1 className="text-5xl font-bold text-slate-900 mb-2">LiveMenu</h1>
        <p className="text-xl text-indigo-600 font-semibold mb-4">
          Menus digitales con codigo QR para tu restaurante
        </p>
        <p className="text-gray-500 max-w-xl mx-auto mb-8 leading-relaxed">
          Crea, gestiona y comparte el menu de tu restaurante de forma digital.
          Tus clientes escanean un QR y ven tu menu actualizado al instante.
        </p>
        <div className="flex gap-4 justify-center flex-wrap">
          {user ? (
            <Link
              to="/admin/dashboard"
              className="bg-indigo-600 text-white px-8 py-3 rounded-lg font-semibold text-lg no-underline hover:bg-indigo-700 transition-colors"
            >
              Ir al Dashboard
            </Link>
          ) : (
            <>
              <Link
                to="/register"
                className="bg-indigo-600 text-white px-8 py-3 rounded-lg font-semibold text-lg no-underline hover:bg-indigo-700 transition-colors"
              >
                Comenzar Gratis
              </Link>
              <Link
                to="/login"
                className="border-2 border-indigo-600 text-indigo-600 px-8 py-3 rounded-lg font-semibold text-lg no-underline hover:bg-indigo-600 hover:text-white transition-all"
              >
                Iniciar Sesion
              </Link>
            </>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
        <div className="bg-white p-8 rounded-xl shadow-sm text-left">
          <h3 className="text-lg font-semibold text-slate-900 mb-2">Menu Digital</h3>
          <p className="text-gray-500 leading-relaxed">
            Tu menu siempre actualizado y accesible desde cualquier dispositivo.
          </p>
        </div>
        <div className="bg-white p-8 rounded-xl shadow-sm text-left">
          <h3 className="text-lg font-semibold text-slate-900 mb-2">Codigo QR</h3>
          <p className="text-gray-500 leading-relaxed">
            Genera un QR unico para tu restaurante. Imprimelo y colocalo en tus mesas.
          </p>
        </div>
        <div className="bg-white p-8 rounded-xl shadow-sm text-left">
          <h3 className="text-lg font-semibold text-slate-900 mb-2">Panel Admin</h3>
          <p className="text-gray-500 leading-relaxed">
            Gestiona tu menu desde un panel seguro con autenticacion JWT.
          </p>
        </div>
      </div>
    </div>
  );
}
