import { AppNav } from "@/components/AppNav";
import { SWRProvider } from "@/components/SWRProvider";

export const dynamic = "force-dynamic";

export default function MainLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <SWRProvider>
      <AppNav />
      <div className="mx-auto max-w-5xl px-4 py-8">{children}</div>
    </SWRProvider>
  );
}
