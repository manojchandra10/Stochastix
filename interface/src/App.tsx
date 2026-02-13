import { useState, useEffect } from 'react';
import {LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine
       } from 'recharts';
import {fetchForecast, fetchScoreboard, type ForecastPoint} from './services/api';
import {TrendingUp, Activity, BarChart3, Settings, HelpCircle, Moon, Sun, Share2, ArrowRightLeft
} from 'lucide-react';

// Config and Data
const getFlagUrl = (code: string) => {
  const map: Record<string, string> = {
    GBP: 'gb', INR: 'in', USD: 'us', EUR: 'eu', JPY: 'jp', CHF: 'ch',
    AUD: 'au', CAD: 'ca', CNY: 'cn', HKD: 'hk', NZD: 'nz', SGD: 'sg',
    ZAR: 'za', SEK: 'se', NOK: 'no', DKK: 'dk', PLN: 'pl', HUF: 'hu',
    CZK: 'cz', RON: 'ro', ISK: 'is', TRY: 'tr', BRL: 'br', IDR: 'id',
    ILS: 'il', KRW: 'kr', MXN: 'mx', MYR: 'my', PHP: 'ph', THB: 'th'
  };
  return `https://flagcdn.com/w40/${map[code] || 'un'}.png`;
};
const CURRENCIES = [
  { code: 'GBP', name: 'British Pound', keywords: 'uk, england, sterling, united kingdom' },
  { code: 'INR', name: 'Indian Rupee', keywords: 'india, bharat' },
  { code: 'USD', name: 'US Dollar', keywords: 'usa, america, united states' },
  { code: 'EUR', name: 'Euro', keywords: 'europe, germany, france, italy, spain' },
  { code: 'JPY', name: 'Japanese Yen', keywords: 'japan, asia' },
  { code: 'CHF', name: 'Swiss Franc', keywords: 'switzerland, swiss' },
  { code: 'AUD', name: 'Australian Dollar', keywords: 'australia, oz' },
  { code: 'CAD', name: 'Canadian Dollar', keywords: 'canada' },
  { code: 'CNY', name: 'Chinese Yuan', keywords: 'china, renminbi' },
  { code: 'HKD', name: 'Hong Kong Dollar', keywords: 'hong kong' },
  { code: 'NZD', name: 'New Zealand Dollar', keywords: 'new zealand, kiwi' },
  { code: 'SGD', name: 'Singapore Dollar', keywords: 'singapore' },
  { code: 'ZAR', name: 'South African Rand', keywords: 'south africa, africa' },
  { code: 'SEK', name: 'Swedish Krona', keywords: 'sweden' },
  { code: 'NOK', name: 'Norwegian Krone', keywords: 'norway' },
  { code: 'DKK', name: 'Danish Krone', keywords: 'denmark' },
  { code: 'PLN', name: 'Polish Zloty', keywords: 'poland' },
  { code: 'HUF', name: 'Hungarian Forint', keywords: 'hungary' },
  { code: 'CZK', name: 'Czech Koruna', keywords: 'czech republic' },
  { code: 'RON', name: 'Romanian Leu', keywords: 'romania' },
  { code: 'ISK', name: 'Icelandic Krona', keywords: 'iceland' },
  { code: 'TRY', name: 'Turkish Lira', keywords: 'turkey' },
  { code: 'BRL', name: 'Brazilian Real', keywords: 'brazil' },
  { code: 'IDR', name: 'Indonesian Rupiah', keywords: 'indonesia' },
  { code: 'ILS', name: 'Israeli Shekel', keywords: 'israel' },
  { code: 'KRW', name: 'South Korean Won', keywords: 'korea' },
  { code: 'MXN', name: 'Mexican Peso', keywords: 'mexico' },
  { code: 'MYR', name: 'Malaysian Ringgit', keywords: 'malaysia' },
  { code: 'PHP', name: 'Philippine Peso', keywords: 'philippines' },
  { code: 'THB', name: 'Thai Baht', keywords: 'thailand' }
];

// SCORECARD COMPONENT
const OracleScorecard = ({ isSidebar = false }: { isSidebar?: boolean }) => {
  const [auditData, setAuditData] = useState<any[]>([]);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchScoreboard();
        if (data && data.length > 0) {
          setAuditData(data);
        }
      } catch (err) {
        console.error('Failed to load scoreboard', err);
      }
    };
    loadData();
  }, []);

  const getColor = (status: string) => {
    if (status === 'success') return '#00C851';
    if (status === 'danger') return '#ff4444';
    return '#33b5e5';
  };

  return (
    <div
      className={isSidebar ? 'audit-scorecard-box audit-glow' : ''}
      style={{
        background: isSidebar ? 'var(--bg-sidebar)' : 'var(--bg-input)',
        padding: isSidebar ? '1.5rem' : '25px',
        borderRadius: '12px',
        border: '1px solid var(--border-color)',
        width: '100%',
        boxSizing: 'border-box',
        color: isSidebar ? 'var(--text-sidebar)' : 'var(--text-main)'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
        <Activity size={isSidebar ? 18 : 22} color="var(--brand-orange)" />
        <h3
          style={{
            margin: 0,
            textTransform: 'uppercase',
            fontSize: isSidebar ? '0.75rem' : '1rem',
            color: isSidebar ? 'var(--brand-orange)' : 'inherit'
          }}
        >
          24h Performance Audit
        </h3>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table
          style={{
            width: '100%',
            borderCollapse: 'collapse',
            textAlign: 'left',
            fontSize: isSidebar ? '0.75rem' : '0.9rem'
          }}
        >
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
              <th style={{ padding: '10px 5px' }}>Currency</th>
              <th style={{ padding: '10px 5px' }}>Predicted</th>
              <th style={{ padding: '10px 5px' }}>Actual</th>
              {!isSidebar && <th style={{ padding: '10px 5px' }}>Trust Label</th>}
            </tr>
          </thead>

          <tbody>
            {auditData.length === 0 ? (
              <tr>
                <td colSpan={4} style={{ padding: '15px', textAlign: 'center', color: 'var(--text-secondary)' }}>
                  Awaiting market data...
                </td>
              </tr>
            ) : (
              auditData.map((item, i) => (
                <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '12px 5px', fontWeight: 700 }}>{item.currency}</td>
                  <td style={{ padding: '12px 5px', fontFamily: 'monospace' }}>{item.pred}</td>
                  <td
                    style={{
                      padding: '12px 5px',
                      fontFamily: 'monospace',
                      color: getColor(item.status),
                      fontWeight: 700
                    }}
                  >
                    {item.actual}
                  </td>
                  {!isSidebar && (
                    <td style={{ padding: '12px 5px' }}>
                      <span style={{ color: getColor(item.status), fontWeight: 700 }}>{item.label}</span>
                    </td>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [fromCurr, setFromCurr] = useState('GBP');
  const [toCurr, setToCurr] = useState('INR');
  const [data, setData] = useState<ForecastPoint[]>([]);
  const [sentiment, setSentiment] = useState<SentimentResponse['sentiment'] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const CURRENCIES = [
    { code: 'GBP', name: 'British Pound' },
    { code: 'USD', name: 'US Dollar' },
    { code: 'EUR', name: 'Euro' },
    { code: 'INR', name: 'Indian Rupee' },
    { code: 'JPY', name: 'Japanese Yen' }
  ];

  const formatToUKDate = (isoDate: string) => {
    if (!isoDate) return '';
    const [year, month, day] = isoDate.split('-');
    return `${day}-${month}-${year}`;
  };

  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  }, [darkMode]);

  const handleSwap = () => {
    const temp = fromCurr;
    setFromCurr(toCurr);
    setToCurr(temp);
  };

  const handlePredict = async () => {
    setLoading(true);
    setError('');
    setSentiment(null);

    try {
      const [forecastResult, sentimentResult] = await Promise.all([
        fetchForecast(fromCurr, toCurr, 30),
        fetchSentiment(fromCurr, toCurr)
      ]);
      // directly use the data from the server.
      // The server handles the weekend calculations.
      setData(forecastResult.forecast);
      setSentiment(sentimentResult.sentiment);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch data.');
    } finally {
      setLoading(false);
    }
  };

  const getMoodColor = (score: number) => {
    if (score > 0.05) return '#00C851';
    if (score < -0.05) return '#ff4444';
    return '#FF851B';
  };

  // If the server includes an 'indicative' point, find the date of the last one.
  const lastIndicativeDate = data.filter(d => d.type === 'indicative').pop()?.date;

  return (
    <div className="main-wrapper">
      <nav>
        <div className="logo-text">
          <Activity size={28} color="#FF851B" strokeWidth={2.5} />
          Stochastix
        </div>
        <button className="theme-toggle" onClick={() => setDarkMode(!darkMode)}>
          {darkMode ? <Sun size={20} /> : <Moon size={20} />}
        </button>
      </nav>

      <div className="hero">
        <h1>
          Predict The Market.
          <br />
          Without <span className="hero-highlight">The Noise.</span>
        </h1>
        <p>AI-Powered Exchange Rate Intelligence. No Logs. No Lag. Pure Data.</p>
      </div>

      <div className="app-container">
        <div className="sidebar-shell">
          <div className="sidebar">
            <div className="menu-label">Tools</div>
            <div className="menu-item active">
              <TrendingUp size={20} /> Forecast
            </div>
            <div className="menu-item">
              <BarChart3 size={20} /> Analytics
            </div>
            <div className="menu-item">
              <Settings size={20} /> Settings
            </div>
            <div className="menu-item">
              <HelpCircle size={20} /> Support
            </div>

            <div className="donate-card">
              <div className="donate-title">Share Alpha</div>
              <div className="donate-sub">Help others find this tool.</div>
              <button className="donate-btn" onClick={() => alert('Link copied to clipboard!')}>
                <Share2 size={16} style={{ display: 'inline', marginRight: '5px' }} /> Share
              </button>
            </div>
          </div>

          {data.length > 0 && (
            <div className="sidebar-secondary-container">
              <OracleScorecard isSidebar={true} />
            </div>
          )}
        </div>

        <div className="workspace">
          <div className="tool-header">
            <h2>Market Oracle</h2>
            <p>Select your currency pair to generate a 30-day neural forecast.</p>
          </div>

          <div className="control-zone">
            <div className="pair-grid">
              <div className="select-wrapper">
                <label style={{ display: 'block', fontSize: '0.8rem', marginBottom: '5px', color: 'var(--text-secondary)' }}>
                  Base Currency
                </label>
                <select
                  className="select-box"
                  value={fromCurr}
                  onChange={(e) => setFromCurr(e.target.value)}
                  style={{ width: '100%' }}
                >
                  {CURRENCIES.map((c) => (
                    <option key={c.code} value={c.code}>{c.code} - {c.name}</option>
                  ))}
                </select>
              </div>

              <div className="swap-col">
                <button
                  onClick={handleSwap}
                  className="swap-btn-style"
                  style={{
                    background: 'none',
                    border: '1px solid var(--border-color)',
                    borderRadius: '50%',
                    width: '40px',
                    height: '40px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer',
                    color: 'var(--brand-orange)'
                  }}
                >
                  <ArrowRightLeft size={20} />
                </button>
              </div>

              <div className="select-wrapper">
                <label style={{ display: 'block', fontSize: '0.8rem', marginBottom: '5px', color: 'var(--text-secondary)' }}>
                  Target Currency
                </label>
                <select
                  className="select-box"
                  value={toCurr}
                  onChange={(e) => setToCurr(e.target.value)}
                  style={{ width: '100%' }}
                >
                  {CURRENCIES.map((c) => (
                    <option key={c.code} value={c.code}>{c.code} - {c.name}</option>
                  ))}
                </select>
              </div>
            </div>

            <button className="primary-action-btn" onClick={handlePredict} disabled={loading}>
              {loading ? 'Processing...' : <><TrendingUp size={22} /> Analyze & Predict</>}
            </button>

            {error && (
              <div style={{ color: '#ff4444', marginTop: '20px', fontWeight: 700, textAlign: 'center' }}>
                {error}
              </div>
            )}
          </div>

          {data.length === 0 && !loading && (
            <div className="workspace-scorecard">
              <OracleScorecard isSidebar={false} />
            </div>
          )}

          {(data.length > 0 || sentiment) && (
            <div className="results-grid">
              {/* --- CHART CARD --- */}
              <div
                className="chart-card"
                style={{
                  gridColumn: '1 / -1',
                  height: '450px',
                  background: 'var(--bg-input)',
                  padding: '20px',
                  borderRadius: '12px',
                  border: '1px solid var(--border-color)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px', gap: '12px', flexWrap: 'wrap' }}>
                  <h3 style={{ margin: 0, textTransform: 'uppercase', fontSize: '1rem', color: 'var(--brand-orange)' }}>
                    Historical Context + 30-Day Forecast
                  </h3>
                  <span style={{ fontWeight: 700 }}>
                    {fromCurr} / {toCurr}
                  </span>
                </div>

                <ResponsiveContainer width="100%" height="90%">
                  <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={darkMode ? '#333' : '#eee'} />
                    <XAxis
                      dataKey="date"
                      tick={{ fontSize: 11, fill: darkMode ? '#888' : '#555' }}
                      tickFormatter={formatToUKDate}
                      minTickGap={45}
                      stroke={darkMode ? '#444' : '#ddd'}
                    />
                    <YAxis
                      domain={['auto', 'auto']}
                      tick={{ fontSize: 11, fill: darkMode ? '#888' : '#555' }}
                      stroke={darkMode ? '#444' : '#ddd'}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: darkMode ? '#222' : '#fff',
                        borderRadius: '8px',
                        border: '1px solid var(--brand-orange)',
                        color: darkMode ? '#fff' : '#000'
                      }}
                      labelFormatter={(label) => formatToUKDate(String(label))}
                      formatter={(value: any, _name: any, props: any) => {
                        const type = props.payload?.type;
                        let typeLabel = 'AI Forecast';
                        if (type === 'history') typeLabel = 'Real History';
                        if (type === 'indicative') typeLabel = 'Weekend Indicative';
                        return [Number(value).toFixed(4), typeLabel];
                      }}
                    />
                    {data.length > 0 && (
                      <ReferenceLine
                        x={lastIndicativeDate || data.filter((d) => d.type === 'history').pop()?.date}
                        stroke="red"
                        strokeWidth={1}
                        strokeDasharray="3 3"
                        label={{ position: 'top', value: 'TODAY', fill: 'red', fontSize: 12, fontWeight: 'bold' }}
                      />
                    )}
                    <Line
                      type="monotone"
                      dataKey="rate"
                      stroke="#FF851B"
                      strokeWidth={3}
                      dot={false}
                      activeDot={{ r: 6, fill: '#FF851B' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* TABLE CARD*/}
              <div
                className="data-card forecast-table-card"
                style={{
                  gridColumn: '1 / -1',
                  background: 'var(--bg-input)',
                  padding: '20px',
                  borderRadius: '12px',
                  border: '1px solid var(--border-color)',
                  maxHeight: '300px',
                  overflowY: 'auto'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '15px' }}>
                  <BarChart3 size={20} color="var(--brand-orange)" />
                  <h3 style={{ margin: 0, textTransform: 'uppercase', fontSize: '0.9rem' }}>Upcoming Forecast</h3>
                </div>

                <table className="data-table" style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem', textAlign: 'left' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
                      <th style={{ padding: '10px' }}>Date</th>
                      <th style={{ padding: '10px', textAlign: 'right' }}>Predicted Rate ({fromCurr}/{toCurr})</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data
                      .filter((point) => {
                        if (point.type === 'forecast') return true;
                        // ONLY show the Indicative row if it's the LATEST one.
                        if (point.type === 'indicative') return point.date === lastIndicativeDate;
                        return false;
                      })
                      .map((point, index) => (
                        <tr
                          key={index}
                          style={{
                            borderBottom: '1px solid rgba(255,255,255,0.05)',
                            background: point.type === 'indicative'
                              ? 'rgba(255, 133, 27, 0.15)'
                              : index === 0 ? 'rgba(255, 133, 27, 0.05)' : 'transparent'
                          }}
                        >
                          <td style={{ padding: '10px', fontWeight: (index === 0 || point.type === 'indicative') ? 700 : 500 }}>
                            {formatToUKDate(point.date)}{' '}
                            {(point.type === 'indicative' || (index === 0 && point.type === 'forecast')) && (
                              <span style={{ fontSize: '0.7rem', color: 'var(--brand-orange)', marginLeft: '5px' }}>
                                {point.type === 'indicative' ? '(TODAY • INDICATIVE)' : '(TODAY)'}
                              </span>
                            )}
                          </td>
                          <td style={{
                            padding: '10px',
                            fontFamily: 'monospace',
                            fontSize: '1rem',
                            textAlign: 'right',
                            color: 'var(--text-primary)',
                            fontStyle: point.type === 'indicative' ? 'italic' : 'normal',
                            fontWeight: (index === 0 || point.type === 'indicative') ? 700 : 400
                          }}>
                            {point.rate.toFixed(4)}
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>

      <footer>
        <p>© 2026 Stochastix. Open Source Financial Intelligence.</p>
        <p style={{ marginTop: '15px', fontSize: '0.8rem', color: '#555' }}>
          Made with <span style={{ color: 'red' }}>&#10084;</span> by M
        </p>
      </footer>
    </div>
  );
}

export default App;
