import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Fixture — has-existing-site",
  description: "Fixture for website-builder entry-mode detection.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
