"use client";

import type { ReactNode } from "react";
import { SWRConfig } from "swr";

export function SWRProvider({ children }: { children: ReactNode }) {
  return (
    <SWRConfig
      value={{
        fetcher: (url: string) => fetch(url).then((r) => {
          if (!r.ok) throw new Error(`HTTP ${r.status}`);
          return r.json();
        }),
        revalidateOnFocus: false,
      }}
    >
      {children}
    </SWRConfig>
  );
}
