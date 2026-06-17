import { AuthGuard } from "@/components/AuthGuard";
import { DashboardClient } from "@/components/DashboardClient";
import { Header } from "@/components/Header";

export default function HomePage() {
  return (
    <AuthGuard>
      <Header />
      <main className="mx-auto max-w-2xl px-4 py-8">
        <DashboardClient />
      </main>
    </AuthGuard>
  );
}
