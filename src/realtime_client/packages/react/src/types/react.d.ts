/**
 * Minimal React type declarations for build compatibility
 * This is a temporary workaround until @types/react is installed
 */

declare module 'react' {
  // Basic hook types
  export function useState<T>(initialState: T | (() => T)): [T, (value: T | ((prev: T) => T)) => void];
  export function useEffect(effect: () => void | (() => void), deps?: any[]): void;
  export function useCallback<T extends (...args: any[]) => any>(callback: T, deps: any[]): T;
  export function useRef<T>(initialValue?: T): { current: T | undefined };
  export function useRef<T>(initialValue: T): { current: T };
  
  // Component types
  export type FC<P = {}> = (props: P) => JSX.Element | null;
  export type ReactNode = string | number | boolean | null | undefined | JSX.Element | ReactNode[];
  
  // JSX namespace
  global {
    namespace JSX {
      interface Element {}
      interface IntrinsicElements {
        [key: string]: any;
      }
    }
  }
}