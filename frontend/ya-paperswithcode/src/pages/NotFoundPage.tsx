import { NotFound } from '../components/papers/NotFound';

export function NotFoundPage() {
  // 从URL获取论文标题参数
  const urlParams = new URLSearchParams(window.location.search);
  const paperTitle = urlParams.get('title') || undefined;

  return (
    <div className="container py-8">
      <NotFound 
        paperTitle={paperTitle}
        message={paperTitle 
          ? "The paper link appears to be invalid or the paper may have been removed."
          : "The page you're looking for doesn't exist or has been moved."
        }
      />
    </div>
  );
}