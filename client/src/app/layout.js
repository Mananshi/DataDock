import './globals.css';
import Link from 'next/link';

export default function Layout({ children }) {
  return (
    <html lang="en">
      <body>
        <nav>
          <Link href="/">File Upload</Link>
          <Link href="/fileList">File List</Link>
        </nav>
        {children}
      </body>
    </html>
  );
}
