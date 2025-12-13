import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-6xl font-bold text-gray-900 dark:text-white mb-4">
            AutoDealGenie
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
            AI-Powered Automotive Deal Management Platform
          </p>
          <p className="text-lg text-gray-500 dark:text-gray-400 max-w-2xl mx-auto">
            Streamline your automotive deals with cutting-edge AI technology, 
            real-time analytics, and intelligent automation.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <div className="text-4xl mb-4">🚗</div>
            <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">
              Deal Management
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Track and manage automotive deals with ease. Complete visibility from inquiry to close.
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">
              AI-Powered Insights
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Leverage OpenAI and LangChain for intelligent pricing analysis and customer responses.
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <div className="text-4xl mb-4">⚡</div>
            <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">
              Real-time Updates
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Stay synchronized with Kafka messaging and Redis caching for instant notifications.
            </p>
          </div>
        </div>

        <div className="text-center">
          <Link
            href="/deals"
            className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-3 rounded-lg transition-colors shadow-lg"
          >
            View Deals
          </Link>
        </div>

        <div className="mt-16 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Technology Stack
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Frontend</h4>
              <ul className="text-gray-600 dark:text-gray-300 space-y-1">
                <li>✓ Next.js 14 with TypeScript</li>
                <li>✓ Tailwind CSS</li>
                <li>✓ React Server Components</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Backend</h4>
              <ul className="text-gray-600 dark:text-gray-300 space-y-1">
                <li>✓ Python FastAPI</li>
                <li>✓ PostgreSQL + SQLAlchemy</li>
                <li>✓ MongoDB + Motor</li>
                <li>✓ Redis for caching</li>
                <li>✓ Kafka for messaging</li>
                <li>✓ LangChain + OpenAI</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
