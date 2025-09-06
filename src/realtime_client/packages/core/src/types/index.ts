/**
 * Common type definitions
 */

export type Nullable<T> = T | null;
export type Optional<T> = T | undefined;
export type AsyncFunction<T = void> = () => Promise<T>;

export interface ErrorDetails {
    code: string;
    message: string;
    details?: unknown;
}