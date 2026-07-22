// =====================================================
// REACT DASHBOARD - Product Review Sentiment Analyzer
// =====================================================
// Tech Stack: React 18, TypeScript, TailwindCSS, Recharts
// Build: npm create vite@latest frontend -- --template react-ts

import React, { useState, useEffect, useMemo, useRef } from 'react';
import {
  LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { Upload, TrendingUp, AlertCircle, CheckCircle, Clock, LogIn, Trash2 } from 'lucide-react';
import { AuthProvider, useAuth } from 'react-oidc-context';

// =====================================================
// TYPE DEFINITIONS
// =====================================================

interface Review {
  review_id: string;
  user_id: string;
  text: string;
  rating: number;
  sentiment: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL' | 'MIXED' | 'PENDING';
  created_at: string;
  key_phrases: string[];
  use_deep_insight?: boolean;
  summary?: string;
  aspects?: string[];
  aspect_sentiments?: Record<string, string>;
  action_items?: string[];
  deep_insight_model?: string;
}

// Response shape from POST /analyze -- deliberately not a Review: this
// result is ephemeral (never stored), so it has no review_id, user_id,
// or created_at.
interface SingleAnalysisResult {
  sentiment: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL' | 'MIXED';
  scores: { Positive: number; Negative: number; Neutral: number; Mixed: number };
  key_phrases: string[];
  language: string;
  summary?: string;
  aspects?: string[];
  aspect_sentiments?: Record<string, string>;
  action_items?: string[];
  deep_insight_model?: string;
}

interface Product {
  product_id: string;
  name: string;
  category: string;
  review_count: number;
  avg_rating: number;
  avg_sentiment_score: number;
}

interface Analytics {
  product_id: string;
  total_reviews: number;
  sentiment_distribution: {
    POSITIVE: number;
    NEGATIVE: number;
    NEUTRAL: number;
    MIXED: number;
  };
  average_rating: number;
  positive_percentage: number;
  negative_percentage: number;
}

// Auth tokens are no longer managed by hand here -- react-oidc-context's
// useAuth().user.id_token replaces the old localStorage-based AuthTokens
// shape (and the login()/signup() stub methods that used it).

// =====================================================
// API CLIENT
// =====================================================

class APIClient {
  private baseURL: string;
  private idToken: string | null = null;

  constructor(baseURL: string, idToken: string | null = null) {
    this.baseURL = baseURL;
    this.idToken = idToken;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> | undefined),
    };

    if (this.idToken) {
      headers['Authorization'] = `Bearer ${this.idToken}`;
    }

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      // response.statusText is frequently empty for HTTP/2 responses
      // (a browser quirk, not an AWS-specific issue) -- relying on it
      // alone hid the actual status code and error body during testing.
      // Surface both explicitly instead.
      let detail = '';
      try {
        const body = await response.json();
        detail = body?.error || JSON.stringify(body);
      } catch {
        // Response wasn't JSON (or was empty) -- fall back to nothing extra.
      }
      throw new Error(`API Error (${response.status}): ${detail || response.statusText || 'unknown error'}`);
    }

    return response.json();
  }

  async getProducts(): Promise<Product[]> {
    const data = await this.request<{ products: Product[] }>('/products');
    return data.products;
  }

  async createProduct(name: string, category: string): Promise<string> {
    const data = await this.request<{ product_id: string }>('/products', {
      method: 'POST',
      body: JSON.stringify({ name, category }),
    });
    return data.product_id;
  }

  async deleteProduct(productId: string): Promise<{ reviews_deleted: number }> {
    return this.request<{ reviews_deleted: number }>(`/products/${productId}`, {
      method: 'DELETE',
    });
  }

  async deleteReview(productId: string, reviewId: string): Promise<void> {
    await this.request<{ status: string }>(`/products/${productId}/reviews/${reviewId}`, {
      method: 'DELETE',
    });
  }

  async getProductReviews(productId: string): Promise<Review[]> {
    const data = await this.request<{ reviews: Review[] }>(
      `/products/${productId}/reviews`
    );
    return data.reviews;
  }

  async getProductAnalytics(productId: string): Promise<Analytics> {
    return this.request<Analytics>(`/products/${productId}/analytics`);
  }

  async getPresignedURL(fileType: 'json' | 'csv', useDeepInsight: boolean): Promise<string> {
    const data = await this.request<{ upload_url: string }>('/upload', {
      method: 'POST',
      body: JSON.stringify({ file_type: fileType, use_deep_insight: useDeepInsight }),
    });
    return data.upload_url;
  }

  async analyzeReview(reviewText: string, rating: number, useDeepInsight: boolean): Promise<SingleAnalysisResult> {
    return this.request<SingleAnalysisResult>('/analyze', {
      method: 'POST',
      body: JSON.stringify({ review_text: reviewText, rating, use_deep_insight: useDeepInsight }),
    });
  }
}

// =====================================================
// COMPONENTS
// =====================================================

// Navigation Header
const Header: React.FC<{ onLogout: () => void; userEmail?: string }> = ({ onLogout, userEmail }) => (
  <header className="bg-gradient-to-r from-blue-600 to-blue-800 text-white shadow-lg">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-wrap justify-between items-center gap-2">
      <div className="flex items-center gap-2 sm:gap-3">
        <TrendingUp size={28} className="shrink-0" />
        <h1 className="text-lg sm:text-2xl font-bold">Review Sentiment Analyzer</h1>
      </div>
      <div className="flex items-center gap-4">
        {userEmail && <span className="text-sm text-blue-100 hidden sm:inline">{userEmail}</span>}
        <button
          onClick={onLogout}
          className="bg-red-500 hover:bg-red-600 px-4 py-2 rounded-lg font-semibold transition"
        >
          Logout
        </button>
      </div>
    </div>
  </header>
);

// File Upload Component
// Add Product Form Component
// Wires up APIClient.createProduct(), which existed in the API client
// already but had no UI calling it -- every product before this could
// only come from auto-registration during review upload (raw ID as
// name, "Uncategorized" category), with no way to give one a real name.
const AddProductForm: React.FC<{ apiClient: APIClient; onCreated: () => void; onCancel: () => void }> = ({
  apiClient,
  onCreated,
  onCancel,
}) => {
  const [name, setName] = useState('');
  const [category, setCategory] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('Product name is required');
      return;
    }
    try {
      setSubmitting(true);
      setError('');
      await apiClient.createProduct(name.trim(), category.trim() || 'Uncategorized');
      onCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create product');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-4 mb-4 border border-blue-200">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <input
          type="text"
          placeholder="Product name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm md:col-span-1"
          autoFocus
        />
        <input
          type="text"
          placeholder="Category (optional)"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm md:col-span-1"
        />
        <div className="flex gap-2 md:col-span-1">
          <button
            type="submit"
            disabled={submitting}
            className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white text-sm font-semibold py-2 px-4 rounded-lg transition"
          >
            {submitting ? 'Creating...' : 'Create'}
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-semibold py-2 px-4 rounded-lg transition"
          >
            Cancel
          </button>
        </div>
      </div>
      {error && <p className="text-red-600 text-sm mt-2">{error}</p>}
    </form>
  );
};

// Single Review Analyzer Component
// Instant, synchronous sentiment analysis for one review at a time --
// no S3 upload, no DynamoDB Stream wait. Result is ephemeral (nothing
// persisted), distinct from the upload/webhook paths that build up a
// product's real review data. Good for quickly trying the analyzer out.
const SingleReviewAnalyzer: React.FC<{ apiClient: APIClient }> = ({ apiClient }) => {
  const [text, setText] = useState('');
  const [rating, setRating] = useState(3);
  const [useDeepInsight, setUseDeepInsight] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<SingleAnalysisResult | null>(null);

  const sentimentColors = {
    POSITIVE: 'bg-green-100 text-green-800',
    NEGATIVE: 'bg-red-100 text-red-800',
    NEUTRAL: 'bg-gray-100 text-gray-800',
    MIXED: 'bg-yellow-100 text-yellow-800',
  };

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    try {
      setAnalyzing(true);
      setError('');
      setResult(null);
      const data = await apiClient.analyzeReview(text.trim(), rating, useDeepInsight);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-bold text-gray-800 mb-1">Analyze a Single Review</h3>
      <p className="text-sm text-gray-500 mb-4">
        Instant test, not saved anywhere — for building up real review data, use Upload Reviews instead.
      </p>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste or type a review..."
        rows={3}
        className="w-full border rounded-lg px-3 py-2 text-sm mb-3"
      />

      <div className="flex flex-wrap items-center gap-4 mb-3">
        <label className="flex items-center gap-2 text-sm text-gray-700">
          Rating:
          <select
            value={rating}
            onChange={(e) => setRating(Number(e.target.value))}
            className="border rounded px-2 py-1 text-sm"
          >
            {[1, 2, 3, 4, 5].map((r) => (
              <option key={r} value={r}>{r}⭐</option>
            ))}
          </select>
        </label>
        <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
          <input
            type="checkbox"
            checked={useDeepInsight}
            onChange={(e) => setUseDeepInsight(e.target.checked)}
          />
          Use AI deep insight
        </label>
      </div>

      {error && (
        <div className="bg-red-50 p-3 rounded-lg mb-3 flex gap-2">
          <AlertCircle size={20} className="text-red-600 shrink-0" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <button
        onClick={handleAnalyze}
        disabled={!text.trim() || analyzing}
        className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white text-sm font-semibold py-2 px-4 rounded-lg transition"
      >
        {analyzing ? 'Analyzing...' : 'Analyze'}
      </button>

      {result && (
        <div className="mt-4 pt-4 border-t">
          <div className="flex items-center gap-2 mb-2">
            <span className={`px-2 py-1 rounded text-xs font-semibold ${sentimentColors[result.sentiment]}`}>
              {result.sentiment}
            </span>
            {result.deep_insight_model && (
              <span
                className="px-2 py-1 rounded text-xs font-semibold bg-purple-100 text-purple-800 max-w-[220px] truncate inline-block"
                title={`Analyzed by ${result.deep_insight_model}`}
              >
                AI · {result.deep_insight_model}
              </span>
            )}
          </div>

          <div className="text-xs text-gray-600 mb-2">
            Positive {(result.scores.Positive * 100).toFixed(0)}% · Negative {(result.scores.Negative * 100).toFixed(0)}%
            {' '}· Neutral {(result.scores.Neutral * 100).toFixed(0)}% · Mixed {(result.scores.Mixed * 100).toFixed(0)}%
          </div>

          {result.key_phrases.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-2">
              {result.key_phrases.slice(0, 5).map((phrase, idx) => (
                <span key={idx} className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                  {phrase}
                </span>
              ))}
            </div>
          )}

          {result.summary && (
            <div className="mt-2">
              <p className="text-sm text-purple-900 italic">"{result.summary}"</p>
              {result.aspects && result.aspects.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {result.aspects.map((aspect, idx) => (
                    <span key={idx} className="text-xs bg-purple-50 text-purple-700 border border-purple-200 px-2 py-1 rounded">
                      {aspect}{result.aspect_sentiments?.[aspect] ? ` · ${result.aspect_sentiments[aspect]}` : ''}
                    </span>
                  ))}
                </div>
              )}
              {result.action_items && result.action_items.length > 0 && (
                <ul className="mt-2 text-xs text-gray-600 list-disc list-inside">
                  {result.action_items.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const FileUploader: React.FC<{ apiClient: APIClient; onUploadComplete: () => void }> = ({ apiClient, onUploadComplete }) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string>('');
  const [useDeepInsight, setUseDeepInsight] = useState(false);

  const handleUpload = async () => {
    if (!file) return;

    try {
      setUploading(true);
      setError('');

      const fileType = file.name.endsWith('.json') ? 'json' : 'csv';
      const presignedURL = await apiClient.getPresignedURL(fileType, useDeepInsight);

      // Must exactly match the Content-Type the backend signed into the
      // presigned URL (generate_presigned_url() always signs
      // 'application/json' or 'text/csv' based on this same fileType) --
      // NOT the browser's own file.type guess. file.type is unreliable:
      // Windows commonly reports .csv files as 'application/vnd.ms-excel'
      // (an Excel file association) rather than 'text/csv', which S3
      // then rejects with SignatureDoesNotMatch since it doesn't match
      // what was actually signed.
      const contentType = fileType === 'json' ? 'application/json' : 'text/csv';

      // Upload to S3 using presigned URL
      const uploadResponse = await fetch(presignedURL, {
        method: 'PUT',
        body: file,
        headers: {
          'Content-Type': contentType,
        },
      });

      if (!uploadResponse.ok) {
        throw new Error('Upload failed');
      }

      setFile(null);
      onUploadComplete();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border-2 border-dashed border-gray-300 hover:border-blue-500 transition">
      <div className="flex flex-col items-center gap-4">
        <Upload size={48} className="text-gray-400" />
        <h3 className="text-lg font-semibold">Upload Reviews</h3>
        <p className="text-gray-600 text-sm text-center">
          Drag and drop your JSON or CSV file here, or click to select
        </p>

        <input
          type="file"
          accept=".json,.csv"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="block w-full text-sm text-gray-500
            file:mr-4 file:py-2 file:px-4
            file:rounded-lg file:border-0
            file:text-sm file:font-semibold
            file:bg-blue-50 file:text-blue-700
            hover:file:bg-blue-100"
        />

        {file && (
          <div className="bg-blue-50 p-3 rounded-lg w-full">
            <p className="text-sm text-blue-800">
              Selected: <strong>{file.name}</strong> ({(file.size / 1024).toFixed(2)} KB)
            </p>
          </div>
        )}

        <label className="flex items-start gap-2 w-full bg-purple-50 border border-purple-200 rounded-lg p-3 cursor-pointer">
          <input
            type="checkbox"
            checked={useDeepInsight}
            onChange={(e) => setUseDeepInsight(e.target.checked)}
            className="mt-0.5"
          />
          <span className="text-sm text-purple-900">
            <strong>Use AI deep insight</strong> — an LLM (Llama 3.1 8B) extracts aspect-based
            sentiment, action items, and a written summary for each review, beyond the
            automatic Comprehend classification that always runs. Pay-per-token; only
            applies to this upload, not turned on globally.
          </span>
        </label>

        {error && (
          <div className="bg-red-50 p-3 rounded-lg w-full flex gap-2">
            <AlertCircle size={20} className="text-red-600" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-2 px-4 rounded-lg transition"
        >
          {uploading ? 'Uploading...' : 'Upload & Process'}
        </button>
      </div>
    </div>
  );
};

// Product Card Component
const ProductCard: React.FC<{
  product: Product;
  onSelect: (id: string) => void;
  apiClient: APIClient;
  onDeleted: () => void;
  isSelected: boolean;
}> = ({ product, onSelect, apiClient, onDeleted, isSelected }) => {
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation(); // don't also trigger onSelect on the card
    const confirmed = window.confirm(
      `Delete "${product.name}"? This also permanently deletes all ${product.review_count} review(s) for this product. This can't be undone.`
    );
    if (!confirmed) return;

    try {
      setDeleting(true);
      await apiClient.deleteProduct(product.product_id);
      onDeleted();
    } catch (err) {
      window.alert(err instanceof Error ? err.message : 'Failed to delete product');
      setDeleting(false);
    }
  };

  return (
    <div
      onClick={() => onSelect(product.product_id)}
      className={`rounded-lg shadow-md p-4 hover:shadow-lg cursor-pointer transition border-l-4 border-blue-500 relative ${
        isSelected ? 'bg-blue-50 ring-2 ring-blue-600 ring-offset-2' : 'bg-white'
      }`}
    >
      {isSelected && (
        <span className="absolute -top-2 -left-2 bg-blue-600 text-white text-xs font-semibold px-2 py-0.5 rounded-full shadow">
          Selected
        </span>
      )}
      <button
        onClick={handleDelete}
        disabled={deleting}
        title="Delete product and all its reviews"
        className="absolute top-3 right-3 text-gray-300 hover:text-red-600 transition disabled:opacity-50"
      >
        {deleting ? <Clock size={16} className="animate-spin" /> : <Trash2 size={16} />}
      </button>

      <h3 className="text-lg font-bold text-gray-800 pr-6">{product.name}</h3>
      <p className="text-sm text-gray-600">{product.category}</p>

      <div className="mt-4 grid grid-cols-3 gap-2 text-center">
        <div className="bg-blue-50 p-2 rounded">
          <p className="text-xs text-gray-600">Reviews</p>
          <p className="text-lg font-bold text-blue-600">{product.review_count}</p>
        </div>
        <div className="bg-yellow-50 p-2 rounded">
          <p className="text-xs text-gray-600">Avg Rating</p>
          <p className="text-lg font-bold text-yellow-600">{product.avg_rating.toFixed(1)}⭐</p>
        </div>
        <div className="bg-green-50 p-2 rounded">
          <p className="text-xs text-gray-600">Sentiment</p>
          <p className="text-lg font-bold text-green-600">{(product.avg_sentiment_score * 100).toFixed(0)}%</p>
        </div>
      </div>
    </div>
  );
};

// CSV export utility -- purely client-side, since the reviews the user
// is currently looking at (already filtered/sorted) are already in
// memory. Handles proper CSV escaping: fields containing a comma,
// quote, or newline get wrapped in quotes with internal quotes doubled.
function csvEscape(value: string): string {
  if (/[",\n]/.test(value)) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}

function downloadReviewsAsCSV(reviews: Review[], productName: string) {
  const headers = [
    'Review ID', 'User ID', 'Rating', 'Sentiment', 'Created At', 'Review Text',
    'Key Phrases', 'Used AI Deep Insight', 'Deep Insight Model', 'Summary',
    'Aspects', 'Action Items',
  ];

  const rows = reviews.map((r) => [
    r.review_id,
    r.user_id,
    String(r.rating),
    r.sentiment,
    r.created_at,
    r.text,
    (r.key_phrases || []).join('; '),
    r.use_deep_insight ? 'Yes' : 'No',
    r.deep_insight_model || '',
    r.summary || '',
    (r.aspects || []).join('; '),
    (r.action_items || []).join('; '),
  ]);

  const csvContent = [headers, ...rows]
    .map((row) => row.map((cell) => csvEscape(cell)).join(','))
    .join('\n');

  // Prepend a UTF-8 BOM so Excel opens accented/non-ASCII characters
  // (e.g. from non-English reviews) correctly instead of mangling them.
  const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${productName.replace(/[^a-z0-9]/gi, '_')}_reviews_${new Date().toISOString().slice(0, 10)}.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

// Analytics Dashboard Component
const AnalyticsDashboard: React.FC<{
  analytics: Analytics;
  reviews: Review[];
  apiClient: APIClient;
  productId: string;
  productName: string;
  onReviewDeleted: () => void;
}> = ({ analytics, reviews, apiClient, productId, productName, onReviewDeleted }) => {
  const sentimentData = [
    { name: 'Positive', value: analytics.sentiment_distribution.POSITIVE, fill: '#10b981' },
    { name: 'Negative', value: analytics.sentiment_distribution.NEGATIVE, fill: '#ef4444' },
    { name: 'Neutral', value: analytics.sentiment_distribution.NEUTRAL, fill: '#6b7280' },
    { name: 'Mixed', value: analytics.sentiment_distribution.MIXED, fill: '#f59e0b' },
  ];

  // Trend data: real counts per day for the last 7 calendar days,
  // computed from actual review creation dates and sentiment. Previously
  // this was Math.random() fabricated data with zero connection to real
  // reviews -- different fake numbers on every single render, not even
  // consistent fake data.
  const trendData = useMemo(() => {
    const days: { date: string; label: string; positive: number; negative: number }[] = [];
    for (let i = 6; i >= 0; i--) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      days.push({
        date: d.toISOString().slice(0, 10), // YYYY-MM-DD, for matching against created_at
        label: d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
        positive: 0,
        negative: 0,
      });
    }
    const dayMap = new Map(days.map((d) => [d.date, d]));
    reviews.forEach((r) => {
      const dateStr = r.created_at?.slice(0, 10);
      const bucket = dateStr ? dayMap.get(dateStr) : undefined;
      if (!bucket) return; // review falls outside the last 7 days -- not plotted
      if (r.sentiment === 'POSITIVE') bucket.positive += 1;
      else if (r.sentiment === 'NEGATIVE') bucket.negative += 1;
    });
    return days;
  }, [reviews]);

  const hasTrendData = trendData.some((d) => d.positive > 0 || d.negative > 0);

  // Recent reviews -- `reviews` is now correctly sorted by actual
  // CreatedAt (see the backend fix), so slicing the first 5 really does
  // give the most recent ones.
  const [sentimentFilter, setSentimentFilter] = useState<
    'ALL' | 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL' | 'MIXED' | 'PENDING'
  >('ALL');
  const [sortBy, setSortBy] = useState<'newest' | 'oldest' | 'rating_high' | 'rating_low'>('newest');

  const sentimentCounts = useMemo(() => {
    const counts: Record<string, number> = { ALL: reviews.length };
    reviews.forEach((r) => {
      counts[r.sentiment] = (counts[r.sentiment] || 0) + 1;
    });
    return counts;
  }, [reviews]);

  const filteredSortedReviews = useMemo(() => {
    const filtered = sentimentFilter === 'ALL' ? reviews : reviews.filter((r) => r.sentiment === sentimentFilter);
    return [...filtered].sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return b.created_at.localeCompare(a.created_at);
        case 'oldest':
          return a.created_at.localeCompare(b.created_at);
        case 'rating_high':
          return b.rating - a.rating;
        case 'rating_low':
          return a.rating - b.rating;
        default:
          return 0;
      }
    });
  }, [reviews, sentimentFilter, sortBy]);

  return (
    <div className="space-y-6">
      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          title="Total Reviews"
          value={analytics.total_reviews}
          icon={<CheckCircle className="text-blue-500" />}
        />
        <MetricCard
          title="Positive Sentiment"
          value={`${analytics.positive_percentage.toFixed(1)}%`}
          icon={<CheckCircle className="text-green-500" />}
        />
        <MetricCard
          title="Negative Sentiment"
          value={`${analytics.negative_percentage.toFixed(1)}%`}
          icon={<AlertCircle className="text-red-500" />}
        />
        <MetricCard
          title="Average Rating"
          value={`${analytics.average_rating.toFixed(1)}⭐`}
          icon={<TrendingUp className="text-yellow-500" />}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pie Chart - Sentiment Distribution */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-800 mb-4">Sentiment Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={sentimentData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {sentimentData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Line Chart - Sentiment Trend */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-800 mb-4">Sentiment Trend (7 Days)</h3>
          {hasTrendData ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="label" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="positive" stroke="#10b981" strokeWidth={2} />
                <Line type="monotone" dataKey="negative" stroke="#ef4444" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[300px] flex items-center justify-center text-center px-8">
              <p className="text-gray-500 text-sm">
                No reviews in the last 7 days yet. This chart plots real review dates —
                it'll fill in as new reviews come in, rather than showing placeholder data.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Reviews (filterable, sortable) */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-4">
          <h3 className="text-lg font-bold text-gray-800">Reviews</h3>
          <div className="flex items-center gap-2">
            <button
              onClick={() => downloadReviewsAsCSV(filteredSortedReviews, productName)}
              disabled={filteredSortedReviews.length === 0}
              title="Export the currently filtered/sorted reviews as CSV"
              className="text-sm text-gray-600 hover:text-gray-900 border rounded-lg px-3 py-1.5 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Export CSV
            </button>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
              className="border rounded-lg px-3 py-1.5 text-sm text-gray-700"
            >
              <option value="newest">Newest first</option>
              <option value="oldest">Oldest first</option>
              <option value="rating_high">Highest rating</option>
              <option value="rating_low">Lowest rating</option>
            </select>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 mb-4">
          {(['ALL', 'POSITIVE', 'NEGATIVE', 'NEUTRAL', 'MIXED', 'PENDING'] as const).map((s) => (
            <button
              key={s}
              onClick={() => setSentimentFilter(s)}
              className={`text-xs font-semibold px-3 py-1.5 rounded-full border transition ${
                sentimentFilter === s
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400'
              }`}
            >
              {s === 'ALL' ? 'All' : s === 'PENDING' ? 'Analyzing' : s.charAt(0) + s.slice(1).toLowerCase()}
              {' '}({sentimentCounts[s] || 0})
            </button>
          ))}
        </div>

        <div className="space-y-3 max-h-96 overflow-y-auto">
          {filteredSortedReviews.length === 0 ? (
            <p className="text-gray-500 text-sm text-center py-6">No reviews match this filter.</p>
          ) : (
            filteredSortedReviews.map((review) => (
              <ReviewItem
                key={review.review_id}
                review={review}
                apiClient={apiClient}
                productId={productId}
                onDeleted={onReviewDeleted}
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
};

// Metric Card Component
const MetricCard: React.FC<{
  title: string;
  value: string | number;
  icon: React.ReactNode;
}> = ({ title, value, icon }) => (
  <div className="bg-white rounded-lg shadow-md p-4 border-l-4 border-blue-500">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm text-gray-600">{title}</p>
        <p className="text-2xl font-bold text-gray-800 mt-1">{value}</p>
      </div>
      <div className="text-3xl">{icon}</div>
    </div>
  </div>
);

// Review Item Component
const ReviewItem: React.FC<{
  review: Review;
  apiClient: APIClient;
  productId: string;
  onDeleted: () => void;
}> = ({ review, apiClient, productId, onDeleted }) => {
  const [expanded, setExpanded] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const sentimentColors = {
    POSITIVE: 'bg-green-100 text-green-800',
    NEGATIVE: 'bg-red-100 text-red-800',
    NEUTRAL: 'bg-gray-100 text-gray-800',
    MIXED: 'bg-yellow-100 text-yellow-800',
    PENDING: 'bg-blue-50 text-blue-700',
  };

  const handleDelete = async () => {
    if (!window.confirm('Delete this review? This can\'t be undone.')) return;
    try {
      setDeleting(true);
      await apiClient.deleteReview(productId, review.review_id);
      onDeleted();
    } catch (err) {
      window.alert(err instanceof Error ? err.message : 'Failed to delete review');
      setDeleting(false);
    }
  };

  return (
    <div className="border rounded-lg p-3 hover:bg-gray-50 transition">
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-2 mb-2">
        <div>
          <p className="font-semibold text-gray-800">
            {review.rating}⭐ • {review.user_id}
          </p>
          <p className="text-xs text-gray-500">
            {new Date(review.created_at).toLocaleDateString()}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {review.use_deep_insight && review.sentiment !== 'PENDING' && (
            <span
              className="px-2 py-1 rounded text-xs font-semibold bg-purple-100 text-purple-800 max-w-[220px] truncate inline-block"
              title={review.deep_insight_model ? `Analyzed by ${review.deep_insight_model}` : undefined}
            >
              AI{review.deep_insight_model ? ` · ${review.deep_insight_model}` : ' deep insight'}
            </span>
          )}
          {review.sentiment === 'PENDING' ? (
            <span className={`flex items-center gap-1 px-2 py-1 rounded text-xs font-semibold ${sentimentColors.PENDING}`}>
              <Clock size={12} className="animate-spin" />
              Analyzing...
            </span>
          ) : (
            <span className={`px-2 py-1 rounded text-xs font-semibold ${sentimentColors[review.sentiment]}`}>
              {review.sentiment}
            </span>
          )}
          <button
            onClick={handleDelete}
            disabled={deleting}
            title="Delete review"
            className="text-gray-300 hover:text-red-600 transition disabled:opacity-50"
          >
            {deleting ? <Clock size={14} className="animate-spin" /> : <Trash2 size={14} />}
          </button>
        </div>
      </div>
      <p
        className={`text-sm text-gray-700 cursor-pointer ${expanded ? '' : 'line-clamp-2'}`}
        onClick={() => setExpanded((e) => !e)}
        title={expanded ? 'Click to collapse' : 'Click to read full review'}
      >
        {review.text}
      </p>
      {review.key_phrases.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {review.key_phrases.slice(0, 3).map((phrase, idx) => (
            <span key={idx} className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
              {phrase}
            </span>
          ))}
        </div>
      )}

      {/* LLM-derived output -- only present when the uploader checked
          "Use AI deep insight" and the OpenRouter call succeeded. */}
      {review.summary && (
        <div className="mt-3 pt-3 border-t border-purple-100">
          <p className="text-sm text-purple-900 italic">"{review.summary}"</p>
          {review.aspects && review.aspects.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {review.aspects.map((aspect, idx) => (
                <span key={idx} className="text-xs bg-purple-50 text-purple-700 border border-purple-200 px-2 py-1 rounded">
                  {aspect}{review.aspect_sentiments?.[aspect] ? ` · ${review.aspect_sentiments[aspect]}` : ''}
                </span>
              ))}
            </div>
          )}
          {review.action_items && review.action_items.length > 0 && (
            <ul className="mt-2 text-xs text-gray-600 list-disc list-inside">
              {review.action_items.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
};

// =====================================================
// DASHBOARD (the actual app -- only rendered once signed in)
// =====================================================

const Dashboard: React.FC<{ apiClient: APIClient; onLogout: () => void; userEmail?: string }> = ({ apiClient, onLogout, userEmail }) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<string | null>(null);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);
  const [productsError, setProductsError] = useState<string | null>(null);
  const [analyticsError, setAnalyticsError] = useState<string | null>(null);
  const [showAddProduct, setShowAddProduct] = useState(false);
  const [productSearch, setProductSearch] = useState('');
  const [autoPolling, setAutoPolling] = useState(false);
  // Persists across re-renders (unlike a plain closure variable), so the
  // attempt count actually accumulates across repeated polls instead of
  // resetting every time a new `reviews`/`products` array comes back.
  const pollAttemptsRef = useRef(0);

  // Load products on mount
  useEffect(() => {
    const loadProducts = async () => {
      try {
        setLoading(true);
        setProductsError(null);
        const data = await apiClient.getProducts();
        setProducts(data);
        if (data.length > 0 && !selectedProduct) {
          setSelectedProduct(data[0].product_id);
        }
      } catch (err) {
        // Previously this only logged to the console -- a failed
        // request and a genuinely empty product list rendered
        // identically ("No products yet"), so a broken backend was
        // silently indistinguishable from a working, empty one.
        console.error('Failed to load products:', err);
        setProductsError(err instanceof Error ? err.message : 'Failed to load products');
      } finally {
        setLoading(false);
      }
    };

    loadProducts();
  }, [refreshKey]);

  // Load analytics and reviews when product is selected
  useEffect(() => {
    if (!selectedProduct) return;

    const loadData = async () => {
      try {
        setAnalyticsError(null);
        const [analyticsData, reviewsData] = await Promise.all([
          apiClient.getProductAnalytics(selectedProduct),
          apiClient.getProductReviews(selectedProduct),
        ]);
        setAnalytics(analyticsData);
        setReviews(reviewsData);
      } catch (err) {
        console.error('Failed to load analytics:', err);
        setAnalyticsError(err instanceof Error ? err.message : 'Failed to load analytics');
      }
    };

    loadData();
    // Previously only [selectedProduct] -- refetched when switching to a
    // different product, but never when staying on the same one after an
    // upload completes or after backend processing (sentiment analysis,
    // deep insight) finishes asynchronously in the background. Reviews
    // could sit showing a stale PENDING snapshot indefinitely unless you
    // happened to switch away and back. refreshKey (bumped by
    // handleUploadComplete) now forces a refetch too.
  }, [selectedProduct, refreshKey]);

  // Auto-polling: while there's genuinely something to wait on (no
  // products loaded yet, or any currently-loaded review still shows
  // PENDING), automatically re-check every few seconds instead of
  // requiring a manual Refresh click or a full page reload to see
  // progress. Capped at 20 attempts (~80s) so it doesn't poll forever
  // if something's actually stuck -- manual Refresh remains available
  // after that, and resets the counter for a fresh attempt.
  useEffect(() => {
    const hasPendingReviews = reviews.some((r) => r.sentiment === 'PENDING');
    const needsPolling = (!loading && products.length === 0 && !productsError) || hasPendingReviews;

    if (!needsPolling) {
      pollAttemptsRef.current = 0;
      setAutoPolling(false);
      return;
    }

    if (pollAttemptsRef.current >= 20) {
      setAutoPolling(false);
      return;
    }

    setAutoPolling(true);
    const timeoutId = setTimeout(() => {
      pollAttemptsRef.current += 1;
      setRefreshKey((k) => k + 1);
    }, 4000);

    return () => clearTimeout(timeoutId);
  }, [products.length, reviews, productsError, loading]);

  const handleManualRefresh = () => {
    pollAttemptsRef.current = 0; // give auto-polling a fresh budget too
    setRefreshKey((k) => k + 1);
  };

  const [toast, setToast] = useState<string | null>(null);

  const handleUploadComplete = () => {
    pollAttemptsRef.current = 0; // fresh polling budget for this new batch
    setRefreshKey((prev) => prev + 1);
    setToast('Upload received — reviews are being processed. This page will auto-refresh for about a minute; use Refresh if you need to check sooner or longer.');
    setTimeout(() => setToast(null), 6000);
  };

  const handleProductDeleted = (productId: string) => {
    if (selectedProduct === productId) {
      setSelectedProduct(null);
      setAnalytics(null);
      setReviews([]);
    }
    setRefreshKey((prev) => prev + 1);
    setToast('Product and its reviews deleted.');
    setTimeout(() => setToast(null), 4000);
  };

  const selectedProductData = products.find((p) => p.product_id === selectedProduct);

  return (
    <div className="min-h-screen bg-gray-100">
      <Header onLogout={onLogout} userEmail={userEmail} />

      {toast && (
        <div className="fixed bottom-4 right-4 bg-gray-900 text-white text-sm px-4 py-3 rounded-lg shadow-lg max-w-sm z-50 flex items-start gap-2">
          <CheckCircle size={18} className="text-green-400 shrink-0 mt-0.5" />
          <span>{toast}</span>
        </div>
      )}

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* File Upload + Single Review Analysis */}
        <section className="mb-8 grid grid-cols-1 lg:grid-cols-2 gap-4">
          <FileUploader apiClient={apiClient} onUploadComplete={handleUploadComplete} />
          <SingleReviewAnalyzer apiClient={apiClient} />
        </section>

        {/* Products Section */}
        <section className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <h2 className="text-2xl font-bold text-gray-800">Products</h2>
              {autoPolling && (
                <span className="flex items-center gap-1.5 text-xs text-blue-600" title="Automatically checking for updates every few seconds">
                  <Clock size={12} className="animate-spin" />
                  Checking for updates...
                </span>
              )}
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleManualRefresh}
                className="text-sm text-gray-600 hover:text-gray-900 border rounded-lg px-3 py-1.5"
              >
                Refresh
              </button>
              {!showAddProduct && (
                <button
                  onClick={() => setShowAddProduct(true)}
                  className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold py-2 px-4 rounded-lg transition"
                >
                  + Add Product
                </button>
              )}
            </div>
          </div>
          {showAddProduct && (
            <AddProductForm
              apiClient={apiClient}
              onCreated={() => {
                setShowAddProduct(false);
                setRefreshKey((k) => k + 1);
              }}
              onCancel={() => setShowAddProduct(false)}
            />
          )}
          {!productsError && !loading && products.length > 0 && (
            <input
              type="text"
              placeholder="Search products by name or category..."
              value={productSearch}
              onChange={(e) => setProductSearch(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 text-sm mb-4"
            />
          )}
          {productsError ? (
            <div className="bg-red-50 border border-red-200 rounded-lg p-6 flex items-start gap-3">
              <AlertCircle className="text-red-500 shrink-0 mt-0.5" size={20} />
              <div>
                <p className="text-red-800 font-semibold">Couldn't load products</p>
                <p className="text-red-600 text-sm mt-1">{productsError}</p>
                <button
                  onClick={handleManualRefresh}
                  className="text-red-700 text-sm font-medium underline mt-2"
                >
                  Try again
                </button>
              </div>
            </div>
          ) : loading ? (
            <div className="text-center py-12">
              <Clock className="inline-block animate-spin text-blue-600" size={48} />
              <p className="text-gray-600 mt-2">Loading products...</p>
            </div>
          ) : products.length === 0 ? (
            <div className="bg-white rounded-lg shadow-md p-8 text-center">
              <p className="text-gray-600">No products yet. Create your first product!</p>
            </div>
          ) : (
            (() => {
              const filteredProducts = productSearch.trim()
                ? products.filter(
                    (p) =>
                      p.name.toLowerCase().includes(productSearch.trim().toLowerCase()) ||
                      (p.category || '').toLowerCase().includes(productSearch.trim().toLowerCase())
                  )
                : products;

              return filteredProducts.length === 0 ? (
                <div className="bg-white rounded-lg shadow-md p-8 text-center">
                  <p className="text-gray-600">No products match "{productSearch}".</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {filteredProducts.map((product) => (
                    <ProductCard
                      key={product.product_id}
                      product={product}
                      onSelect={setSelectedProduct}
                      apiClient={apiClient}
                      onDeleted={() => handleProductDeleted(product.product_id)}
                      isSelected={product.product_id === selectedProduct}
                    />
                  ))}
                </div>
              );
            })()
          )}
        </section>

        {/* Analytics Section */}
        {selectedProduct && analyticsError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 flex items-start gap-3 mb-8">
            <AlertCircle className="text-red-500 shrink-0 mt-0.5" size={20} />
            <div>
              <p className="text-red-800 font-semibold">Couldn't load analytics</p>
              <p className="text-red-600 text-sm mt-1">{analyticsError}</p>
            </div>
          </div>
        )}
        {selectedProduct && selectedProductData && analytics && (
          <section>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-800">
                  Analytics: {selectedProductData.name}
                </h2>
                <p className="text-gray-600 flex items-center gap-2">
                  Sentiment analysis for {analytics.total_reviews} reviews
                  {autoPolling && (
                    <span className="flex items-center gap-1 text-xs text-blue-600" title="Automatically checking for updates every few seconds">
                      <Clock size={12} className="animate-spin" />
                      Checking for updates...
                    </span>
                  )}
                </p>
              </div>
              <button
                onClick={handleManualRefresh}
                className="text-sm text-blue-600 hover:text-blue-800 font-medium border border-blue-200 rounded-lg px-3 py-1.5"
                title="Sentiment and AI deep-insight analysis finish a few seconds after upload -- refresh to see the latest"
              >
                Refresh
              </button>
            </div>
            <AnalyticsDashboard
              analytics={analytics}
              reviews={reviews}
              apiClient={apiClient}
              productId={selectedProduct}
              productName={selectedProductData.name}
              onReviewDeleted={() => setRefreshKey((k) => k + 1)}
            />
          </section>
        )}
      </main>
    </div>
  );
};

// =====================================================
// SIGN-IN GATE
// =====================================================
// Cognito's Hosted UI already has both "Sign in" and "Sign up" on the
// same page (self-registration is enabled on the user pool), so one
// button covers both -- no separate signup form needed in this app.

const SignInGate: React.FC = () => {
  const auth = useAuth();

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-md p-10 text-center max-w-sm">
        <TrendingUp size={40} className="mx-auto text-blue-600 mb-4" />
        <h1 className="text-xl font-bold text-gray-800 mb-2">Review Sentiment Analyzer</h1>
        <p className="text-gray-600 mb-6">Sign in to view products and sentiment analytics.</p>
        <button
          onClick={() => auth.signinRedirect()}
          className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-3 rounded-lg font-semibold transition"
        >
          <LogIn size={18} />
          Sign in / Sign up
        </button>
      </div>
    </div>
  );
};

// =====================================================
// AUTH-AWARE ROOT (decides: loading / error / sign-in / dashboard)
// =====================================================

const AuthenticatedRoot: React.FC = () => {
  const auth = useAuth();

  // react-oidc-context needs a stable APIClient instance per token, not a
  // fresh one on every render (that would drop in-flight request state).
  const apiClient = useMemo(
    () => new APIClient(import.meta.env.VITE_API_URL, auth.user?.id_token ?? null),
    [auth.user?.id_token]
  );

  const signOutRedirect = () => {
    const clientId = import.meta.env.VITE_COGNITO_CLIENT_ID;
    const cognitoDomain = import.meta.env.VITE_COGNITO_DOMAIN;
    const logoutUri = import.meta.env.VITE_COGNITO_LOGOUT_URI;
    auth.removeUser();
    window.location.href = `https://${cognitoDomain}/logout?client_id=${clientId}&logout_uri=${encodeURIComponent(logoutUri)}`;
  };

  if (auth.isLoading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <Clock className="animate-spin text-blue-600" size={48} />
      </div>
    );
  }

  if (auth.error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-md p-8 text-center max-w-md">
          <AlertCircle className="mx-auto text-red-500 mb-3" size={36} />
          <p className="text-gray-800 font-semibold mb-1">Sign-in error</p>
          <p className="text-gray-600 text-sm">{auth.error.message}</p>
        </div>
      </div>
    );
  }

  if (!auth.isAuthenticated) {
    return <SignInGate />;
  }

  return <Dashboard apiClient={apiClient} onLogout={signOutRedirect} userEmail={auth.user?.profile.email} />;
};

// =====================================================
// MAIN APP COMPONENT (exported) -- wires up the Cognito Hosted UI
// =====================================================
// Values come from Vite env vars (.env) rather than being hardcoded, so
// the same build works across environments. See 04_deployment_testing_guide.md
// for where each of these comes from (Cognito app client / domain pages).

const cognitoAuthConfig = {
  authority: import.meta.env.VITE_COGNITO_AUTHORITY, // e.g. https://cognito-idp.ap-southeast-1.amazonaws.com/<user-pool-id>
  client_id: import.meta.env.VITE_COGNITO_CLIENT_ID,
  redirect_uri: import.meta.env.VITE_COGNITO_REDIRECT_URI, // e.g. https://<your-amplify-domain>/callback
  response_type: 'code',
  scope: 'email openid profile',
  // Cognito redirects back to /callback with ?code&state in the query
  // string. Once react-oidc-context has consumed those, send the user
  // back to / -- previously this only stripped the query string and left
  // /callback itself in the URL bar permanently, which was harmless
  // (the app doesn't do path-based routing) but confusing to look at.
  onSigninCallback: () => {
    window.history.replaceState({}, document.title, '/');
  },
};

export default function App() {
  return (
    <AuthProvider {...cognitoAuthConfig}>
      <AuthenticatedRoot />
    </AuthProvider>
  );
}
