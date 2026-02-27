import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Utility function para combinar clases de Tailwind CSS.
 * Usa clsx para condicionales y tailwind-merge para resolver conflictos.
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}
