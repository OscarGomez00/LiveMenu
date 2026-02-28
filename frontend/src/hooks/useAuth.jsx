/**
 * Hook personalizado para manejar el estado de autenticación.
 */
import { useState, useEffect, createContext, useContext } from "react";
import authService from "../services/authService";

const AuthContext = createContext(null);

/**
 * Provider de autenticación.
 * Envuelve la app para dar acceso al estado de auth en todos los componentes.
 */
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      if (authService.isAuthenticated()) {
        try {
          const userData = await authService.getMe();
          setUser(userData);
        } catch {
          authService.logout();
          setUser(null);
        }
      }
      setLoading(false);
    };
    checkAuth();
  }, []);

  const login = async (email, password) => {
    await authService.login(email, password);
    const userData = await authService.getMe();
    setUser(userData);
  };

  const register = async (email, password) => {
    await authService.register(email, password);
    const userData = await authService.getMe();
    setUser(userData);
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Hook para acceder al contexto de autenticación.
 * @returns {{ user, loading, login, register, logout }}
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
