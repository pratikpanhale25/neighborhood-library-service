"use client";

import { useCallback, useRef, useState } from "react";

/**
 * Serialize async UI actions so submit buttons stay disabled until completion.
 *
 * WHY: Without this, rapid clicks can fire duplicate POST/PUT requests before the
 * first response returns, causing double creates or conflicting updates.
 */
export function useAsyncAction() {
  const [pending, setPending] = useState(false);
  const running = useRef(false);

  const run = useCallback(async <T,>(fn: () => Promise<T>): Promise<T | undefined> => {
    if (running.current) return undefined;
    running.current = true;
    setPending(true);
    try {
      return await fn();
    } finally {
      running.current = false;
      setPending(false);
    }
  }, []);

  return { pending, run };
}
