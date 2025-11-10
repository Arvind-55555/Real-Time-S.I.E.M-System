import React, { useState } from 'react';
import { Upload, AlertTriangle, Activity, Shield, TrendingUp, Download, Play } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const SIEMAnalyzer = () => {
  const [file, setFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [logs, setLogs] = useState([]);

  const COLORS = ['#3b82f6', '#ef4444', '#f59e0b', '#10b981', '#8b5cf6'];

  const addLog = (message, type = 'info') => {
    setLogs(prev => [...prev, { message, type, timestamp: new Date().toISOString() }]);
  };

  const handleFileUpload = (event) => {
    const uploadedFile = event.target.files[0];
    if (uploadedFile) {
      setFile(uploadedFile);
      addLog(`File uploaded: ${uploadedFile.name} (${(uploadedFile.size / 1024).toFixed(2)} KB)`, 'success');
    }
  };

  const parseApacheLog = (line) => {
    const regex = /^(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) (\S+) \S+" (\d+) (\S+) "([^"]*)" "([^"]*)"/;
    const match = line.match(regex);
    
    if (match) {
      return {
        ip: match[1],
        timestamp: match[2],
        method: match[3],
        path: match[4],
        status: parseInt(match[5]),
        size: match[6] === '-' ? 0 : parseInt(match[6]),
        referer: match[7],
        userAgent: match[8]
      };
    }
    return null;
  };

  const detectAnomalies = (parsedLogs) => {
    const ipStats = {};
    
    parsedLogs.forEach(log => {
      if (!ipStats[log.ip]) {
        ipStats[log.ip] = {
          requests: 0,
          distinctPaths: new Set(),
          failures: 0,
          totalSize: 0,
          methods: new Set(),
          timestamps: []
        };
      }
      
      const stats = ipStats[log.ip];
      stats.requests++;
      stats.distinctPaths.add(log.path);
      if (log.status >= 400) stats.failures++;
      stats.totalSize += log.size;
      stats.methods.add(log.method);
      stats.timestamps.push(new Date(log.timestamp));
    });

    const anomalies = [];
    Object.entries(ipStats).forEach(([ip, stats]) => {
      const failRate = stats.failures / stats.requests;
      const distinctPathCount = stats.distinctPaths.size;
      let score = 0;
      let reasons = [];

      if (stats.requests > 100) {
        score += 30;
        reasons.push('High request volume');
      }

      if (distinctPathCount > 50) {
        score += 40;
        reasons.push('Path scanning detected');
      }

      if (failRate > 0.5) {
        score += 20;
        reasons.push('High failure rate');
      }

      if (stats.failures > 20) {
        score += 10;
        reasons.push('Possible brute-force');
      }

      if (score > 30) {
        anomalies.push({
          ip,
          score: Math.min(score, 100),
          requests: stats.requests,
          distinctPaths: distinctPathCount,
          failRate: (failRate * 100).toFixed(1),
          reasons: reasons.join(', ')
        });
      }
    });

    return { ipStats, anomalies: anomalies.sort((a, b) => b.score - a.score) };
  };

  const detectAttackPatterns = (parsedLogs) => {
    const patterns = {
      bruteForce: [],
      webshell: [],
      suspiciousUA: []
    };

    const authPaths = ['/login', '/wp-login.php', '/admin', '/auth'];
    const shellPatterns = ['/shell', '/wp-admin', '/phpmyadmin', '/xmlrpc.php', '/etc/passwd'];
    const suspiciousUAs = ['sqlmap', 'nikto', 'nmap', 'masscan', 'curl', 'wget', 'python'];

    const ipAuthFailures = {};

    parsedLogs.forEach(log => {
      if (authPaths.some(p => log.path.includes(p)) && log.status >= 400) {
        if (!ipAuthFailures[log.ip]) ipAuthFailures[log.ip] = 0;
        ipAuthFailures[log.ip]++;
      }

      if (shellPatterns.some(p => log.path.toLowerCase().includes(p))) {
        patterns.webshell.push({ ip: log.ip, path: log.path, timestamp: log.timestamp });
      }

      if (suspiciousUAs.some(ua => log.userAgent.toLowerCase().includes(ua))) {
        patterns.suspiciousUA.push({ ip: log.ip, ua: log.userAgent, path: log.path });
      }
    });

    Object.entries(ipAuthFailures).forEach(([ip, count]) => {
      if (count > 10) {
        patterns.bruteForce.push({ ip, attempts: count });
      }
    });

    return patterns;
  };

  const analyzeTimeSeries = (parsedLogs) => {
    const timeSlots = {};
    
    parsedLogs.forEach(log => {
      const date = new Date(log.timestamp);
      const minute = new Date(date.getFullYear(), date.getMonth(), date.getDate(), 
                              date.getHours(), date.getMinutes()).toISOString();
      
      if (!timeSlots[minute]) timeSlots[minute] = 0;
      timeSlots[minute]++;
    });

    const timeSeriesData = Object.entries(timeSlots)
      .map(([time, count]) => ({ time: time.slice(11, 16), count }))
      .sort((a, b) => a.time.localeCompare(b.time));

    const avgRequests = timeSeriesData.reduce((sum, d) => sum + d.count, 0) / timeSeriesData.length;
    const bursts = timeSeriesData.filter(d => d.count > avgRequests * 3);

    return { timeSeriesData, bursts };
  };

  const analyzeData = async () => {
    if (!file) {
      addLog('Please upload a log file first', 'error');
      return;
    }

    setAnalyzing(true);
    addLog('Starting SIEM analysis...', 'info');

    try {
      const text = await file.text();
      const lines = text.split('\n').filter(line => line.trim());
      
      addLog(`Parsing ${lines.length} log entries...`, 'info');
      
      const parsedLogs = lines
        .map(parseApacheLog)
        .filter(log => log !== null);

      addLog(`Successfully parsed ${parsedLogs.length} entries`, 'success');

      const validLogs = parsedLogs.filter(log => log.timestamp && log.ip);
      addLog(`Data quality: ${validLogs.length}/${parsedLogs.length} valid entries`, 'info');

      const ipCounts = {};
      const pathCounts = {};
      const statusCounts = {};
      
      validLogs.forEach(log => {
        ipCounts[log.ip] = (ipCounts[log.ip] || 0) + 1;
        pathCounts[log.path] = (pathCounts[log.path] || 0) + 1;
        statusCounts[log.status] = (statusCounts[log.status] || 0) + 1;
      });

      const topIPs = Object.entries(ipCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)
        .map(([ip, count]) => ({ ip, count }));

      const topPaths = Object.entries(pathCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)
        .map(([path, count]) => ({ path, count }));

      const statusData = Object.entries(statusCounts)
        .map(([status, count]) => ({ status, count }));

      addLog('Running anomaly detection...', 'info');
      const { anomalies } = detectAnomalies(validLogs);
      addLog(`Detected ${anomalies.length} anomalous IPs`, anomalies.length > 0 ? 'warning' : 'success');

      addLog('Detecting attack patterns...', 'info');
      const attackPatterns = detectAttackPatterns(validLogs);
      addLog(`Found ${attackPatterns.bruteForce.length} brute-force attempts`, 
             attackPatterns.bruteForce.length > 0 ? 'warning' : 'success');

      addLog('Analyzing time series...', 'info');
      const { timeSeriesData, bursts } = analyzeTimeSeries(validLogs);
      addLog(`Detected ${bursts.length} traffic bursts`, bursts.length > 0 ? 'warning' : 'success');

      setResults({
        summary: {
          totalRequests: validLogs.length,
          uniqueIPs: Object.keys(ipCounts).length,
          timeRange: {
            start: validLogs[0]?.timestamp,
            end: validLogs[validLogs.length - 1]?.timestamp
          }
        },
        topIPs,
        topPaths,
        statusData,
        anomalies,
        attackPatterns,
        timeSeriesData,
        bursts
      });

      addLog('Analysis complete!', 'success');
    } catch (error) {
      addLog(`Error: ${error.message}`, 'error');
    } finally {
      setAnalyzing(false);
    }
  };

  const downloadReport = () => {
    if (!results) return;

    const report = `# SIEM Analysis Report
    
## Executive Summary
- Total Requests: ${results.summary.totalRequests}
- Unique Source IPs: ${results.summary.uniqueIPs}
- Analysis Period: ${results.summary.timeRange.start} to ${results.summary.timeRange.end}
- Anomalous IPs Detected: ${results.anomalies.length}
- Brute Force Attempts: ${results.attackPatterns.bruteForce.length}
- Traffic Bursts: ${results.bursts.length}

## Top 10 Source IPs
${results.topIPs.map((ip, i) => `${i + 1}. ${ip.ip} - ${ip.count} requests`).join('\n')}

## Anomalous IPs (Threat Score > 30)
${results.anomalies.map(a => 
  `- **${a.ip}** (Score: ${a.score}/100)
  - Requests: ${a.requests}
  - Distinct Paths: ${a.distinctPaths}
  - Fail Rate: ${a.failRate}%
  - Reasons: ${a.reasons}`
).join('\n')}

## Attack Patterns Detected

### Brute Force Attempts
${results.attackPatterns.bruteForce.map(bf => 
  `- ${bf.ip}: ${bf.attempts} failed authentication attempts`
).join('\n') || 'None detected'}

### Webshell Probes
${results.attackPatterns.webshell.slice(0, 10).map(w => 
  `- ${w.ip} attempted access to ${w.path}`
).join('\n') || 'None detected'}

### Suspicious User Agents
${[...new Set(results.attackPatterns.suspiciousUA.map(s => s.ip))].slice(0, 10).map(ip => 
  `- ${ip}`
).join('\n') || 'None detected'}

## Recommendations
1. **Immediate Actions:**
   - Block top ${Math.min(5, results.anomalies.length)} anomalous IPs
   - Implement rate limiting (500 req/10min threshold)
   - Review authentication logs for compromise

2. **Detection Rules to Deploy:**
   - Alert on >20 auth failures in 5 minutes
   - Alert on >50 distinct paths from single IP in 10 minutes
   - Block known scanner user agents

3. **Further Investigation:**
   - Correlate with firewall logs
   - Check for data exfiltration patterns
   - Review affected endpoints for vulnerabilities
`;

    const blob = new Blob([report], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `siem-report-${new Date().toISOString().slice(0, 10)}.md`;
    a.click();
  };

  const downloadCSV = (data, filename) => {
    const csv = [
      Object.keys(data[0]).join(','),
      ...data.map(row => Object.values(row).join(','))
    ].join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Shield className="w-10 h-10 text-blue-400" />
            <h1 className="text-4xl font-bold">SIEM Analysis Platform</h1>
          </div>
          <p className="text-blue-200">Real-time Security Information and Event Management</p>
        </div>

        <div className="bg-slate-800/50 backdrop-blur rounded-lg p-6 mb-6 border border-blue-500/20">
          <div className="flex items-center gap-4">
            <label className="flex-1 cursor-pointer">
              <div className="flex items-center gap-3 p-4 border-2 border-dashed border-blue-400 rounded-lg hover:bg-blue-500/10 transition">
                <Upload className="w-6 h-6 text-blue-400" />
                <div>
                  <p className="font-semibold">{file ? file.name : 'Upload Apache Access Log'}</p>
                  <p className="text-sm text-gray-400">Supports Apache Combined Log Format</p>
                </div>
              </div>
              <input
                type="file"
                accept=".log,.txt"
                onChange={handleFileUpload}
                className="hidden"
              />
            </label>
            
            <button
              onClick={analyzeData}
              disabled={!file || analyzing}
              className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded-lg font-semibold transition"
            >
              <Play className="w-5 h-5" />
              {analyzing ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
        </div>

        <div className="bg-black/40 backdrop-blur rounded-lg p-4 mb-6 border border-green-500/20 max-h-40 overflow-y-auto font-mono text-sm">
          {logs.map((log, i) => (
            <div key={i} className={`mb-1 ${
              log.type === 'error' ? 'text-red-400' :
              log.type === 'warning' ? 'text-yellow-400' :
              log.type === 'success' ? 'text-green-400' :
              'text-blue-300'
            }`}>
              [{log.timestamp.slice(11, 19)}] {log.message}
            </div>
          ))}
        </div>

        {results && (
          <>
            <div className="flex gap-2 mb-6 overflow-x-auto">
              {['overview', 'anomalies', 'attacks', 'timeline'].map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-6 py-2 rounded-lg font-semibold whitespace-nowrap transition ${
                    activeTab === tab
                      ? 'bg-blue-600'
                      : 'bg-slate-700 hover:bg-slate-600'
                  }`}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>

            {activeTab === 'overview' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg p-6">
                    <Activity className="w-8 h-8 mb-2" />
                    <h3 className="text-2xl font-bold">{results.summary.totalRequests.toLocaleString()}</h3>
                    <p className="text-blue-200">Total Requests</p>
                  </div>
                  <div className="bg-gradient-to-br from-purple-600 to-purple-800 rounded-lg p-6">
                    <TrendingUp className="w-8 h-8 mb-2" />
                    <h3 className="text-2xl font-bold">{results.summary.uniqueIPs}</h3>
                    <p className="text-purple-200">Unique IP Addresses</p>
                  </div>
                  <div className="bg-gradient-to-br from-red-600 to-red-800 rounded-lg p-6">
                    <AlertTriangle className="w-8 h-8 mb-2" />
                    <h3 className="text-2xl font-bold">{results.anomalies.length}</h3>
                    <p className="text-red-200">Anomalous IPs</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="bg-slate-800/50 backdrop-blur rounded-lg p-6 border border-blue-500/20">
                    <h3 className="text-xl font-bold mb-4">Request Volume Over Time</h3>
                    <ResponsiveContainer width="100%" height={250}>
                      <LineChart data={results.timeSeriesData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                        <XAxis dataKey="time" stroke="#94a3b8" />
                        <YAxis stroke="#94a3b8" />
                        <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #3b82f6' }} />
                        <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="bg-slate-800/50 backdrop-blur rounded-lg p-6 border border-blue-500/20">
                    <h3 className="text-xl font-bold mb-4">Status Code Distribution</h3>
                    <ResponsiveContainer width="100%" height={250}>
                      <PieChart>
                        <Pie
                          data={results.statusData}
                          dataKey="count"
                          nameKey="status"
                          cx="50%"
                          cy="50%"
                          outerRadius={80}
                          label
                        >
                          {results.statusData.map((entry, index) => (
                            <Cell key={index} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #3b82f6' }} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="bg-slate-800/50 backdrop-blur rounded-lg p-6 border border-blue-500/20">
                    <h3 className="text-xl font-bold mb-4">Top 10 Source IPs</h3>
                    <ResponsiveContainer width="100%" height={250}>
                      <BarChart data={results.topIPs}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                        <XAxis dataKey="ip" stroke="#94a3b8" angle={-45} textAnchor="end" height={80} />
                        <YAxis stroke="#94a3b8" />
                        <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #3b82f6' }} />
                        <Bar dataKey="count" fill="#8b5cf6" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="bg-slate-800/50 backdrop-blur rounded-lg p-6 border border-blue-500/20">
                    <h3 className="text-xl font-bold mb-4">Top 10 Requested Paths</h3>
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {results.topPaths.map((path, i) => (
                        <div key={i} className="flex justify-between items-center p-2 bg-slate-700/50 rounded">
                          <span className="text-sm truncate flex-1 font-mono">{path.path}</span>
                          <span className="text-blue-400 font-semibold ml-2">{path.count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <button
                  onClick={downloadReport}
                  className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition"
                >
                  <Download className="w-5 h-5" />
                  Download Full Report (Markdown)
                </button>
              </div>
            )}

            {activeTab === 'anomalies' && (
              <div className="space-y-6">
                <div className="flex justify-between items-center">
                  <h2 className="text-2xl font-bold">Detected Anomalies</h2>
                  <button
                    onClick={() => downloadCSV(results.anomalies, 'anomalies.csv')}
                    className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg"
                  >
                    <Download className="w-4 h-4" />
                    Export CSV
                  </button>
                </div>

                <div className="grid gap-4">
                  {results.anomalies.map((anomaly, i) => (
                    <div key={i} className="bg-slate-800/50 backdrop-blur rounded-lg p-6 border-l-4 border-red-500">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h3 className="text-xl font-bold font-mono">{anomaly.ip}</h3>
                          <p className="text-red-400">Threat Score: {anomaly.score}/100</p>
                        </div>
                        <div className={`px-3 py-1 rounded-full text-sm font-semibold ${
                          anomaly.score >= 70 ? 'bg-red-600' :
                          anomaly.score >= 50 ? 'bg-orange-600' :
                          'bg-yellow-600'
                        }`}>
                          {anomaly.score >= 70 ? 'CRITICAL' : anomaly.score >= 50 ? 'HIGH' : 'MEDIUM'}
                        </div>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <p className="text-gray-400">Requests</p>
                          <p className="font-semibold">{anomaly.requests}</p>
                        </div>
                        <div>
                          <p className="text-gray-400">Distinct Paths</p>
                          <p className="font-semibold">{anomaly.distinctPaths}</p>
                        </div>
                        <div>
                          <p className="text-gray-400">Fail Rate</p>
                          <p className="font-semibold">{anomaly.failRate}%</p>
                        </div>
                        <div className="md:col-span-1 col-span-2">
                          <p className="text-gray-400">Detection Reasons</p>
                          <p className="font-semibold text-yellow-400">{anomaly.reasons}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'attacks' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold">Attack Pattern Analysis</h2>

                <div className="bg-slate-800/50 backdrop-blur rounded-lg p-6 border border-red-500/20">
                  <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <AlertTriangle className="w-6 h-6 text-red-400" />
                    Brute Force Attempts ({results.attackPatterns.bruteForce.length})
                  </h3>
                  {results.attackPatterns.bruteForce.length > 0 ? (
                    <div className="space-y-2">
                      {results.attackPatterns.bruteForce.slice(0, 10).map((bf, i) => (
                        <div key={i} className="flex justify-between items-center p-3 bg-red-900/20 rounded">
                          <span className="font-mono">{bf.ip}</span>
                          <span className="text-red-400 font-semibold">{bf.attempts} failed attempts</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-400">No brute force attempts detected</p>
                  )}
                </div>

                <div className="bg-slate-800/50 backdrop-blur rounded-lg p-6 border border-orange-500/20">
                  <h3 className="text-xl font-bold mb-4">Webshell/Admin Probes ({results.attackPatterns.webshell.length})</h3>
                  {results.attackPatterns.webshell.length > 0 ? (
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {results.attackPatterns.webshell.slice(0, 20).map((probe, i) => (
                        <div key={i} className="p-3 bg-orange-900/20 rounded">
                          <div className="flex justify-between">
                            <span className="font-mono text-sm">{probe.ip}</span>
                            <span className="text-xs text-gray-400">{probe.timestamp}</span>
                          </div>
                          <p className="text-orange-400 text-sm mt-1">{probe.path}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-400">No webshell probes detected</p>
                  )}
                </div>

                <div className="bg-slate-800/50 backdrop-blur rounded-lg p-6 border border-yellow-500/20">
                  <h3 className="text-xl font-bold mb-4">Suspicious User Agents ({results.attackPatterns.suspiciousUA.length})</h3>
                  {results.attackPatterns.suspiciousUA.length > 0 ? (
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {results.attackPatterns.suspiciousUA.slice(0, 15).map((ua, i) => (
                        <div key={i} className="p-3 bg-yellow-900/20 rounded">
                          <div className="flex justify-between">
                            <span className="font-mono text-sm">{ua.ip}</span>
                            <span className="text-xs text-gray-400">{ua.path}</span>
                          </div>
                          <p className="text-yellow-400 text-xs mt-1 truncate">{ua.ua}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-400">No suspicious user agents detected</p>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'timeline' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold">Traffic Bursts Timeline</h2>
                
                {results.bursts.length > 0 ? (
                  <div className="space-y-4">
                    {results.bursts.map((burst, i) => (
                      <div key={i} className="bg-slate-800/50 backdrop-blur rounded-lg p-6 border-l-4 border-orange-500">
                        <div className="flex justify-between items-center">
                          <div>
                            <h3 className="text-xl font-bold">Burst #{i + 1}</h3>
                            <p className="text-gray-400">Time: {burst.time}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-3xl font-bold text-orange-400">{burst.count}</p>
                            <p className="text-sm text-gray-400">requests/minute</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="bg-slate-800/50 backdrop-blur rounded-lg p-6 border border-green-500/20">
                    <p className="text-gray-400">No significant traffic bursts detected</p>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default SIEMAnalyzer;