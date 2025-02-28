import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * Conditionally applies className strings based on the provided arguments.
 * Works similarly to the classnames or clsx libraries.
 *
 * @param {...string} inputs - Class names to be conditionally joined
 * @returns {string} - Combined class string
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
