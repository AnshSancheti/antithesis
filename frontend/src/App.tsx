import { useCallback, useEffect, useMemo, useState } from 'react';
import './App.css';

const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000';
const SESSION_STORAGE_KEY = 'phrase-quiz-session-id';

type PhraseOption = {
  id: number;
  text: string;
  totalVotes: number;
};

type PhrasePairPayload = {
  id: number;
  phraseA: PhraseOption;
  phraseB: PhraseOption;
  totalVotes: number;
};

type QuizResponse = {
  pairs: PhrasePairPayload[];
};

type VoteStatus = 'idle' | 'submitting' | 'error' | 'success';

function generateSessionId(): string {
  const fallbackId =
    typeof crypto !== 'undefined' && 'randomUUID' in crypto
      ? crypto.randomUUID()
      : `${Date.now()}-${Math.random().toString(16).slice(2)}`;

  if (typeof window === 'undefined') {
    return fallbackId;
  }

  const existing = window.localStorage.getItem(SESSION_STORAGE_KEY);
  if (existing && existing.trim().length > 0) {
    return existing;
  }

  window.localStorage.setItem(SESSION_STORAGE_KEY, fallbackId);
  return fallbackId;
}

function formatPercentage(part: number, total: number): string {
  if (total === 0) {
    return '0%';
  }
  const value = (part / total) * 100;
  return `${Math.round(value)}%`;
}

function App() {
  const [pairs, setPairs] = useState<PhrasePairPayload[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [voteStatus, setVoteStatus] = useState<VoteStatus>('idle');
  const [votedPairs, setVotedPairs] = useState<Set<number>>(new Set());
  const [activePairIndex, setActivePairIndex] = useState(0);

  const apiBaseUrl = useMemo(() => {
    const envUrl = import.meta.env.VITE_API_BASE_URL?.trim();
    return envUrl && envUrl.length > 0 ? envUrl.replace(/\/$/, '') : DEFAULT_API_BASE_URL;
  }, []);

  const sessionId = useMemo(generateSessionId, []);

  const fetchQuiz = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiBaseUrl}/api/quiz`);
      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const data = (await response.json()) as QuizResponse;
      setPairs(data.pairs ?? []);
      setActivePairIndex((index) => (data.pairs && data.pairs.length > index ? index : 0));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load quiz data');
    } finally {
      setIsLoading(false);
    }
  }, [apiBaseUrl]);

  useEffect(() => {
    void fetchQuiz();
  }, [fetchQuiz]);

  const handleVote = useCallback(
    async (pair: PhrasePairPayload, phraseId: number) => {
      if (voteStatus === 'submitting') {
        return;
      }

      setVoteStatus('submitting');
      setError(null);

      try {
        const response = await fetch(`${apiBaseUrl}/api/vote`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            phrasePairId: pair.id,
            selectedPhraseId: phraseId,
            sessionId,
          }),
        });

        if (response.status === 409) {
          setVoteStatus('error');
          setError('You have already voted for this pair.');
          return;
        }

        if (response.status === 404) {
          setVoteStatus('error');
          setError('This phrase pair is no longer available.');
          return;
        }

        if (!response.ok) {
          throw new Error(`Vote request failed with status ${response.status}`);
        }

        // Refresh totals after successful vote
        await fetchQuiz();

        setVoteStatus('success');
        setVotedPairs((prev) => new Set(prev).add(pair.id));
        setTimeout(() => setVoteStatus('idle'), 1500);
      } catch (err) {
        setVoteStatus('error');
        setError(err instanceof Error ? err.message : 'Unable to submit vote');
      }
    },
    [apiBaseUrl, fetchQuiz, sessionId, voteStatus]
  );

  const activePair = pairs[activePairIndex];
  const hasActivePair = Boolean(activePair);
  const votedThisPair = hasActivePair && votedPairs.has(activePair.id);

  return (
    <main className="app">
      <header className="app__header">
        <h1>Pick Your Phrase</h1>
        <p>Choose the phrase you prefer and see how others voted.</p>
      </header>

      {isLoading && <p className="status">Loading phrases…</p>}
      {error && !isLoading && <p className="status status--error">{error}</p>}

      {!isLoading && !error && !hasActivePair && (
        <p className="status">No phrase pairs available right now. Please check back later.</p>
      )}

      {!isLoading && !error && hasActivePair && (
        <section className="pair">
          <header className="pair__meta">
            <h2>Phrase Pair #{activePair.id}</h2>
            <div className="pair__totals">
              Total votes: {activePair.totalVotes}
            </div>
          </header>

          <div className="pair__options">
            {[activePair.phraseA, activePair.phraseB].map((phrase) => {
              const totalVotes = activePair.phraseA.totalVotes + activePair.phraseB.totalVotes;
              const percentage = formatPercentage(phrase.totalVotes, totalVotes);

              return (
                <article key={phrase.id} className="phrase-card">
                  <h3>{phrase.text}</h3>
                  <p className="phrase-card__votes">
                    {phrase.totalVotes} vote{phrase.totalVotes === 1 ? '' : 's'} ({percentage})
                  </p>
                  <button
                    type="button"
                    className="phrase-card__vote-button"
                    disabled={votedThisPair || voteStatus === 'submitting'}
                    onClick={() => handleVote(activePair, phrase.id)}
                  >
                    {votedThisPair ? 'Vote recorded' : 'Vote for this phrase'}
                  </button>
                </article>
              );
            })}
          </div>

          {pairs.length > 1 && (
            <nav className="pair__nav">
              {pairs.map((pair, index) => (
                <button
                  key={pair.id}
                  type="button"
                  className={`pair__nav-button${index === activePairIndex ? ' pair__nav-button--active' : ''}`}
                  onClick={() => setActivePairIndex(index)}
                >
                  Pair {pair.id}
                </button>
              ))}
            </nav>
          )}

          {voteStatus === 'success' && (
            <p className="status status--success">Thanks for voting!</p>
          )}
          {voteStatus === 'error' && error && (
            <p className="status status--error">{error}</p>
          )}
        </section>
      )}
    </main>
  );
}

export default App;
