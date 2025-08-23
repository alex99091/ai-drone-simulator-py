export default function ErrorBanner({ show, children }) {
  if (!show) return null;
  return (
    <div className="mt-3 rounded-md bg-amber-900/40 border border-amber-700 text-amber-200 px-3 py-2 text-xs">
      {children}
    </div>
  );
}
