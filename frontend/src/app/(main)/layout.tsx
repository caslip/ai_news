import MainLayout from "@/components/layout/MainLayout";

export default function LayoutGroupLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <MainLayout>{children}</MainLayout>;
}
