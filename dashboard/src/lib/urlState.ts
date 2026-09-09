import { useCallback } from "react";
import { useSearchParams } from "react-router";

/** URL-state for filtre, valgt visning og åpne objekter. Én nøkkel = én søkeparameter. */
export function useUrlParam(key: string, fallback = ""): [string, (v: string | null) => void] {
  const [params, setParams] = useSearchParams();
  const value = params.get(key) ?? fallback;
  const set = useCallback(
    (v: string | null) => {
      setParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          if (v === null || v === "" || v === fallback) next.delete(key);
          else next.set(key, v);
          return next;
        },
        { replace: true },
      );
    },
    [key, fallback, setParams],
  );
  return [value, set];
}

export function useUrlParams(): [URLSearchParams, (patch: Record<string, string | null>) => void] {
  const [params, setParams] = useSearchParams();
  const patch = useCallback(
    (p: Record<string, string | null>) => {
      setParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          for (const [k, v] of Object.entries(p)) {
            if (v === null || v === "") next.delete(k);
            else next.set(k, v);
          }
          return next;
        },
        { replace: true },
      );
    },
    [setParams],
  );
  return [params, patch];
}
