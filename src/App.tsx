/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect, useRef } from 'react';
import { 
  Folder, 
  FolderOpen, 
  File, 
  ChevronRight, 
  ChevronDown, 
  Terminal, 
  Play, 
  Search, 
  Database, 
  ShieldCheck, 
  Cpu, 
  CheckCircle2, 
  ExternalLink, 
  Copy, 
  Github, 
  GitBranch, 
  Sparkles, 
  Lock, 
  CreditCard,
  Check,
  RefreshCw,
  HelpCircle,
  AlertCircle
} from 'lucide-react';
import { REPO_FILES, REPO_TREE, MOCK_RAG_DATABASE, FolderNode, RepoFile } from './data';
import { motion, AnimatePresence } from 'motion/react';

// Simple custom syntax highlighting using regex replacement
function highlightCode(code: string, language: string) {
  if (language === 'json') {
    return code
      .replace(/(".*?"\s*:)/g, '<span class="text-emerald-400 font-semibold">$1</span>')
      .replace(/(:\s*".*?")/g, ':<span class="text-amber-300">$1</span>')
      .replace(/(:\s*[0-9.]+)/g, ':<span class="text-sky-400">$1</span>');
  }
  if (language === 'python') {
    return code
      .replace(/\b(def|class|import|from|as|return|async|await|pass|yield|for|in|if|else|try|except|with|None|True|False)\b/g, '<span class="text-sky-400 font-medium">$1</span>')
      .replace(/(\".*?\")/g, '<span class="text-amber-200">$1</span>')
      .replace(/(\#.*?)$/gm, '<span class="text-slate-500 italic">$1</span>')
      .replace(/(@\w+)/g, '<span class="text-violet-400">$1</span>');
  }
  if (language === 'markdown') {
    return code
      .replace(/^(#+ .*)$/gm, '<span class="text-emerald-400 font-bold">$1</span>')
      .replace(/(\*\*.*?\*\*)/g, '<span class="text-sky-300 font-semibold">$1</span>')
      .replace(/(\`.*?\`)/g, '<span class="text-slate-300 font-mono bg-slate-800/60 px-1 rounded">$1</span>');
  }
  return code;
}

export default function App() {
  const [activeTab, setActiveTab] = useState<'explorer' | 'simulator' | 'rag' | 'docs'>('explorer');
  const [selectedFile, setSelectedFile] = useState<RepoFile | null>(REPO_FILES['README.md']);
  const [expandedFolders, setExpandedFolders] = useState<Record<string, boolean>>({
    'hospitality-reservation-payment-agent': true,
    'app': true,
    'app/api': true,
    'graph': true,
    'crew': true,
    'agent_mcp': true,
    'agent_mcp/tools': false,
    'rag': false,
    'models': false,
    'mock_data': false,
    'knowledge_base': false,
    'docs': true,
  });
  const [copiedPath, setCopiedPath] = useState<string | null>(null);

  // Simulation states
  const [simState, setSimState] = useState<'idle' | 'running' | 'pending_payment' | 'processing_payment' | 'paid' | 'confirmed'>('idle');
  const [simLogs, setSimLogs] = useState<{ step: string; status: 'completed' | 'pending' | 'success'; message: string; timestamp: string }[]>([]);
  const [simProgress, setSimProgress] = useState(0);
  const [idempotencyKey, setIdempotencyKey] = useState('idem_sandbox_88cf9b61a320');
  const [stripeForm, setStripeForm] = useState({
    cardNumber: '4242 •••• •••• 4242',
    expiry: '12 / 29',
    cvc: '123',
    cardholder: 'AQUILINO FRANCISCO'
  });

  // RAG query states
  const [ragQuery, setRagQuery] = useState('');
  const [ragResults, setRagResults] = useState<any[]>([]);
  const [isSearchingRag, setIsSearchingRag] = useState(false);

  // Terminal actions
  const [terminalLogs, setTerminalLogs] = useState<string[]>([
    'Initializing local environment checks...',
    'Python 3.11.8 detected.',
    'Docker container engines verified [v24.0.7]',
    'Git configuration initialized for aquilinoFrancisco',
    'Ready. Explore Phase 1 directories below.'
  ]);

  // Copy code utility
  const handleCopyCode = (text: string, path: string) => {
    navigator.clipboard.writeText(text);
    setCopiedPath(path);
    setTimeout(() => setCopiedPath(null), 2000);
  };

  // Toggle folders
  const toggleFolder = (folderPath: string) => {
    setExpandedFolders(prev => ({ ...prev, [folderPath]: !prev[folderPath] }));
  };

  // Run stream simulator
  const runReservationSimulation = async () => {
    setSimState('running');
    setSimProgress(10);
    setSimLogs([]);
    
    const stepsData = [
      { step: 'validate_request', title: 'State Validation', msg: 'LangGraph node validating email syntax & date constraints' },
      { step: 'check_availability', title: 'Schedule Check', msg: 'MCP tool checking rooms.json & calendars' },
      { step: 'calculate_price', title: 'Pricing Matrix', msg: 'MCP tool checking rate rules: $250.00 x 2 nights = $500.00' },
      { step: 'reservation_agent', title: 'CrewAI: ReservationAgent', msg: 'Reservations manager generating draft records' },
      { step: 'payment_agent', title: 'CrewAI: PaymentAgent', msg: 'Compliance officer invoking MCP create_payment_link' },
    ];

    for (let i = 0; i < stepsData.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 1200));
      const logTime = new Date().toLocaleTimeString();
      setSimLogs(prev => [
        ...prev, 
        { 
          step: stepsData[i].step, 
          status: 'completed', 
          message: stepsData[i].msg, 
          timestamp: logTime 
        }
      ]);
      setSimProgress((i + 1) * 18);
    }

    await new Promise(resolve => setTimeout(resolve, 1000));
    setSimState('pending_payment');
    setSimProgress(90);
    setSimLogs(prev => [
      ...prev,
      {
        step: 'pending_payment',
        status: 'pending',
        message: 'Awaiting webhook transaction authorization link in Stripe Sandbox...',
        timestamp: new Date().toLocaleTimeString()
      }
    ]);
  };

  // Execute mock Stripe Sandbox Payment
  const submitStripePayment = async () => {
    setSimState('processing_payment');
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    setSimState('paid');
    setSimLogs(prev => [
      ...prev,
      {
        step: 'webhooks',
        status: 'completed',
        message: 'POST /webhooks/stripe: checkout.session.completed received & signature verified.',
        timestamp: new Date().toLocaleTimeString()
      }
    ]);

    await new Promise(resolve => setTimeout(resolve, 1200));
    setSimState('confirmed');
    setSimProgress(100);
    setSimLogs(prev => [
      ...prev,
      {
        step: 'confirmed',
        status: 'success',
        message: 'Reservation state set to CONFIRMED. Audit JSON report saved to /reports/report_res_001.json!',
        timestamp: new Date().toLocaleTimeString()
      }
    ]);
  };

  // Reset simulation
  const resetSimulation = () => {
    setSimState('idle');
    setSimLogs([]);
    setSimProgress(0);
    // Generate new idempotency key on restart
    setIdempotencyKey('idem_sandbox_' + Math.random().toString(36).substring(2, 14));
  };

  // Run semantic RAG Search
  const executeRagSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!ragQuery.trim()) return;

    setIsSearchingRag(true);
    setTimeout(() => {
      const normalizedQuery = ragQuery.toLowerCase();
      const hits = MOCK_RAG_DATABASE.filter(doc => {
        return doc.title.toLowerCase().includes(normalizedQuery) ||
               doc.content.toLowerCase().includes(normalizedQuery) ||
               doc.tags.some(tag => tag.includes(normalizedQuery));
      });
      setRagResults(hits);
      setIsSearchingRag(false);
    }, 800);
  };

  // File explorer tree component
  const renderTree = (nodes: FolderNode[]) => {
    return (
      <div className="pl-3 border-l border-slate-800 select-none">
        {nodes.map(node => {
          const isFolder = node.type === 'folder';
          const isExpanded = expandedFolders[node.path] || false;
          const isFileSelected = selectedFile?.path === node.path;

          return (
            <div key={node.path} className="my-1">
              <div 
                onClick={() => {
                  if (isFolder) {
                    toggleFolder(node.path);
                  } else {
                    const foundFile = REPO_FILES[node.path];
                    if (foundFile) setSelectedFile(foundFile);
                  }
                }}
                className={`flex items-center gap-2 py-1 px-2 rounded-md cursor-pointer transition-colors ${
                  isFileSelected 
                    ? 'bg-emerald-950/40 text-emerald-300 border border-emerald-900/40' 
                    : 'text-slate-300 hover:bg-slate-800/40'
                }`}
              >
                {isFolder ? (
                  <>
                    {isExpanded ? <ChevronDown size={14} className="text-slate-400" /> : <ChevronRight size={14} className="text-slate-400" />}
                    {isExpanded ? <FolderOpen size={16} className="text-emerald-400" /> : <Folder size={16} className="text-emerald-500" />}
                    <span className="font-sans font-medium text-xs text-slate-200">{node.name}</span>
                  </>
                ) : (
                  <>
                    <span className="w-3.5 h-3.5 flex items-center justify-center">
                      <File size={14} className={isFileSelected ? 'text-emerald-400' : 'text-slate-400'} />
                    </span>
                    <span className={`font-mono text-xs ${isFileSelected ? 'text-emerald-300 font-semibold' : 'text-slate-300'}`}>
                      {node.name}
                    </span>
                    {node.name.endsWith('.md') && (
                      <span className="text-[9px] px-1 py-0.5 rounded bg-slate-800 text-slate-400 font-sans">Doc</span>
                    )}
                    {node.name.endsWith('.json') && (
                      <span className="text-[9px] px-1 py-0.5 rounded bg-amber-950/40 text-amber-300 font-sans">JSON</span>
                    )}
                  </>
                )}
              </div>
              
              {isFolder && isExpanded && node.children && (
                <div className="mt-0.5">
                  {renderTree(node.children)}
                </div>
              )}
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-[#070b12] text-slate-200 font-sans selection:bg-emerald-800/40 flex flex-col">
      
      {/* HEADER BAR */}
      <header className="border-b border-slate-800/80 bg-[#090e18] px-6 py-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1 rounded bg-emerald-500/10 border border-emerald-500/20">
              <Sparkles className="text-emerald-400" size={18} />
            </span>
            <h1 className="text-lg font-bold text-slate-100 tracking-tight">
              Hospitality Reservation Payment Agent
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Agentic booking and safe Stripe Sandbox workflows with LangGraph, CrewAI, and Model Context Protocol.
          </p>
        </div>

        {/* Action badges and project links */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs bg-emerald-950/60 border border-emerald-900/50 text-emerald-400 px-2.5 py-1 rounded-full font-medium flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            Phase 1: Structure Ready
          </span>
          <span className="text-xs bg-slate-800/60 border border-slate-700/50 text-slate-300 px-2.5 py-1 rounded-full font-medium flex items-center gap-1">
            Stripe Sandbox
          </span>
          <span className="text-xs bg-slate-800/60 border border-slate-700/50 text-slate-300 px-2.5 py-1 rounded-full font-medium flex items-center gap-1">
            Local RAG
          </span>
          <a 
            href="https://github.com/aquilinoFrancisco/hospitality-reservation-payment-agent" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-xs bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-emerald-400 px-3 py-1 rounded-lg font-medium transition-all flex items-center gap-1.5"
          >
            <Github size={14} />
            GitHub Repo
            <ExternalLink size={10} />
          </a>
        </div>
      </header>

      {/* CORE NAVIGATION TABS */}
      <nav className="flex border-b border-slate-800/60 bg-[#080c14] px-6">
        <button 
          onClick={() => setActiveTab('explorer')}
          className={`py-3 px-4 text-xs font-semibold border-b-2 flex items-center gap-2 transition-all cursor-pointer ${
            activeTab === 'explorer' 
              ? 'border-emerald-500 text-emerald-400 bg-emerald-950/10' 
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <FolderOpen size={14} />
          Repository Explorer
        </button>
        <button 
          onClick={() => setActiveTab('simulator')}
          className={`py-3 px-4 text-xs font-semibold border-b-2 flex items-center gap-2 transition-all cursor-pointer ${
            activeTab === 'simulator' 
              ? 'border-emerald-500 text-emerald-400 bg-emerald-950/10' 
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Cpu size={14} />
          Agent Payment Simulator
          <span className="text-[9px] px-1 py-0.2 bg-emerald-500/10 border border-emerald-500/20 rounded text-emerald-400">Live</span>
        </button>
        <button 
          onClick={() => setActiveTab('rag')}
          className={`py-3 px-4 text-xs font-semibold border-b-2 flex items-center gap-2 transition-all cursor-pointer ${
            activeTab === 'rag' 
              ? 'border-emerald-500 text-emerald-400 bg-emerald-950/10' 
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Database size={14} />
          Local RAG Search
        </button>
        <button 
          onClick={() => setActiveTab('docs')}
          className={`py-3 px-4 text-xs font-semibold border-b-2 flex items-center gap-2 transition-all cursor-pointer ${
            activeTab === 'docs' 
              ? 'border-emerald-500 text-emerald-400 bg-emerald-950/10' 
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <ShieldCheck size={14} />
          Security & Architecture
        </button>
      </nav>

      {/* WORKSPACE AREA */}
      <main className="flex-1 flex flex-col lg:flex-row overflow-hidden bg-[#05080e]">
        
        {/* VIEW 1: REPOSITORY EXPLORER */}
        {activeTab === 'explorer' && (
          <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
            
            {/* FILE EXPLORER SIDEBAR */}
            <section className="w-full lg:w-80 border-r border-slate-900/60 bg-[#080d16] p-4 flex flex-col overflow-y-auto">
              <div className="flex items-center justify-between text-xs text-slate-400 font-semibold uppercase tracking-wider mb-3 px-1">
                <span>Repository Files</span>
                <span className="text-[10px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded font-mono">
                  Phase 1
                </span>
              </div>
              
              <div className="flex-1 overflow-y-auto pr-1">
                {renderTree(REPO_TREE)}
              </div>

              {/* GIT STATUS PANEL SUMMARY */}
              <div className="mt-4 pt-4 border-t border-slate-800/80">
                <div className="flex items-center gap-1.5 text-xs text-slate-300 font-semibold mb-2">
                  <GitBranch size={13} className="text-sky-400" />
                  <span>git status</span>
                </div>
                <div className="font-mono text-[10px] text-slate-400 leading-relaxed bg-[#060a10] p-2.5 rounded-lg border border-slate-900">
                  <div>On branch <span className="text-emerald-400">main</span></div>
                  <div>nothing to commit, working tree clean</div>
                  <div className="text-slate-500 text-[9px] mt-1.5">
                    Prepared for upload:
                    <div className="text-sky-400 mt-0.5 truncate">https://github.com/aquilinoFrancisco/...</div>
                  </div>
                </div>
              </div>
            </section>

            {/* CODE WORKSPACE EDITOR */}
            <section className="flex-1 flex flex-col bg-[#05080e] overflow-hidden min-h-[400px]">
              {selectedFile ? (
                <div className="flex-1 flex flex-col overflow-hidden">
                  
                  {/* EDITOR CONTROLS */}
                  <div className="bg-[#080d16] border-b border-slate-900/80 px-4 py-3 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="p-1 rounded bg-slate-800/50">
                        <File size={13} className="text-emerald-400" />
                      </span>
                      <span className="font-mono text-xs text-slate-300 font-semibold truncate">
                        hospitality-reservation-payment-agent/{selectedFile.path}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleCopyCode(selectedFile.content, selectedFile.path)}
                        className="text-slate-400 hover:text-emerald-400 p-1.5 hover:bg-slate-800/50 rounded-lg transition-all cursor-pointer"
                        title="Copy code to clipboard"
                      >
                        {copiedPath === selectedFile.path ? (
                          <span className="text-xs text-emerald-400 font-sans flex items-center gap-1">
                            <Check size={12} /> Copied!
                          </span>
                        ) : (
                          <Copy size={14} />
                        )}
                      </button>
                    </div>
                  </div>

                  {/* FILE INFO BOX */}
                  <div className="bg-slate-950/40 px-5 py-3 border-b border-slate-900/30 flex items-start gap-2.5">
                    <AlertCircle size={14} className="text-emerald-500 mt-0.5 flex-shrink-0" />
                    <p className="text-xs text-slate-400 leading-normal">
                      <strong className="text-slate-200">Module Blueprint:</strong> {selectedFile.description}
                    </p>
                  </div>

                  {/* CODE PANEL */}
                  <div className="flex-1 overflow-auto bg-[#05080e] p-6 font-mono text-xs leading-relaxed text-slate-300">
                    <pre className="relative select-text">
                      <code 
                        dangerouslySetInnerHTML={{ 
                          __html: highlightCode(selectedFile.content, selectedFile.language) 
                        }} 
                      />
                    </pre>
                  </div>
                </div>
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-slate-500 p-6 bg-[#05080e]">
                  <File size={40} className="text-slate-700 mb-2" />
                  <p className="text-sm font-sans">Select a file from the repository tree to inspect its placeholder code.</p>
                </div>
              )}
            </section>
          </div>
        )}

        {/* VIEW 2: STREAM AGENT SIMULATOR */}
        {activeTab === 'simulator' && (
          <div className="flex-1 flex flex-col xl:flex-row overflow-y-auto p-6 gap-6">
            
            {/* WORKFLOW CONTROLLERS */}
            <div className="flex-1 flex flex-col gap-6">
              
              {/* CONFIG & INITIATE BLOCK */}
              <div className="bg-[#080d16] border border-slate-800/80 rounded-xl p-5">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Terminal size={16} className="text-emerald-400" />
                    <h2 className="text-sm font-bold text-slate-200">Simulation Config</h2>
                  </div>
                  <span className="text-[10px] font-mono bg-emerald-950/40 text-emerald-400 border border-emerald-900/50 px-2 py-0.5 rounded">
                    Stripe Sandbox Ready
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-[10px] text-slate-400 uppercase tracking-wider font-semibold mb-1">
                      Customer Email
                    </label>
                    <input 
                      type="text" 
                      disabled
                      value="aquilino.francisco@gmail.com" 
                      className="w-full bg-[#05080e] border border-slate-800 rounded-lg p-2 text-xs font-mono text-slate-300 cursor-not-allowed"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] text-slate-400 uppercase tracking-wider font-semibold mb-1">
                      Idempotency Key (Safe Operations)
                    </label>
                    <input 
                      type="text" 
                      disabled
                      value={idempotencyKey} 
                      className="w-full bg-[#05080e] border border-slate-800 rounded-lg p-2 text-xs font-mono text-emerald-400 cursor-not-allowed"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] text-slate-400 uppercase tracking-wider font-semibold mb-1">
                      Room Type
                    </label>
                    <select disabled className="w-full bg-[#05080e] border border-slate-800 rounded-lg p-2 text-xs font-sans text-slate-300 cursor-not-allowed">
                      <option>Deluxe Suite ($250.00 / night)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-[10px] text-slate-400 uppercase tracking-wider font-semibold mb-1">
                      Stay Period
                    </label>
                    <input 
                      type="text" 
                      disabled
                      value="2026-07-10 to 2026-07-12 (2 Nights)" 
                      className="w-full bg-[#05080e] border border-slate-800 rounded-lg p-2 text-xs font-sans text-slate-300 cursor-not-allowed"
                    />
                  </div>
                </div>

                <div className="flex gap-2">
                  {simState === 'idle' && (
                    <button
                      onClick={runReservationSimulation}
                      className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs py-2.5 px-4 rounded-lg cursor-pointer transition-all flex items-center justify-center gap-1.5 shadow-lg shadow-emerald-950/20"
                    >
                      <Play size={14} />
                      Start Agentic Booking Stream
                    </button>
                  )}
                  {simState !== 'idle' && (
                    <button
                      onClick={resetSimulation}
                      className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs py-2.5 px-4 rounded-lg cursor-pointer transition-all flex items-center justify-center gap-1.5"
                    >
                      <RefreshCw size={14} className={simState === 'running' ? 'animate-spin' : ''} />
                      Reset Simulator State
                    </button>
                  )}
                </div>
              </div>

              {/* SIMULATION STEPPER METRICS */}
              <div className="bg-[#080d16] border border-slate-800/80 rounded-xl p-5">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                    Agent Stream Event Log
                  </h3>
                  {simProgress > 0 && (
                    <span className="text-xs font-mono text-slate-400">{simProgress}% Complete</span>
                  )}
                </div>

                {/* Simulated Progress bar */}
                <div className="w-full bg-slate-900 rounded-full h-1.5 mb-5 overflow-hidden">
                  <motion.div 
                    className="bg-emerald-500 h-1.5 rounded-full" 
                    initial={{ width: 0 }}
                    animate={{ width: `${simProgress}%` }}
                    transition={{ duration: 0.4 }}
                  />
                </div>

                {/* Log messages */}
                <div className="space-y-3 font-mono text-xs max-h-[250px] overflow-y-auto pr-1">
                  {simLogs.length === 0 ? (
                    <div className="text-slate-500 text-center py-6 text-xs">
                      No stream active. Click the button above to simulate the LangGraph node executions.
                    </div>
                  ) : (
                    simLogs.map((log, index) => (
                      <div key={index} className="border-l-2 border-emerald-500/40 pl-3 py-1">
                        <div className="flex items-center justify-between text-[10px] text-slate-500 mb-0.5">
                          <span className="font-semibold uppercase text-sky-400">Step: {log.step}</span>
                          <span>{log.timestamp}</span>
                        </div>
                        <p className="text-slate-300 leading-normal">{log.message}</p>
                      </div>
                    ))
                  )}

                  {simState === 'running' && (
                    <div className="flex items-center gap-2 text-xs text-slate-400 italic py-2 pl-3 animate-pulse">
                      <RefreshCw size={12} className="animate-spin text-emerald-500" />
                      LangGraph node processing...
                    </div>
                  )}
                </div>
              </div>

            </div>

            {/* STRIPE SANDBOX INTERACTIVE BLOCK */}
            <div className="w-full xl:w-96 flex flex-col gap-6">
              
              {/* STATUS INDICATOR CARD */}
              <div className="bg-[#080d16] border border-slate-800/80 rounded-xl p-5 text-center flex flex-col items-center justify-center">
                <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider mb-2">
                  Workflow Reservation State
                </span>
                
                <AnimatePresence mode="wait">
                  {simState === 'idle' && (
                    <motion.div 
                      key="state-idle"
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      className="text-slate-500 font-bold font-mono text-lg py-2"
                    >
                      IDLE
                    </motion.div>
                  )}
                  {simState === 'running' && (
                    <motion.div 
                      key="state-running"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="text-sky-400 font-bold font-mono text-lg py-2 flex items-center gap-2"
                    >
                      <RefreshCw size={18} className="animate-spin" />
                      PROCESSING
                    </motion.div>
                  )}
                  {simState === 'pending_payment' && (
                    <motion.div 
                      key="state-pending"
                      initial={{ opacity: 0, y: 5 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="text-amber-400 font-bold font-mono text-base py-2 flex flex-col items-center gap-1.5"
                    >
                      <span className="px-2.5 py-0.5 rounded bg-amber-500/10 border border-amber-500/20 text-xs animate-pulse">
                        PENDING_PAYMENT
                      </span>
                      <span className="text-[10px] text-slate-400 font-sans font-normal mt-1">
                        Awaiting Stripe Payment Link Authorization
                      </span>
                    </motion.div>
                  )}
                  {simState === 'processing_payment' && (
                    <motion.div 
                      key="state-processing"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="text-amber-500 font-bold font-mono text-sm py-2 flex items-center gap-2"
                    >
                      <RefreshCw size={14} className="animate-spin" />
                      SUBMITTING CHECKOUT...
                    </motion.div>
                  )}
                  {(simState === 'paid' || simState === 'confirmed') && (
                    <motion.div 
                      key="state-confirmed"
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="text-emerald-400 font-bold font-mono text-base py-1 flex flex-col items-center gap-1.5"
                    >
                      <span className="px-2.5 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-xs flex items-center gap-1">
                        <CheckCircle2 size={12} /> CONFIRMED & PAID
                      </span>
                      <span className="text-[10px] text-slate-400 font-sans font-normal">
                        Webhook response received. Reservation completed.
                      </span>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* STRIPE SANDBOX SIMULATOR */}
              <div className="bg-[#080d16] border border-slate-800/80 rounded-xl overflow-hidden shadow-2xl shadow-black/40">
                <div className="bg-[#635bff] px-5 py-4 flex items-center justify-between">
                  <div className="flex items-center gap-2 text-white">
                    <CreditCard size={16} />
                    <span className="font-sans font-bold text-xs uppercase tracking-wider">Stripe Sandbox Checkout</span>
                  </div>
                  <span className="text-[9px] bg-white/20 text-white font-mono px-2 py-0.5 rounded">
                    Test Mode
                  </span>
                </div>

                <div className="p-5">
                  <div className="mb-4 border-b border-slate-800/60 pb-4">
                    <div className="flex justify-between items-center text-xs mb-1.5">
                      <span className="text-slate-400">Reservation Reference</span>
                      <span className="font-mono text-slate-200 font-semibold">res_99f2b8a0</span>
                    </div>
                    <div className="flex justify-between items-center text-xs mb-1.5">
                      <span className="text-slate-400">Item</span>
                      <span className="text-slate-200">Deluxe Suite • 2 Nights</span>
                    </div>
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-slate-400 font-medium">Total Amount Due</span>
                      <span className="text-emerald-400 font-bold">$500.00 USD</span>
                    </div>
                  </div>

                  {simState === 'pending_payment' ? (
                    <div className="space-y-4">
                      <p className="text-[11px] text-slate-400 leading-normal">
                        The PaymentAgent created an active secure Checkout Session checkout url with Stripe Sandbox. Click below to authorize transaction.
                      </p>

                      <div className="space-y-2">
                        <div className="bg-slate-950 p-2.5 rounded border border-slate-800 font-mono text-[10px] text-slate-400 leading-normal">
                          <div className="text-[9px] uppercase font-bold text-slate-500 mb-1">Idempotency-Key Header:</div>
                          <span className="text-emerald-400 break-all">{idempotencyKey}</span>
                        </div>

                        <button
                          onClick={submitStripePayment}
                          className="w-full bg-[#635bff] hover:bg-[#7a73ff] text-white font-bold text-xs py-2.5 px-4 rounded-lg cursor-pointer transition-all flex items-center justify-center gap-2 shadow-lg shadow-[#635bff]/20"
                        >
                          <Lock size={12} />
                          Simulate Stripe Payment ($500)
                        </button>
                      </div>
                    </div>
                  ) : simState === 'processing_payment' ? (
                    <div className="py-8 text-center flex flex-col items-center justify-center">
                      <RefreshCw className="animate-spin text-[#635bff] mb-3" size={24} />
                      <p className="text-xs text-slate-400">Submitting authorized charge to Stripe API sandbox...</p>
                    </div>
                  ) : simState === 'confirmed' || simState === 'paid' ? (
                    <div className="py-6 text-center flex flex-col items-center justify-center">
                      <div className="w-10 h-10 rounded-full bg-emerald-950/40 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mb-3">
                        <CheckCircle2 size={20} />
                      </div>
                      <h4 className="text-xs font-bold text-slate-200 mb-1">Sandbox Payment Complete!</h4>
                      <p className="text-[10px] text-slate-400 leading-relaxed max-w-[200px] mx-auto">
                        Webhook callback confirmed. The room has been securely reserved. Check reports/ folder!
                      </p>
                    </div>
                  ) : (
                    <div className="py-8 text-center text-xs text-slate-500 leading-normal">
                      <HelpCircle size={20} className="mx-auto mb-2 text-slate-700" />
                      Stripe checkout session will display here once you run the Agent booking stream.
                    </div>
                  )}
                </div>
              </div>

            </div>

          </div>
        )}

        {/* VIEW 3: LOCAL RAG EXPLORER */}
        {activeTab === 'rag' && (
          <div className="flex-1 flex flex-col p-6 overflow-y-auto">
            
            {/* RAG HEADER */}
            <div className="mb-6">
              <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                <Database size={16} className="text-emerald-400" />
                Local RAG Knowledge base Explorer
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Query local policy files in the `knowledge_base/` folder. The RAG retriever finds semantic contexts to ground prompt validations.
              </p>
            </div>

            {/* SEARCH BOX */}
            <form onSubmit={executeRagSearch} className="mb-6 flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3.5 top-3 text-slate-500" size={14} />
                <input 
                  type="text"
                  placeholder="Ask policies database (e.g. 'cancellation policy', 'how are refunds issued?', 'check-in time')"
                  value={ragQuery}
                  onChange={(e) => setRagQuery(e.target.value)}
                  className="w-full bg-[#080d16] border border-slate-800 focus:border-emerald-500 rounded-lg py-2.5 pl-10 pr-4 text-xs text-slate-200 outline-none transition-colors font-sans"
                />
              </div>
              <button
                type="submit"
                className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold py-2.5 px-5 rounded-lg cursor-pointer transition-all flex items-center gap-1.5"
              >
                Query RAG
              </button>
            </form>

            {/* RESULTS CONTAINER */}
            <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4">
              
              {/* RETRIEVED BLOCKS */}
              <div className="border border-slate-800 bg-[#080d16] rounded-xl p-5 flex flex-col min-h-[300px]">
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">
                  Retrieved Contexts ({ragResults.length} hits)
                </h3>

                {isSearchingRag ? (
                  <div className="flex-1 flex flex-col items-center justify-center text-slate-400 text-xs italic">
                    <RefreshCw className="animate-spin text-emerald-500 mb-2" size={18} />
                    Calculating sentence-transformers embeddings...
                  </div>
                ) : ragResults.length === 0 ? (
                  <div className="flex-1 flex flex-col items-center justify-center text-slate-500 text-xs py-8 text-center max-w-sm mx-auto">
                    <HelpCircle size={24} className="mb-1 text-slate-700" />
                    Enter a query such as <strong className="text-slate-300">"cancellation"</strong>, <strong className="text-slate-300">"refund"</strong>, or <strong className="text-slate-300">"incidentals"</strong> to simulate semantic passage indexing.
                  </div>
                ) : (
                  <div className="space-y-4 overflow-y-auto pr-1">
                    {ragResults.map((hit, index) => (
                      <div key={index} className="bg-[#05080e] p-3.5 rounded-lg border border-slate-800">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-[10px] font-mono text-emerald-400 font-semibold bg-emerald-950/40 px-2 py-0.5 rounded">
                            {hit.doc}
                          </span>
                          <span className="text-[10px] text-slate-500 font-mono">Similarity: {(0.88 + (0.1 - index * 0.04)).toFixed(3)}</span>
                        </div>
                        <h4 className="text-xs font-bold text-slate-200 mb-1.5">{hit.title}</h4>
                        <p className="text-xs text-slate-400 leading-relaxed font-sans">{hit.content}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* KNOWLEDGE MAP SUMMARY */}
              <div className="border border-slate-800 bg-[#080d16] rounded-xl p-5 flex flex-col">
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">
                  Indexed Knowledge Documents
                </h3>
                
                <div className="space-y-3 flex-1 overflow-y-auto pr-1">
                  <div className="p-3 bg-slate-900/40 rounded-lg border border-slate-800/60">
                    <h4 className="text-xs font-semibold text-slate-300 flex items-center justify-between">
                      <span>cancellation_policy.md</span>
                      <span className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 font-mono">Active</span>
                    </h4>
                    <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                      Determines booking late cancellations, standard 48 hours bounds, and penalty rate evaluations.
                    </p>
                  </div>

                  <div className="p-3 bg-slate-900/40 rounded-lg border border-slate-800/60">
                    <h4 className="text-xs font-semibold text-slate-300 flex items-center justify-between">
                      <span>refund_policy.md</span>
                      <span className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 font-mono">Active</span>
                    </h4>
                    <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                      Defines Stripe Sandbox refund authorizations, required tracking variables, and validation schemas.
                    </p>
                  </div>

                  <div className="p-3 bg-slate-900/40 rounded-lg border border-slate-800/60">
                    <h4 className="text-xs font-semibold text-slate-300 flex items-center justify-between">
                      <span>payment_policy.md</span>
                      <span className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 font-mono">Active</span>
                    </h4>
                    <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                      Strict guidelines mandating the LLM/Agent to redirect checkouts securely through unique checkout links.
                    </p>
                  </div>

                  <div className="p-3 bg-slate-900/40 rounded-lg border border-slate-800/60">
                    <h4 className="text-xs font-semibold text-slate-300 flex items-center justify-between">
                      <span>hotel_terms.md</span>
                      <span className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 font-mono">Active</span>
                    </h4>
                    <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                      Check-in requirements, incidental deposits, and general property usage limits.
                    </p>
                  </div>
                </div>
              </div>

            </div>

          </div>
        )}

        {/* VIEW 4: SECURITY & DESIGN */}
        {activeTab === 'docs' && (
          <div className="flex-1 flex flex-col p-6 overflow-y-auto gap-6">
            
            {/* PRINCIPLES */}
            <div className="bg-[#080d16] border border-slate-800/80 rounded-xl p-5">
              <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2 mb-4">
                <ShieldCheck size={16} className="text-emerald-400" />
                Stripe Sandbox Payment Security Architecture
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-slate-900/40 border border-slate-800/60 rounded-lg">
                  <div className="w-8 h-8 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mb-2.5 font-bold font-mono text-xs">
                    01
                  </div>
                  <h3 className="text-xs font-bold text-slate-200 mb-1">Indirect Checkout</h3>
                  <p className="text-[11px] text-slate-400 leading-relaxed">
                    AI agents are strictly forbidden from collecting, storing, or directly prompting credit card numbers. Checkout sessions are generated out-of-band via secure links.
                  </p>
                </div>

                <div className="p-4 bg-slate-900/40 border border-slate-800/60 rounded-lg">
                  <div className="w-8 h-8 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mb-2.5 font-bold font-mono text-xs">
                    02
                  </div>
                  <h3 className="text-xs font-bold text-slate-200 mb-1">Idempotency Guard</h3>
                  <p className="text-[11px] text-slate-400 leading-relaxed">
                    Every transactional action submits a unique `idempotency_key` header. Double charges due to network disconnects or browser reloads are completely mitigated.
                  </p>
                </div>

                <div className="p-4 bg-slate-900/40 border border-slate-800/60 rounded-lg">
                  <div className="w-8 h-8 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mb-2.5 font-bold font-mono text-xs">
                    03
                  </div>
                  <h3 className="text-xs font-bold text-slate-200 mb-1">Webhooks Authority</h3>
                  <p className="text-[11px] text-slate-400 leading-relaxed">
                    Client-side confirmation state transitions are treated as warnings. The system state is only set to PAID upon cryptographically verified webhook call events.
                  </p>
                </div>
              </div>
            </div>

            {/* FLOW CHART & GITHUB STEPS */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              {/* FLOW SECTION */}
              <div className="bg-[#080d16] border border-slate-800/80 rounded-xl p-5">
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-4 flex items-center gap-2">
                  <Cpu size={14} className="text-sky-400" />
                  LangGraph + CrewAI + MCP Approved Flow
                </h3>

                <div className="space-y-4 font-sans text-xs">
                  <div className="flex items-start gap-3">
                    <div className="w-5 h-5 rounded bg-emerald-500/10 text-emerald-400 flex items-center justify-center text-[10px] font-bold border border-emerald-500/20 mt-0.5">
                      1
                    </div>
                    <div>
                      <h4 className="font-semibold text-slate-200">POST /reserve/stream</h4>
                      <p className="text-slate-400 text-[11px] mt-0.5">Customer requests Deluxe Suite check-in bounds. Starts server-sent stream.</p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <div className="w-5 h-5 rounded bg-emerald-500/10 text-emerald-400 flex items-center justify-center text-[10px] font-bold border border-emerald-500/20 mt-0.5">
                      2
                    </div>
                    <div>
                      <h4 className="font-semibold text-slate-200">LangGraph Execution Nodes</h4>
                      <p className="text-slate-400 text-[11px] mt-0.5">Nodes sequence executes state validations, room availability checks, and price calculations.</p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <div className="w-5 h-5 rounded bg-emerald-500/10 text-emerald-400 flex items-center justify-center text-[10px] font-bold border border-emerald-500/20 mt-0.5">
                      3
                    </div>
                    <div>
                      <h4 className="font-semibold text-slate-200">CrewAI Agent (ReservationAgent + PaymentAgent)</h4>
                      <p className="text-slate-400 text-[11px] mt-0.5">ReservationAgent compiles parameters. PaymentAgent calls MCP tool server to initiate link.</p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <div className="w-5 h-5 rounded bg-emerald-500/10 text-emerald-400 flex items-center justify-center text-[10px] font-bold border border-emerald-500/20 mt-0.5">
                      4
                    </div>
                    <div>
                      <h4 className="font-semibold text-slate-200">Stripe Webhooks & CONFIRMED State</h4>
                      <p className="text-slate-400 text-[11px] mt-0.5">Customer pays securely. Stripe triggers webhook receiver. State updates to PAID.</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* GIT UPLOAD SECTION */}
              <div className="bg-[#080d16] border border-slate-800/80 rounded-xl p-5">
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <Github size={14} className="text-slate-300" />
                  GitHub Repository Upload Guidelines
                </h3>

                <p className="text-xs text-slate-400 leading-normal mb-3">
                  This Phase 1 directory structure has been fully written to the workspace containers. Run these command parameters to link to your portfolio repository:
                </p>

                <div className="bg-[#05080e] rounded-lg border border-slate-900 p-4 font-mono text-xs text-slate-300 space-y-2">
                  <div><span className="text-slate-500"># 1. Initialize local repository</span></div>
                  <div><span className="text-emerald-400">cd</span> hospitality-reservation-payment-agent</div>
                  <div><span className="text-emerald-400">git init</span></div>
                  
                  <div className="pt-2"><span className="text-slate-500"># 2. Add Phase 1 placeholder schemas & policies</span></div>
                  <div><span className="text-emerald-400">git add .</span></div>
                  <div><span className="text-emerald-400">git commit -m</span> <span className="text-amber-200">"feat: initialize Phase 1 hospitality agent skeleton"</span></div>
                  
                  <div className="pt-2"><span className="text-slate-500"># 3. Bind to portfolio repository</span></div>
                  <div><span className="text-emerald-400">git remote add origin</span> https://github.com/aquilinoFrancisco/hospitality-reservation-payment-agent.git</div>
                  <div><span className="text-emerald-400">git branch -M</span> main</div>
                  <div><span className="text-emerald-400">git push -u origin</span> main</div>
                </div>
              </div>

            </div>

          </div>
        )}

      </main>

      {/* COMPLIANCE FOOTER */}
      <footer className="bg-[#060a10] border-t border-slate-800/60 px-6 py-3.5 flex justify-between items-center text-[11px] text-slate-500 font-mono">
        <span>Portfolio Owner: aquilino.francisco@gmail.com</span>
        <span>AI Studio Platform Build • 2026-07-06</span>
      </footer>

    </div>
  );
}
