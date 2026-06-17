import { AuthGuard } from "@/components/AuthGuard";
import { DependantDetailClient } from "@/components/DependantDetailClient";
import { Header } from "@/components/Header";

export default async function DependantPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <AuthGuard>
      <Header />
      <main className="mx-auto max-w-2xl px-4 py-8">
        <DependantDetailClient id={id} />
      </main>
    </AuthGuard>
  );
}
