/**
 * Barra de navegacion principal.
 */
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="flex justify-between items-center px-8 py-3 bg-slate-900 text-white shadow-md sticky top-0 z-50">
      <div>
        <Link to="/" className="text-xl font-bold text-white no-underline">
          LiveMenu
        </Link>
      </div>
      <div className="flex items-center gap-4">
        {user ? (
          <>
            <Link
              to="/admin/dashboard"
              className="text-gray-300 hover:text-white text-sm no-underline transition-colors"
            >
              Dashboard
            </Link>
            <span className="text-gray-400 text-xs">{user.email}</span>
            <button
              onClick={handleLogout}
              className="border border-red-500 text-red-500 bg-transparent px-4 py-1.5 rounded-md text-sm cursor-pointer hover:bg-red-500 hover:text-white transition-all"
            >
              Cerrar sesion
            </button>
          </>
        ) : (
          <>
            <Link
              to="/login"
              className="text-gray-300 hover:text-white text-sm no-underline transition-colors"
            >
              Iniciar sesion
            </Link>
            <Link
              to="/register"
              className="bg-indigo-600 text-white px-5 py-2 rounded-lg font-semibold text-sm no-underline hover:bg-indigo-700 transition-colors"
            >
              Registrarse
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
